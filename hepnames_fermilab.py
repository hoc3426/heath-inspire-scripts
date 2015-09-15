from invenio.search_engine import perform_request_search
import unicodedata
import re
import os
#from afftranslator2 import *
from hepnames_fermilab_aff_from_email import *

print '<?xml version="1.0" ?>'
print '<collection>'

my_file = open('tmp.in','r')
d = {}
for i in open('tmp.in','r').readlines() :
  if re.search("=", i) :
    g = re.search(r'\s*(.*) \= (.*)\;', i)
    d[g.group(1)] = g.group(2)
  #if 'AFFILIATION' in d and 'NAME' in d and 'EMAIL' in d :
  if 'NAME' in d and 'EMAIL' in d :
    name = d['NAME']
    email = d['EMAIL'] 
    #aff = d['AFFILIATION'] 
    aff = 'mouse'
    if not re.search(r'High School', aff) and \
       not re.search(r'imsa', email):
      search = "find a " + name
      x = perform_request_search(p=search,cc='HepNames')
      result = len(x)
      if result == 0 :
        #print name
        #bm = bestmatch(aff,'ICN')
        #a = bm[0]
        #aff = a[1]
        niceName = re.sub(r'(.*)\, (.*)',r'\2 \1',name)
        print '<record>'
        print '  <datafield tag="100" ind1=" " ind2=" ">'
        print '    <subfield code="a">' + name + '</subfield>'
        print '    <subfield code="q">' + niceName + '</subfield>'
        print '    <subfield code="g">ACTIVE</subfield>'
        print '  </datafield>'
        print '  </datafield>'
        print '  <datafield tag="371" ind1=" " ind2=" ">'
        print '    <subfield code="m">' + email + '</subfield>'
        aff = aff_from_email(email)
        if aff:
          print '    <subfield code="a">' + aff + '</subfield>'
        print '    <subfield code="z">Current</subfield>'
        print '  </datafield>'
        print '  <datafield tag="650" ind1="1" ind2="7">'
        print '    <subfield code="a">HEP-EX</subfield>'
        print '    <subfield code="2">INSPIRE</subfield>'
        print '  </datafield>'
        print '  <datafield tag="670" ind1=" " ind2=" ">'
        print '    <subfield code="a">Fermilab</subfield>'
        print '  </datafield>'
        print '  <datafield tag="980" ind1=" " ind2=" ">'
        print '    <subfield code="a">HEPNAMES</subfield>'
        print '  </datafield>'
        print '</record>'
    d = {}
print '</collection>'


