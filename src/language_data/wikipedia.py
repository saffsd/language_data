import networkx as nx

from ethnologue import Ethnologue
from LanguageTree import LanguageTree 
from iso639 import iso639_map, iso639_2to3, macrolanguages
from hydra.preprocessor.model.hdf5 import HDF5ModelStore
from hydra import configuration
from hydra.common.decorators import shelved
from hydra.classifier.tree.ClassTree import ClassBranch, ClassLeaf, ClassNode
model_path = configuration.getpath('model') 
etn_path = configuration.getpath('ethnologue')

def remove_redundant_families(graph):
  for n in graph.nodes():
    successors = graph.successors(n)
    #print n.label, "has", len(successors), "successors"
    if len(successors) == 1:
      graph.add_edge(graph.predecessors(n)[0], successors[0])
      graph.remove_node(n)
      graph.branches.remove(n)

def group_leaves(g):
  # This transform results in a tree that does not classify 
  # correctly for some reason.
  ClassNode.count = max(n.index for n in g) + 1
  count = 0
  queue = [g.root]
  while queue:
    n = queue.pop()
    leaves = []
    branches = []
    for s in g.successors(n):
      if isinstance(s, ClassLeaf):
        leaves.append(s)
      elif isinstance(s, ClassBranch):
        branches.append(s)
      else:
        raise ValueError, "Unknown node type!"

    if len(leaves) > 1 and len(branches) > 0:
      label = 'leaves'+str(count)
      count += 1
      new_node = ClassBranch(label)
      #g.add_node(new_node)
      for l in leaves:
        g.remove_edge(n,l)
        g.add_edge(new_node,l)
        new_node.leaves.add(l.label)
      g.add_edge(n,new_node)

    queue.extend(branches)
    
    
@shelved('wikipedia_lang_tree')
def wikipedia_lang_tree():
  model = HDF5ModelStore(model_path)

  spaces = model.resolve_space({'type':'class','dataset':'fivek_subonek'})
  wikipedia_ids = getattr(model.spaces, spaces[0]).read()

  etn = Ethnologue(etn_path)
  g = LanguageTree() 

  for id in wikipedia_ids:
    # Upgrade iso639-1 to iso639-3
    full_id = iso639_2to3(id) if len(id) == 2 else id
    if len(full_id) == 3:
      lineage = etn.lineage(full_id)
      if lineage is not None:
        g.add_lineage(id, lineage)
      else:
        g.add_lineage(id, [])

  remove_redundant_families(g)
  g.layout = nx.graphviz_layout(g, prog='dot', args='')
  
  return g

def wlt2():
  g = wikipedia_lang_tree()
  group_leaves(g)
  g.layout = nx.graphviz_layout(g, prog='dot', args='')
  print [n for n in g if len(g.neighbors(n)) == 0 ]
  return g


