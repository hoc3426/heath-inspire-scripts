import os
import re
import time
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
serieses = ['thesis','misc','tm','fn','proposal','workbook','bachelors','masters','design','loi','pbar','nal','annual','upc','ap','en','exp','lu','habil','vlhcpub','mura']
serieses = ['thesis']
serieses.sort()
print 'cd /afs/fnal.gov/files/expwww/bss/html/techpubs'

VERBOSE = False

for series in serieses :
  reports = []
  authorId = False
  search = "find r fermilab-" + series + "-*"
  if series == 'mura': search = "find r " + series + "-*"
  #search = "find recid 1261432"
  #print search 
  result = perform_request_search(p=search,cc='HEP')
  for recid in result : 
    if VERBOSE: print recid
    reportValues = get_fieldvalues(recid,'037__a')
    author = get_fieldvalues(recid,'100__a')
    authorId = get_fieldvalues(recid,'100__i')
    authorAff = get_fieldvalues(recid,'100__u')
    title = get_fieldvalues(recid,'245__a')
    experiment = get_fieldvalues(recid,'693__e')
    
    if author : 
      author = author[0]    
    else :
      author = ''
    if title : 
      title = '<i>' + title[0][:100] + '</i>'
    else :
      title = ''
    if experiment :
      experiment = experiment[0]
    else :
      experiment = ''
    if authorAff :
      authorAff = authorAff[0]
    else :
      authorAff = ''
    #print "author = ", author
    #print "title = ",  title
    #print "authorId = ",  authorId
    #print "experiment = ", experiment
    if authorId : 
      authorId = authorId[0]
    for report in reportValues :  
      if re.match('FERMILAB-' + series, report, re.IGNORECASE) \
      or re.match(r'MURA-\d', report, re.IGNORECASE) \
      or re.match(r'MURA-\w\-', report, re.IGNORECASE) \
      or re.match(r'MURA-\w$', report, re.IGNORECASE):
        y = [report,str(recid),author,title,authorId,experiment,authorAff]
        if VERBOSE: print "y = ", y
        reports.append(y)
  reports.sort(reverse=True)

  file = 'www/fermilab-reports-' + series + '.html' 
  output = open(file,'w')
  output.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n')
  output.write('        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
  output.write('<html xmlns="http://www.w3.org/1999/xhtml">\n')
  output.write('<head>\n')
  output.write('<title>Fermilab Technical Publications: ')
  output.write(series)
  output.write('</title>\n')
  output.write('<meta http-equiv="content-type" content="text/html;charset=utf-8" />\n')
  output.write('</head>\n')
  output.write('<body>\n')
  output.write('<a href="http://bss.fnal.gov/techpubs/fermilab_spires.html">Fermilab Technical Publications</a>\n')
  output.write('<br /><br />')
  os.environ['TZ'] = 'CEST+5'
  dateTimeStamp = '<i>Updated '+time.strftime('%Y-%m-%d %H:%M:%S')+'</i>\n'
  output.write(dateTimeStamp)
  output.write('<br />\n<table>\n')
  for report in reports :
    if VERBOSE: print "report =", report
    if report[4]: 
      #print report
      search2 = '035__a:' + report[4] 
      if VERBOSE: print "search2 =", search2
      result = perform_request_search(p=search2,cc='HepNames')
      if VERBOSE: print report[4], result
      try:
          report[2] = '<a href="http://inspirehep.net/record/' + str(result[0]) + '">'+report[2]+'</a>'
      except IndexError:
          print "Problem with", result, report
    line = '<tr><td><a href="http://inspirehep.net/record/'+report[1]+'">'+report[0]+'</a></td>\
                <td>'+report[2]+'</td><td>'+report[3]+'</td></tr>\n'
    if re.search(r'THESIS', report[0]):
      if report[5]:
        search2 = '119__a:' + report[5]
        result = perform_request_search(p=search2,cc='Experiments')
        if result: result = result[0]
        collaboration = get_fieldvalues(result,'710__g')
        if collaboration: 
          collaboration = collaboration[0]
          collaboration = collaboration.replace(' Collaboration','')
          report[5] = report[5] + ' (' + collaboration + ')'
        if result:
          report[5] = '<a href="http://inspirehep.net/record/' + str(result) + '">'+report[5]+'</a>'
      line = '<tr><td><a href="http://inspirehep.net/record/'+report[1]+'">'+report[0]+'</a></td>\
                <td>'+report[2]+'</td><td>'+report[5]+'</td><td>'+report[6]+'</td><td>'+report[3]+'</td></tr>\n'
    output.write(line)
  output.write('</table>\n')
  output.write('</body>\n')
  output.write('</html>\n')
  output.close()
  print '\\rm fermilab-reports-' + series + '.html' 
  print 'wget http://hoc.web.cern.ch/hoc/' + 'fermilab-reports-' + series + '.html' 

