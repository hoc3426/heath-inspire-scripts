import re
import collections

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
eprints = ['gr-qc','hep-ex','hep-lat','hep-ph','hep-th','nucl-ex','nucl-th']
eprints = ['gr-qc']
for eprint in eprints :
  print eprint
  search = "find primarch " + eprint + " and tc p and (jy 2012 not jy 2011 not jy 2010 not jy 2009 not jy 2008 not jy 2007)"
  x = perform_request_search(p=search,cc='HEP')
  journals = []
  for r in x :
    v = str(get_fieldvalues(r,'773__p')[0]) + str(get_fieldvalues(r,'773__v')[0])
    v = re.sub(r"\d", "", v)
    journals.append(v)
  journals.sort()
  from Counter import Counter
  counter=Counter(journals)
  print counter



c = Counter(journals)
l = list(set(journals))
for letter in c:
    print '%s : %d' % (letter, c[letter])
