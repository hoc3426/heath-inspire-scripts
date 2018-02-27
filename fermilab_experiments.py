import os
import re
import time
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
serieses = ['thesis','misc','tm','fn','proposal','workbook','bachelors','masters','design','loi','pbar','nal','annual','upc','ap','en','exp','lu','habil','vlhcpub','mura']
serieses = ['experiments']
serieses.sort()
print 'cd /web/sites/ccd.fnal.gov/htdocs/techpubs'

VERBOSE = False
VERBOSE = True

for series in serieses :
  reports = []
  authorId = False
  search = "119__a:FNAL* or 419__a:FNAL*"
  #search = "find recid 1110234"
  #print search 
  result = perform_request_search(p=search,cc='Experiments')
  for recid in result : 
    reportValues = get_fieldvalues(recid,'119__a')
    reportValues += get_fieldvalues(recid,'419__a')
    author = get_fieldvalues(recid,'702__a')
    authorId = get_fieldvalues(recid,'702__i')
    authorAff = get_fieldvalues(recid,'702__u')
    title = get_fieldvalues(recid,'245__a')
    collaboration = get_fieldvalues(recid,'710__g')
    try:
        end_date = get_fieldvalues(recid,'046__t')[0]
    except: 
        try:
            end_date = get_fieldvalues(recid,'046__c')[0]
        except:
            end_date = ''       
    if VERBOSE: print recid, reportValues, author, authorId, authorAff, title, collaboration, end_date
    if author : 
      author = author[0]    
    else :
      author = ''
    if title : 
      title = '<i>' + title[0][:100] + '</i>'
    else :
      title = ''
    if collaboration :
      collaboration = collaboration[0]
    else :
      collaboration = ''
    if authorAff :
      authorAff = authorAff[0]
    else :
      authorAff = ''
    #print "author = ", author
    #print "title = ",  title
    #print "authorId = ",  authorId
    #print "collaboration = ", collaboration
    if authorId : 
      authorId = authorId[0]
    else:
      authorId = ''
    for report in reportValues :  
      if re.match('FNAL-', report, re.IGNORECASE) \
      or re.match(r'MURA-\d', report, re.IGNORECASE) \
      or re.match(r'MURA-\w\-', report, re.IGNORECASE) \
      or re.match(r'MURA-\w$', report, re.IGNORECASE):
        search_proposal = re.sub(r'FNAL-\w-', r'FERMILAB-PROPOSAL-', report)
        #search_proposal = 'find exp ' + report + ' and r proposal'
        proposal_recid = perform_request_search(p=search_proposal,cc='HEP')
        try:
            proposal_recid = proposal_recid[0]
            proposal_date = get_fieldvalues(proposal_recid,'269__c')[0]
        except:
            proposal_recid = ''
            proposal_date = ''
        sorter = re.sub(r'\D', '', report)
        if re.search('FNAL-T', report):
          title = '<font color="green">' + title + '</font>'
        y = [sorter,report,str(recid),author,title,authorId,collaboration,authorAff,str(proposal_recid),proposal_date,end_date]
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
  output.write('<a href="http://ccd.fnal.gov/techpubs/fermilab_spires.html">Fermilab Technical Publications</a>\n')
  output.write('<h2>Fermilab experiments</h2>')
  output.write('<p>Please send comments, additions or corrections ')
  output.write('to Heath O\'Connell <a href="mailto:hoc@fnal.gov">hoc@fnal.gov</a>.</p>')
  os.environ['TZ'] = 'CEST+5'
  dateTimeStamp = '<i>Updated '+time.strftime('%Y-%m-%d %H:%M:%S')+'</i>\n'
  output.write(dateTimeStamp)
  output.write('<br />\n<table>\n')
  output.write('<tr><td>Number</td><td>Collaboration</td><td>Spokesperson</td><td>Title (test beam in green)</td><td>Proposal</td><td>Finished</td></tr>')
  for report in reports :
    report.pop(0)
    if VERBOSE: print "report =", report
    if report[4]: 
      search2 = '035__a:' + report[4] 
      if VERBOSE: print "search2 =", search2
      result = perform_request_search(p=search2,cc='HepNames')
      if VERBOSE: print report[4], result
      report[2] = '<a href="http://inspirehep.net/record/' + str(result[0]) + '">'+report[2]+'</a>'
    #print report
    line = \
'<tr>\
  <td><a href="http://inspirehep.net/record/'+report[1]+'">'+report[0]+'</a></td>\
  <td>'+report[5]+'</td>\
  <td>'+report[2]+'</td>\
  <td>'+report[3]+'</td>\
  <td><a href="http://inspirehep.net/record/'+report[7]+'">'+report[8]+'</a></td>\
  <td>'+report[9]+'</td> </tr>\n'
    if re.search(r'THESIS', report[0]):
      if report[5]:
        search2 = '119__a:' + report[5]
        result = perform_request_search(p=search2,cc='collaborations')
        if result: result = result[0]
        collaboration = get_fieldvalues(result,'710__g')
        if collaboration: 
          collaboration = collaboration[0]
          collaboration = collaboration.replace(' Collaboration','')
          report[5] = report[5] + ' (' + collaboration + ')'
        if result:
          report[5] = '<a href="http://inspirehep.net/record/' + str(result) + '">'+report[5]+'</a>'
      line = \
'<tr>\
  <td><a href="http://inspirehep.net/record/'+report[1]+'">'+report[0]+'</a></td>\
  <td>'+report[2]+'</td>\
  <td>'+report[5]+'</td>\
  <td>'+report[6]+'</td>\
  <td>'+report[3]+'</td>\
</tr>\n'
    output.write(line)
  output.write('</table>\n')
  output.write('</body>\n')
  output.write('</html>\n')
  output.close()
  print '\\rm fermilab-reports-' + series + '.html' 
  print 'wget http://hoc.web.cern.ch/hoc/' + 'fermilab-reports-' + series + '.html' 

