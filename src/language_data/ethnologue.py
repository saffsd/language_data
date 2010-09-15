from __future__ import with_statement
import csv
import urllib
import os
import re
from iso639 import macrolanguages

class EthnologueDataError(Exception): pass

class Ethnologue(object):
  lang_tree_url = 'http://www.ethnologue.org/show_lang_family.asp?code='
  re_family = re.compile(r"""<A HREF=\"show_family\.asp\?subid=\d+">(?P<name>.*)</A>&nbsp;\((?P<member_count>\d+)\)""")
  re_language = re.compile(r"""\b(?P<name>.*)&nbsp;\[<a href="show_language.asp\?code=(?P<code>\w\w\w)">""")

  def __init__(self, data_path = None):
    self.data_path = 'data' if data_path is None else data_path
    assert(os.path.exists(self.data_path))
    lang_codes_path = os.path.join(self.data_path,'LanguageCodes.tab')
    self.macrolangs = macrolanguages()

  def scrape_ethonologue_for_tree_data(self):
    LanguageCodes = [    row['LangID']
                    for  row 
                    in   csv.DictReader( open(lang_codes_path)
                                       , delimiter='\t'
                                       )
                    ]
    for lang_code in LanguageCodes:
      path = self.prefix_path(lang_code)
      if not os.path.exists(path):
        print "Retrieving", lang_code
        urllib.urlretrieve( self.lang_tree_url + lang_code
                          , path
                          )
  def prefix_path(self, prefix):
    return os.path.join(self.data_path, prefix)
   
  def _lineage(self, file):
    lineage = []
    for line in file:
      # Check if this is a lineage line
      match_obj = self.re_family.search(line)
      if match_obj is not None:
        lineage.append(match_obj.group('name'))
      else:
        # Check if this is the language line
        match_obj = self.re_language.search(line)
        if match_obj is not None:
          return (match_obj.group('code'), match_obj.group('name'), lineage)
    # May need to fail if we get here, did not find the language line
    raise EthnologueDataError

  def lineage(self, lang_code):
    # Establish the longest shared lineage
    if lang_code in self.macrolangs:
      base_lineage = None 
      for mid in self.macrolangs[lang_code]:
        if base_lineage is None:
          base_lineage = self.lineage(mid)
          continue
        new_lineage = self.lineage(mid)
        # Ignore creole in determining lineage
        if new_lineage is None or new_lineage[0] == 'Creole':
          continue
        lineage = []
        for bl, nl in zip(base_lineage, new_lineage):
          if bl == nl:
            lineage.append(bl)
          else:
            break
        base_lineage = lineage
      return base_lineage
    else:
      try:
        with open(self.prefix_path( lang_code )) as ethnologue_page:
          try:
            code, name, lineage = self._lineage(ethnologue_page)
            lineage.append(name)
            return lineage
          except EthnologueDataError,e:
            return None 
      except IOError,e:
        return None

 

from cPickle import dump, load
def store_ethnologue_tree(path):
  etn = Ethnologue()
  etn.scrape_ethonologue_for_tree_data()
  etn.process_ethnologue_data()
  with open(path, 'w') as file:
    dump(etn.lineage_tree, file)

def load_ethnologue_tree(path):
  with open(path) as file:
    tree = load(file)
  return tree

import os
if __name__ == "__main__":
  path = 'etn_tree.pickle'
  if not os.path.exists(path):
    store_ethnologue_tree(path)
  tree = load_ethnologue_tree(path)
  print tree

