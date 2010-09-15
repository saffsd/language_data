from hydra.classifier.tree.ClassTree import ClassTree, ClassBranch, ClassLeaf

class LanguageTree(ClassTree):
  def __init__(self):
    ClassTree.__init__(self)
    self.lineages = {}

  def add_lineage(self, language, lineage):
    self.root.leaves.add(language)
    nlist = [ self.root ]

    for i, label in enumerate(lineage):
      node_lineage = '_'.join(lineage[:i+1])
      if node_lineage in self.lineages:
        family = self.lineages[node_lineage]
      else:
        family = ClassBranch(label)
        self.lineages[node_lineage] = family
        self.branches.add(family)
      family.leaves.add( language )
      nlist.append( family )

    new_language = ClassLeaf(language)
    self.leaves.add(new_language)
    nlist.append(new_language)

    self.add_path(nlist)


