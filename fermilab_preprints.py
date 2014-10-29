import os
import re
import time
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
serieses = ['PUB','CONF']

reports = []
for series in serieses :
  #print series
  for year in range(1970,2014) :
    #print year
    dd = str(year)
    dd = re.sub(r"19", "", dd)
    dd = re.sub(r"20", "", dd)
    search = "find r fermilab-" + series + "-" + dd + "*"
    #print search
    result = perform_request_search(p=search,cc='HEP')
    for recid in result : 
      reportValues = get_fieldvalues(recid,'037__a')
      author = get_fieldvalues(recid,'100__a')
      title = get_fieldvalues(recid,'245__a')
      if author : 
        author = author[0]
      else :
        author = ''
      if title : 
        title = title[0][:100]
      else :
        title = ''
      for report in reportValues :  
        #print 'report = ' + report
        #print 'FERMILAB-' + series
        if re.match('FERMILAB-' + series, report, re.IGNORECASE) :
          number = re.sub("FERMILAB-" + series + "-","",report)
          y = [year,number,report,str(recid),author,title]
          #print 'y = ' , y
          reports.append(y)
reports.sort(reverse=True)
#print reports

file = 'www/fermilab-reports-preprints.html' 
output = open(file,'w')
output.write('<html>\n')
output.write('<header>\n')
output.write('<title>Fermilab Technical Publications: ')
output.write('preprints')
output.write('</title>\n')
output.write('</header>\n')
output.write('<body>\n')
output.write('<a href="http://bss.fnal.gov/techpubs/fermilab_spires.html">Fermilab Technical Publications</a>\n')
output.write('<br /><br />')
os.environ['TZ'] = 'CEST+5'
dateTimeStamp = '<i>Updated '+time.strftime('%Y-%m-%d %H:%M:%S')+'</i>\n'
output.write(dateTimeStamp)
output.write('<br />\n<table>\n')
for report in reports :
  line = '<tr><td><a href="http://inspirehep.net/record/' + report[3] + '">' + report[2] + '</a></td><td>'+report[4]+'</td><td>'+report[5]+'</td></tr>\n'
  output.write(line)
output.write('</table>\n')
output.write('</body>\n')
output.write('</html>\n')
output.close()
print 'cd /afs/fnal.gov/files/expwww/bss/html/techpubs'
print '\\rm fermilab-reports-preprints.html' 
print 'wget http://hoc.web.cern.ch/hoc/fermilab-reports-preprints.html' 
