import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_record
from invenio.bibformat_engine import format_record

#print_record(811388,ot=['100','520'],format='xm')


author = 'Adamson, Philip'
author = 'Vellidis, Konstantinos' 
author = 'Escobar, Carlos Ourivio'
author = 'Khalid, Farah'
author = 'Lowe, Andrew'
author = 'Vellidis, Konstantinos (Costas)'
author = 'Vellidis'
author = 'Bellettini, Giorgio'
author = 'Damgov, Jordan V.'
author = 'Stoynev, Stoyan'
fileName = re.sub(r'(.*)\,.*',r'\1',author)
fileName = fileName.replace(' ','_')
fileName = 'www/texfiles/' + fileName + '.tex'
print fileName
search = 'find a ' + author 
search = 'find ea C.O.Escobar.1'
search = 'fin a F. Khalid or a f fahim'
search = 'find ea A.Lowe.1'
search = 'find a Vellidis'
search = 'find ea Giorgio.Bellettini.1'
search = 'find ea J.Damgov.1'
search = 'find ea Stoyan.Stoynev.1'

print search

x = perform_request_search(p=search,cc='HEP')
x.sort(reverse=True)
print len(x)
output = open(fileName,'w')
input = open('hep_cv.header', 'r')
header = input.read()
input.close()
author = re.sub(r'(.*)\,(.*)',r'\2 \1',author)
title = 'PUBLICATIONS and CITATIONS\\\\' + author
header = header.replace('TITLE',title)
output.write(header)

def clean(r) :
  #print r
  fr = format_record(r, "hlxu", "fr")
  fr = format_record(r, "hlxu")
  #print fr
  fr = fr[0]
  fr = fr.replace('<br>','\n')
  fr = fr.replace('<pre>','\n')
  fr = fr.replace('<br />','\n')
  fr = fr.replace('</pre>','\n')
  fr = fr.replace('&nbsp;','')
  fr = fr.replace('%``','``')
  return fr


for r in x:
  fr = clean(r)
  output.write(fr)
  search = 'refersto:recid:' + str(r) + ' -author:"' + author + '"'
  print search
  xx = perform_request_search(p=search,cc='HEP')
  if len(xx) > 0 :
    output.write('\\begin{enumerate}\n') 
    for rr in xx:
      frr = clean(rr)
      output.write(frr)
    output.write('\\end{enumerate}\n')    

output.write('\end{enumerate}\n')
output.write('\end{document}\n')
output.close()
web = 'http://hoc.web.cern.ch/hoc/texfiles/' + fileName
web = web.replace('texfiles/www/texfiles','texfiles')
print web



