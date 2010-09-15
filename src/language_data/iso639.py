# Interface to iso639 data
from __future__ import with_statement
import csv
import re
import os

dataP = os.path.join(os.path.dirname(__file__), 'data')
datafile = os.path.join(dataP, 'iso-639-3_Latin1_20090210.tab')

with open(datafile) as data:
  reader = csv.DictReader(data, delimiter='\t')
  iso639_2 = dict( (x['Id'], x) for x in reader)
  iso639_1 = dict( (x['Part1'], x) for x in iso639_2.values() if x['Part1'] != '')

iso639_1_name_assoc = []
for code in iso639_1:
  iso639_1_name_assoc.append( (code, iso639_1[code]['Ref_Name']) )
  
iso639_2_name_assoc = []
for code in iso639_2:
  iso639_2_name_assoc.append( (code, iso639_2[code]['Ref_Name']) )
  
def __macrolanguages():
  """
  Returns a dict mapping from a macrolanguage code in iso639-3
  to the list of macrolanguages it covers
  """
  macrolanguages_data_path = os.path.join(dataP,'macrolanguages.asp')
  macrolanguage_map = {}
  code_re = re.compile(r"""<a HREF="documentation.asp\?id=(?P<code>\w\w\w)">""")
  with open(macrolanguages_data_path) as data:
    key = None
    values = []
    for line in data:
      code_line = code_re.search(line)
      if line.startswith(r'<tr VALIGN="TOP">'):
        entries = 0
      elif code_line is not None: 
        if entries == 0:
          values.append(code_line.group('code'))
        else:
          new_key = values.pop(-1)
          if key is not None:
            macrolanguage_map[key] = values
          key = new_key
          values = [code_line.group('code')]
        entries += 1
  macrolanguage_map[key] = values
  return macrolanguage_map

macrolanguages = __macrolanguages()

def iso639_1to2(two_code):
  if len(two_code) != 2:
    raise ValueError, "Two character code required"
  try:
    result = iso639_1[two_code]['Id']
  except KeyError:
    raise ValueError, "Unknown code %s"%two_code
  return result 

