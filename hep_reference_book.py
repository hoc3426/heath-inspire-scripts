#!/usr/bin/python

import unicodedata
import re
import os

from invenio.search_engine import print_record
from invenio.search_engine import perform_request_search
from invenio.intbitset import intbitset


books = [
#['Itzykson', 'quantum field theory', '0486445682', '159194'],
['Baxter', 'exactly solved models in statistical mechanics', '0486462714' , '1120339'],
['Carroll', 'spacetime and geometry', '0805387323', '650093'],
['Birrell', 'quantum fields in curved space', '0521278589', '181166'],
['Peskin', 'introduction to quantum field theory', '0201503972', '407703'],
['Halzen', 'quarks and leptons', '0471887412', '205394'],
['Zee', 'quantum field theory in a nutshell', '0691140340', '633051'],
['Zee', 'einstein gravity in a nutshell', '069114558X', '1230427'],
['Quigg', 'gauge theories of the strong', '0805360204', '195708', '1983'],
['Quigg', 'gauge theories of the strong', '0805360204', '195708'],
['Zinn\-Justin', 'quantum field theory and critical phenomena', '0198509235', '290037'],
['Deligne','quantum fields and strings', '0821820125', '508870'],
['Collins','foundations of perturbative qcd','9781107645257','922696'],
['Chandrasekhar','mathematical theory of black holes','9780198503705','224457'],
['H\S+bsch','bestiary for physicists','9789810219277','338506'],
['Streater','pct.*spin and statistics.*and all that','0691070628','290343'],
['Galperin','harmonic superspace*camb','9780511535109','570842'],
['Feynman','photon[\s\-]+hadron interactions', '9780201360745', '85512'],
['W5013','w5013','CERN-W5013','863473']]

books = [['Streater','pct.*spin and statistics.*and all that','0691070628','290343']]
#books = [['Chandrasekhar','mathematical theory of black holes','9780198503705','224457']]
books = [['Birrell', 'quantum fields in curved space', '0521278589', '181166'],
['W5013','w5013','CERN-W5013','863473']]
#books = [['Galperin','harmonic superspace.*camb','9780511535109','570842'],
#['W5013','w5013','CERN-W5013','863473']]
books = [['Feynman','photon[\s\-]+hadron interactions', '9780201360745', '85512']]
for book in books:
    referenceFlag = False
    date = False
    author = book[0]
    title = book[1]
    isbn = book[2]
    isbnTag = "i"
    recid = book[3]
    if len(book) == 5 : date = book[4]
    if re.search(r"\-",isbn): isbnTag = "r"
    fileName =  'tmp___hep_reference_book' + recid + '.out'
    fileName2 = 'tmp__hep_reference_book' + recid + '.out'
    fileName3 = 'tmp_hep_reference_book' + recid + '.out'

    search_author = '999C5:/' + author + '/'
    search_title  = '999C5:/' + title + '/ -refersto:recid:' + recid
    x_author = perform_request_search(p=search_author,cc='HEP')
    x_title = perform_request_search(p=search_title,cc='HEP')
    x = list(intbitset(x_author) & intbitset(x_title))
    x = x[:50]

    output = open(fileName,'w')
    for r in x:
        output.write(print_record(r,ot=['999C5'],format='hm'))
    output.close()
    output2 = open(fileName2,'w')
    for i in open(fileName,'r'):
        i = re.sub(r'\n',r'',i)
        i = re.sub(r'</?pre>','',i)
        i = re.sub(r'<pre style="margin: 1em 0px;">','',i)
        if re.search(author,i):
            j = i.lower()
            #j = re.sub(r',',r' ',j)
            #j = re.sub('[ ]+',r' ',j)
            if re.search(title,j) and not re.search(r'$$[rs]',j):
                referenceFlag = True
                if date:
                    if re.search(date,j):
                       i = i + "$$" + isbnTag + isbn + "$$0" + recid
                else:
                    i = i + "$$" + isbnTag + isbn  + "$$0" + recid
                if not re.search(r'CURATOR',i):
                    i = i + "$$9CURATOR"
        output2.write(i)
        output2.write("\n")
    output2.close()
    conversion = "iconv -c -f utf-8 -t ascii " + fileName2 + " > " + fileName3
    os.system(conversion)
    os.unlink(fileName)
    os.unlink(fileName2)
    if not referenceFlag : os.unlink(fileName3)
