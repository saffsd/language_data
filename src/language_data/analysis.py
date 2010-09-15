from __future__ import with_statement
from hydra.classifier.tree.ClassTreeClassifier import ClassTreeLearner 

import sys
import pylab
import networkx as nx


def langtree_plot(graph, path):
  pylab.figure(figsize=(30,30))
  
  pos = nx.graphviz_layout(graph, prog='twopi',args='')

  # Draw the actual nodes 
  nx.draw_networkx_edges(graph, pos)

  # Draw little circles where the languages are
  nx.draw_networkx_nodes( graph
                        , pos
                        , node_size = 500
                        , node_color = 'w'
                        , nodelist = graph.languages
                        )
  
  # Mark the families
  nx.draw_networkx_nodes( graph
                        , pos
                        , node_size = 200
                        , node_color = 'w'
                        , nodelist = graph.families 
                        )

  # Mark the root                      
  nx.draw_networkx_nodes( graph
                        , pos
                        , node_size = 800
                        , node_color = 'w'
                        , nodelist = [graph.root] 
                        )
  # Write the labels                      
  fringe_labels = dict( (n,n.label) for n in graph.languages)
  family_labels = dict(    ( n
                           , "%d,%d" % ( len(n.languages)
                                       , len(graph.successors(n))
                                       ) 
                           ) 
                      for  n 
                      in 
                      graph.families
                      )
  labels = {}
  labels.update(family_labels)
  labels.update(fringe_labels)
  nx.draw_networkx_labels(graph, pos, labels)

  pylab.savefig(path)


def main():
  from hydra.classifier import cosine_1nnL, bsvmL, naivebayesL
  from hydra.preprocessor.model.hdf5 import HDF5ModelStore
  from hydra.common.log import getHydraLogger
  from hydra.task.taskset import CrossValidate
  from hydra.experiments import Experiment
  from wikipedia import wikipedia_lang_tree

  logger = getHydraLogger()
  g = wikipedia_lang_tree()
  langtree_plot(g, 'tree.png')
  raise
  #learner = bsvmL()
  learner = cosine_1nnL()
  #learner = naivebayesL()
  model_store = HDF5ModelStore()
  model = model_store.getModel({ 'dataset':'fivek_subonek'
                              ,  'tokenizer':'byte_unigram'
                              })
  treelearner = ClassTreeLearner(g, model.classlabels, learner)

  taskset = CrossValidate(model)
  experiment = Experiment(taskset, treelearner)
  tsr1 = experiment._run()

  experiment = Experiment(taskset, learner)
  tsr2 = experiment._run()

  print tsr1
  print tsr2




if __name__ == '__main__':
  main()
