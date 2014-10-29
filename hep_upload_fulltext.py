import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

import urllib2

def checkURL(url):
     x = 0
     #print url
     try:
          req = urllib2.urlopen(url)
         
     except IOError, (errno, strerror):
         print "Error with: ", url
         print "I/O error(%s): %s" % (errno, strerror)
     except ValueError:
         print "Error with: ", url
         print "Could not convert data to an integer."
     except:
         print "Error with: ", url 
         print "Unexpected error:", sys.exc_info()[0]
         raise
#     except urllib2.HTTPError as e:
#          print e.code
         return 0
     s = len(req.read())
     t = req.headers.getsubtype()
     if s > 10000:
       if t == 'pdf' : x = 1
     return x

series = "pub"
series = "thesis"
series = "vlhcpub"
series = "mura"

search = "037:/fermilab-" + series + "/ -8564:/files/ -037:arXiv"
search2 = "8564:fermilab" + series + "f"


#search = "037:/^ssc/ -8564:/files/ -037:arXiv"
search = "037:MURA* -8564:/files/ -037:arXiv -037:MURA-A"
search2 = "8564:fermilabother"

#print search
#search = "find r FERMILAB-CONF-92-210"

#print "<?xml version=\"1.0\" ?>"
#print "<collection>"

x = perform_request_search(p=search,cc='HEP')
x2 = perform_request_search(p=search2,cc='HEP')
#x3 = perform_request_search(p=search3,cc='HEP')
x4 = list(set(x) & set(x2))
x4 = x4[:300]


#print len(x),search
#print len(x2),search2
#print len(x3),search3
#print len(x4)
#print 'x4 = ',x4

for r in x4 :
  #print ' or ', r
  #print 'first r = ',r
  url = ''
  urlf = ''
  t  = get_fieldvalues(r,'245__a')[0]
  c  = get_fieldvalues(r,'999C5h')
  urls = get_fieldvalues(r,'8564_u')
  for url in urls :
    #print r,':',url
    urlStart = "find\_paper\.pl\?" + series
    urlStart = "lss.fnal.gov/archive/other/mura"
    if re.search(urlStart, url, re.IGNORECASE) and not re.search('pdf', url): 
      urlf = url + ".pdf"
    elif re.search(urlStart, url, re.IGNORECASE):
      urlf = url
  reportValues  = get_fieldvalues(r,'037__a')
  for y in reportValues :
    if re.search('FERMILAB-' + series, y, re.IGNORECASE) : report = y
    if re.search(series, y, re.IGNORECASE) : report = y
  report = report.lower()
  ##print report
  #if re.search("-2\d\d\d",report) :
  #  url = 'http://lss.fnal.gov/archive/test-'+series+'/2000/'+report+'.pdf'
  #elif re.search("-1\d\d\d",report) :
  #  url = 'http://lss.fnal.gov/archive/test-'+series+'/1000/'+report+'.pdf'
  #elif re.search("-0\d\d\d",report) :
  #  url = 'http://lss.fnal.gov/archive/test-'+series+'/0000/'+report+'.pdf'
  if urlf :
    #print 'r = ',r
    #print 'urlf = ',urlf
    if checkURL(urlf): 
      searchString = series + "[A-z0-9\-]+"
      #print 'searchString = ', searchString
      matchObj = re.search(searchString, urlf, re.IGNORECASE)
      report = matchObj.group()
      #report = 'fermilab-' + report
      #print report
      #print "t = ", t
      #print "c = ", c
      print '<record>'
      print '  <controlfield tag="001">' + str(r) + '</controlfield>'
      print '  <datafield tag="FFT" ind1=" " ind2=" ">'
      print '    <subfield code="a">' + urlf + '</subfield>'
      print '    <subfield code="f">pdf</subfield>'
      print '    <subfield code="n">' + report + '</subfield>'
      print '    <subfield code="t">INSPIRE-PUBLIC</subfield>'
      print '  </datafield>'
      #print '  <datafield tag="246" ind1=" " ind2=" ">'
      #print '    <subfield code="a">' + t + '</subfield>'
      #print '  </datafield>'
      print '</record>'
    if not checkURL(urlf):
      print r, urlf, 'does not exist'
#print "</collection>"



