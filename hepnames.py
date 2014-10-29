import os
import re
import time

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_record
from invenio.search_engine import get_fieldvalues
from invenio.mailutils import send_email

print 'This script should be run on the mailout machine.\n\n'
time.sleep(10)


date = '2012'
region = 'Europe'
search = '670:/' + date + '/ 043:/' + region + '/ 371__m:/\@/'
search = '371:hoc@fnal.gov'
search = 'fermilab 371__m:/@/ -035:bai'
search = '001:1226850->9999999 371__m:/\@/ -670__d:2014* -670__d:2013* -670__d:2012*'
1284129
search = '001:1284129->9999999 371__m:/\@/ -670__d:2014* -670__d:2013* -670__d:2012*'
search = '001:983937->9999999 371__m:/\@/ 670__d:2012* -670__d:2014* -670__d:2013*'
search = '371__m:/\@/ 670__d:2011* -670__d:2012* -670__d:2014* -670__d:2013* -371__r:senior'
#search = '693__e:bnl-rhic-phenix 371__m:/\@/ -670__d:2014* -670__d:2013*'
search = '001:1005691'

print search
time.sleep(5)
#os._exit(0)

x = perform_request_search(p=search,cc='HepNames')
print len(x)
time.sleep(5)
log = open('hepnames.log','a')
dateTimeStamp = time.strftime('%Y-%m-%d %H:%M:%S')
dateTimeStamp = dateTimeStamp + ' ' + search + ' : ' + str(len(x)) + '\n'
log.write(dateTimeStamp)
log.close()

i = 1

for r in x:
  recid = str(r)
  print i
  print 'recid = ',recid
  author = get_fieldvalues(r,'100__q')[0]
  author2 = get_fieldvalues(r,'100__a')[0]
  
  author2 = author2.replace(' ','+') 
  email = get_fieldvalues(r,'371__m')[0]
  email = email.replace('employ@fnal.gov','jartel@fnal.gov')
  email = email.replace('recruitment.service@cern','Caroline.Dumont@cern')
  #email = 'hoc@fnal.gov'
  print 'author = ',author
  print 'email = ',email
  print ' '

  sender  = '"HEPNames Database Administrator" <authors@inspirehep.net>'
  subject = 'Your entry in INSPIRE HEPNames [' + recid + ']'
  text = "Dear " + author + ",\n\n"
  text = text + "Have you already checked if your publication list and career information are correct and up-to-date in INSPIRE?\n\n"
  text = text + "Your publication lists and citesummary are now automatically generated in INSPIRE.  You can search, confirm or change yours at:\n"
  text = text + "http://inspirehep.net/author/search?q=" + author2 + "\n"
  text = text + "You may proceed in two ways:  as a guest or logging in through our partner site arXiv.org (only do this if you have already claimed papers on arXiv.org).\n\n"
  text = text + "If you have changed jobs recently, finished your PhD or got a promotion, please make sure these changes are communicated to the community by updating your HEPNAMES entry here:\n"
  text = text + "http://inspirehep.net/record/" + recid + "\n"
  text = text + "Please click on the update button to complete the information in your HEPNames profile. \
You might also wish to check that the STUDENTS link works. If it does not \
show everyone, please either update their records or let us know that you \
need to be listed as the person's advisor.\
\n\n\
We hope you will find this a useful and interesting service and your \
improvements will be greatly appreciated.\
\n\n\
If no changes are needed to your HEPNames entry, please just reply to this email with \
\"verified\". That way we will know your record is \
up to date and correct.\
\n\
\n\
\n\
Best Wishes,\n\
\n\
The INSPIRE HEPNames Team\n\
authors@inspirehep.net\n\
\n\
"
  send_email(sender,email,subject,text,header='', footer='')
  i = i + 1


