import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
import  xml.dom.minidom

print "<?xml version=\"1.0\" ?>"
print "<collection>"


xmldoc = xml.dom.minidom.parse('aps.xml')
articles = xmldoc.getElementsByTagName('article')
counter = 1
for article in articles :
  metadata = article.attributes.keys()
  for element in metadata :
    x = article.attributes[element]
    if x.name == 'published' : date = x.value
    if x.name == 'doi' : doi = x.value
    if x.name == 'preprint_id' : eprint = x.value
    if x.name == 'published' : date = x.value
  search = "find eprint " + eprint + " not doi " + doi
  if counter < 51 :
    x = perform_request_search(p=search,cc='HEP')
    if len(x) == 1 :
      eprint = 'oai:arXiv.org:' + eprint
      eprint = re.sub(r'oai:arXiv.org:arXiv',r'oai:arXiv.org',eprint)
      [publisher,jvp] = re.split('/',doi)
      [journal,volume,page] = re.split('\.',jvp)      
      if journal == 'PhysRevSTAB' : journal = 'Phys.Rev.ST Accel.Beams'
      else : 
        matchObj = re.search("[A-EX]$", journal) 
        if matchObj : 
          volume =  matchObj.group() + volume
          journal = re.sub(r'[A-EX]$',r'',journal) 
        journal = journal + "."
        journal = re.sub(r'([a-z])([A-Z])',r'\1.\2',journal)
      matchObj = re.search("\d\d\d\d", date)
      year = matchObj.group()
      print '<record>'
      print '  <datafield tag="035" ind1=" " ind2=" ">'
      print '    <subfield code="a">' + eprint + '</subfield>'
      print '    <subfield code="9">arXiv</subfield>'
      print '  </datafield>'
      print '  <datafield tag="024" ind1="7" ind2=" ">'
      print '    <subfield code="2">DOI</subfield>'
      print '    <subfield code="a">' + doi + '</subfield>'
      print '  </datafield>'
      print '  <datafield tag="773" ind1=" " ind2=" ">'
      print '    <subfield code="p">' + journal + '</subfield>'
      print '    <subfield code="v">' + volume + '</subfield>'
      print '    <subfield code="c">' + page + '</subfield>'
      print '    <subfield code="y">' + year + '</subfield>'
      print '  </datafield>'
      print '  <datafield tag="260" ind1=" " ind2=" ">'
      print '    <subfield code="c">' + date + '</subfield>'
      print '  </datafield>'
      print '  <datafield tag="980" ind1=" " ind2=" ">'
      print '    <subfield code="a">Published</subfield>'
      print '  </datafield>'
      print '</record>'    
      counter += 1
print "</collection>"

