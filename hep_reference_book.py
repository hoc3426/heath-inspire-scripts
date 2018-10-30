#!/usr/bin/python

import unicodedata
import re
import os

from invenio.intbitset import intbitset
from invenio.search_engine import print_record
from invenio.search_engine import perform_request_search
from invenio.textmarc2xmlmarc import encode_for_xml


DATAS = [
['asqtad', '64192f21b781m0028m014', '10.15484/milc.asqtad.en24a/1177873', '1364957'],
['asqtad', '4096f21b708m0031m031b', '10.15484/milc.asqtad.en13b/1178093', '1399427'],
['asqtad', '2864f21b676m010m050', '10.15484/milc.asqtad.en08a/1178162', '1399428'],
['asqtad', '56144f21b7465m0025m018', '10.15484/milc.asqtad.en19a/1178035', '1399429'],
['asqtad', '4096f21b708m0031m031a', '10.15484/milc.asqtad.en13a/1178092', '1399430'],
['asqtad', '2064f21b676m010m050b', '10.15484/milc.asqtad.en06b/1178159', '1399431'],
['asqtad', '64144f21b746m0036m0108', '10.15484/milc.asqtad.en21a/1178038', '1399432'],
['asqtad', '48144f21b748m0072m018b', '10.15484/milc.asqtad.en23b/1178041', '1399433'],
['asqtad', '1648f21b6586m0194m0484', '10.15484/milc.asqtad.en01a/1178169', '1399434'],
['asqtad', '2896f21b710m0093m031', '10.15484/milc.asqtad.en16a/1178098', '1399435'],
['asqtad', '2064f21b678m010m050', '10.15484/milc.asqtad.en07a/1178160', '1399436'],
['asqtad', '2064f21b681m030m050', '10.15484/milc.asqtad.en10a/1178165', '1399437'],
['asqtad', '2464f21b676m005m050', '10.15484/milc.asqtad.en04a/1178155', '1399438'],
['asqtad', '1648f21b6572m0097m0484', '10.15484/milc.asqtad.en00a/1178168', '1399439'],
['asqtad', '2064f21b676m007m050', '10.15484/milc.asqtad.en05a/1178156', '1399440'],
['asqtad', '2064f21b679m020m050b', '10.15484/milc.asqtad.en09b/1178164', '1399441'],
['asqtad', '2896f21b711m0124m031', '10.15484/milc.asqtad.en17a/1178099', '1399442'],
['asqtad', '2896f21b709m0062m031', '10.15484/milc.asqtad.en15a/1178095', '1399443'],
['asqtad', '48144f21b747m0036m018b', '10.15484/milc.asqtad.en20b/1178037', '1399444'],
['asqtad', '2896f21b709m0062m031b', '10.15484/milc.asqtad.en15b/1178096', '1399445'],
['asqtad', '48144f21b747m0036m018a', '10.15484/milc.asqtad.en20a/1178036', '1399446'],
['asqtad', '1648f21b6628m0484m0484', '10.15484/milc.asqtad.en03a/1178171', '1399447'],
['asqtad', '64144f21b746m0018m018a', '10.15484/milc.asqtad.en18a/1178033', '1399448'],
['asqtad', '2064f21b678m010m050b', '10.15484/milc.asqtad.en07b/1178161', '1399449'],
['asqtad', '3296f21b7085m00465m031', '10.15484/milc.asqtad.en14a/1178094', '1399450'],
['asqtad', '2064f21b679m020m050', '10.15484/milc.asqtad.en09a/1178163', '1399451'],
['asqtad', '48144f21b748m0072m018a', '10.15484/milc.asqtad.en23a/1178040', '1399452'],
['asqtad', '2896f21b709m0062m031c', '10.15484/milc.asqtad.en15c/1178097', '1399453'],
['asqtad', '64144f21b746m0018m018b', '10.15484/milc.asqtad.en18b/1178034', '1399454'],
['asqtad', '1648f21b6600m0290m0484', '10.15484/milc.asqtad.en02a/1178170', '1399455'],
['asqtad', '2064f21b683m040m050', '10.15484/milc.asqtad.en11a/1178166', '1399456'],
['asqtad', '6496f21b7075m00155m031', '10.15484/milc.asqtad.en12a/1178091', '1399457'],
['asqtad', '48144f21b7475m0054m018a', '10.15484/milc.asqtad.en22a/1178039', '1399458'],
['asqtad', '2064f21b676m010m050', '10.15484/milc.asqtad.en06a/1178158', '1399459'],
['asqtad', '2064f21b676m007m050b', '10.15484/milc.asqtad.en05b/1178157', '1399460']]

BOOKS = [
#['Itzykson', 'quantum field theory', '0486445682', '159194'],
['Baxter', 'exactly solved models in statistical mechanics', '0486462714' , 
'1120339'],
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

BOOKS = [['Streater','pct.*spin and statistics.*and all that','0691070628','290343']]
#BOOKS = [['Chandrasekhar','mathematical theory of black holes','9780198503705','224457']]
BOOKS = [['Birrell', 'quantum fields in curved space', '0521278589', '181166'],
['W5013','w5013','CERN-W5013','863473'],
['Baxter', 'exactly solved models in statistical mechanics', '0486462714' ,
'1120339']]
#BOOKS = [['Galperin','harmonic superspace.*camb','9780511535109','570842'],
#['W5013','w5013','CERN-W5013','863473']]
#BOOKS = [['Feynman','photon[\s\-]+hadron interactions', '9780201360745', '85512']]
BOOKS = [['Baxter', 
'exactly solved models in statistical mechanics', '0486462714' ,
'1120339']]
#BOOKS = [['Anderson','The Problem of time','9783319588469','1625434','2017']]

for book in BOOKS:
    reference_flag = False
    date = None
    counter = 0
    author = book[0]
    title = book[1].lower()
    isbn = book[2]
    isbnTag = "i"
    recid = book[3]
    if len(book) == 5 : date = book[4]
    if re.search(r"\-",isbn): isbnTag = "r"

    search_author = '999C5:/' + author + '/'
    search_title  = '999C5:/' + title + '/ -refersto:recid:' + recid
    x_author = perform_request_search(p=search_author,cc='HEP')
    x_title = perform_request_search(p=search_title,cc='HEP')
    result = list(intbitset(x_author) & intbitset(x_title))

    records = []
    new_records = []
    for recid in result:
        records.append(print_record(recid, ot=['999C5'], format='hm'))
    #lines = [record.split('\n') for record in records]]
    for record in records:
      if counter > 50:
          continue
      new_record = []
      reference_flag = False
      for i in record.split('\n'):
        i = re.sub(r'\n',r'',i)
        i = re.sub(r'</?pre>','',i)
        i = re.sub(r'<pre style="margin: 1em 0px;">','',i)
        if re.search(author,i):
            j = i.lower()
            #j = re.sub(r',',r' ',j)
            #j = re.sub('[ ]+',r' ',j)
            if re.search(title, j) and not re.search(r'$$0', j):
                if date:
                    if re.search(date,j):
                       i = i + "$$" + isbnTag + isbn + "$$0" + str(recid)
                       reference_flag = True
                else:
                    i = i + "$$" + isbnTag + isbn  + "$$0" + str(recid)
                    reference_flag = True
                if not re.search(r'CURATOR',i):
                    i = i + "$$9CURATOR"
                if reference_flag:
                    counter += 1
        new_record.append(i)
      if reference_flag:
        new_records.append(new_record)
for record in new_records:
    for line in record:
        print line

