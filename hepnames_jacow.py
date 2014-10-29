from invenio.search_engine import perform_request_search
import unicodedata
import re
import os
from afftranslator2 import *

print '<?xml version="1.0" ?>'
print '<collection>'

#author$$eemail$$jJACoW-00000357$$uHZB, Berlin, Ge


my_file = open('tmp.in','r')
d = {}
[name,email,id,aff] = ['','','',''] 
for i in open('tmp.in','r').readlines() :
  if re.search("\$\$", i) : 
    g = re.search(r'(.*)\$\$e(.*)\$\$j(.*)\$\$u(.*)', i) 
    name = g.group(1)
    email = g.group(2)
    id = g.group(3)
    aff = g.group(4)
  elif re.search("=", i) :
    g = re.search(r'\s*(.*) \= (.*)\;', i)
    d[g.group(1)] = g.group(2)
    name = d['NAME']
    email = d['EMAIL']
    aff = d['AFFILIATION']
  if name and email and aff :
    if not re.search(r'High School', aff) :
      search = "find a " + name
      search = "find email " + email
      search = "371:" + email + " or 595:" + email + " not 035:" + id
      #print search
      x = perform_request_search(p=search,cc='HepNames')
      result = len(x)
      if result == 1 :
        for r in x:
          print '<record>'
          print '  <controlfield tag="001">'+str(r)+'</controlfield>'
          print '  <datafield tag="035" ind1=" " ind2=" ">'
          print '    <subfield code="9">JACOW</subfield>'
          print '    <subfield code="a">' + id + '</subfield>'
          print '  </datafield>'
          print '</record>'          
      #if result == 0 :
      if 0 :
        bm = bestmatch(aff,'ICN')
        a = bm[0]
        aff = a[1]
        niceName = re.sub(r'(.*)\, (.*)',r'\2 \1',name)
        print '<record>'
        print '  <datafield tag="100" ind1=" " ind2=" ">'
        print '    <subfield code="a">' + name + '</subfield>'
        print '    <subfield code="q">' + niceName + '</subfield>'
        print '    <subfield code="g">ACTIVE</subfield>'
        print '  </datafield>'
        print '  <datafield tag="035" ind1=" " ind2=" ">'
        print '    <subfield code="9">JACOW</subfield>'
        print '    <subfield code="a">' + id + '</subfield>'
        print '  </datafield>'
        print '  <datafield tag="371" ind1=" " ind2=" ">'
        print '    <subfield code="a">' + aff + '</subfield>'
        print '    <subfield code="z">Current</subfield>'
        #print '  </datafield>'
        #print '  <datafield tag="371" ind1=" " ind2=" ">'
        print '    <subfield code="m">' + email + '</subfield>'
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
    [name,email,id,aff] = ['','','','']
print '</collection>'
