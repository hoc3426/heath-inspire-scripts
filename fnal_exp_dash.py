import bitly
import re
import time
import os
from invenio.search_engine import perform_request_search

bitly_key = 'R_4165e9efdb444469a6dd475b52f16b87'
bitly_account = 'hoc3426'
api = bitly.Api(login = bitly_account, apikey = bitly_key)


category = {'a' : ['1. Cosmic Frontier',50,'exp fnal-e-0990 or fnal-t-0969 or fnal-e-0987 or auger or cdms or fnal-e-0961 or fnal-e-1000 or lsst or sdss or snap or des'],
            'b' : ['2a. Energy Frontier (TeV)',50,'exp fnal-e-0823 or fnal-e-0830'],
            'c' : ['2b. Energy Frontier (CMS)',50,'exp cern-lhc-cms'],
            'd' : ['3. Intensity Frontier',50,'exp fnal-e-0831 or fnal-e-0875 or fnal-e-0898 or fnal-e-0906 or fnal-e-0929 or fnal-e-0938 or fnal-e-0954 or fnal-e-0973 or fnal-e-0974 or fnal-e-0989 or fnal-t-0962 or lbne'],
            'e' : ['4. Theory',50,'r fermilab pub and tc p not tc c not tc r and (r ae and fc p or r t or r a)'],
            'f' : ['5a. Science and Technology (S&T) conference',10,'Major accelerator conferences from http://www.jacow.org/index.php?n=Main.Proceedings'],
            'g' : ['5b. Science and Technology (S&T) published', 10,'Papers from a section of journals']}

yearStart = 2007
yearEnd = 2016

os.environ['TZ'] = 'CEST+5'
dateTimeStamp = time.strftime('%Y-%m-%d %H:%M:%S')

dateStamp = time.strftime('%Y-%m-%d')

total_result = {}
total_result_top = {}
file = 'www/fnal_exp_dash.html'
fileDate = file + '.' + dateStamp
output = open(file,'w')
output.write('<i>Updated '+ dateTimeStamp + '</i>\n')
output.write('<table border=\"1\">\n')
output.write('  <tr><td></td><td></td>\n')
for jy in range(yearStart,yearEnd) :
  output.write('  <td colspan="2" align="center">' + str(jy) + '</td>\n')
output.write('  </tr>\n')
output.write('  <tr><td> Category </td><td> Highly cited threshold </td>\n')
for jy in range(yearStart,yearEnd) :
  output.write('  <td> Total </td><td> Highly<br/>cited </td>\n')
output.write('  </tr>\n')

for key in sorted(category.iterkeys()) : 
  topcite = category[key][1]
  output.write('  <tr>\n')
  output.write('    <td>' + category[key][0] + '</td>\n')
  output.write('    <td align="center">' + str(topcite) + '</td>\n')
  topcite = str(topcite)+'+' 
  for jy in range(yearStart,yearEnd) :
    jy1 = jy - 1
    jy2 = jy - 2
    jy3 = jy - 3
    jy4 = jy - 4
    jy5 = jy - 5  
    jyFull = str(jy)+' not '+str(jy1)+' not '+str(jy2)+' not '+str(jy3)+' not '+str(jy4)+' not '+str(jy5)
    search = category[key][2] + ' and tc p not tc c not tc r not fc i and jy ' + jyFull
    if (key == "f") :
      if   (jy == 2007) : search = "cnum C07-01-29 or C07-06-25 or C07-08-06 or C07-08-26.2 or C07-08-27.7 or C07-09-10.10 or C07-10-14.1 "
      elif (jy == 2008) : search = "cnum C08-02-11.3 or C08-05-04 or C08-06-23.3 or C08-06-30 or C08-07-27.1 or C08-08-24.2 or C08-09-28 or C08-09-29.2 "
      elif (jy == 2009) : search = "cnum C09-05-04 or C09-07-20 or C09-08-23.1 or C09-08-31.7 or C09-08-31.8 or C09-09-20.2 or C09-10-18.1 "
      elif (jy == 2010) : search = "cnum C10-05-02 or C10-05-23 or C10-06-13.1 or C10-08-23.7 or C10-09-12 or C10-09-13.7 or C10-09-27.6 or C10-10-20 "
      elif (jy == 2011) : search = "cnum C11-03-28 or C11-07-25.4 or C11-08-01.6 or C11-08-22.5 or C11-09-04 or C11-09-12.1 or C11-09-12.5 "
      elif (jy == 2012) : search = "cnum C12-04-15.1 or C12-05-20.1 or C12-06-10.1 or C12-07-23.4 or C12-08-19.2 or C12-09-09 or C12-09-10.2 or C12-09-24.1 or C12-09-30 "
      elif (jy == 2013) : search = "cnum C13-05-12 or C13-06-10.4 or C13-08-26.1 or C13-09-09.6 or C13-09-16.7 or C13-09-23.1 or C13-09-29 or C13-10-06"
      elif (jy == 2014) : search = "cnum C14-08-24.1 or C14-08-31 or C14-09-14 or C14-10-06 or C14-10-14" 
    elif (key == "g") :
      j  = "j nuima or itase or jinst or ietna or 00699 or JGCOA or cphcb or prsta "
      j2 = "rsina or appla or pramc or nutyb ";
      j3 = "prlta or j mplae or j arnua not r e not r t not r a not r ppd not r ae ";
      search = j + " or " + j2 + " or " + j3 + " and jy " + jyFull
      search = search + " and (r apc or r ad) and tc p and r fermilab" 
    elif (key == "acceleratorP") :
        j  = "nuima or itase or jinst or ietna or 00699 or JGCOA or cphcb or prsta "
        j2 = "rsina or appla or pramc or nutyb ";
        j3 = "(j prlta or j mplae or j arnua not r e not r t not r a not r ppd not r ae) ";
        searchBase = "and (j prsta or r ad or r apc not r ae) and tc p not tc c and jy " + jyFull + " and r fermilab*";
        search  = "j " + j + searchBase
        search2 = "j " + j2 + searchBase
        search3 = j3 + searchBase
        searchTotal = "j " + j + " or + " + j2 + " or " + j3 + searchBase
    elif (key == "computing") :
        search = "r fermilab pub cd not fc a not fc x not fc p not fc e not fc i not fc b and tc p not tc c not tc r and jy " + jyFull
    elif (key == "detector") :
        search = "r fermilab pub and (j nuima or itase or jinst or ietna or rsina) not fc b and tc p not tc c not tc r and jy " + jyFull
    elif (key == "cern-lhc-cms") :
        search = search.replace('cern-lhc-cms','cern-lhc-cms and r fermilab pub not r cern-cms-note* not r cern-lhcc*')
    search = "find " + search
    if re.search('fermilab',search) == None : search = search + ' and r fermilab'
    searchTop = search + ' and topcite '  + str(topcite)
    search = search.replace('  ',' ')
    x = perform_request_search(p=search,cc="HEP")
    total_result[(jy,key)] = x
    x = str(len(x))    
    searchTop = searchTop.replace('  ',' ')
    y = perform_request_search(p=searchTop,cc="HEP")
    total_result_top[(jy,key)] = y
    y = str(len(y))
    link = search.replace(' ','+')
    link = 'http://inspirehep.net/search?p=' + link + '&rg=100'
    link = api.shorten(link)
    linkTop = searchTop.replace('+','%2B')
    linkTop = linkTop.replace(' ','+')
    linkTop = 'http://inspirehep.net/search?p=' + linkTop + '&rg=100'
    linkTop = api.shorten(linkTop)
    #line = '    <td align="center"> <a href=\"http://inspirehep.net/search?p=' + link + '&rg=100\"><b>' + x + '</b></a> </td>' 
    line = '    <td align="center"> <a href=\"' + link + '\"><b>' + x + '</b></a> </td>'
    if (key == "f") :
        confs = search
        confs = re.sub(r' and r fermilab', r'', confs)
        confs = re.sub(r'cnum ', r'111__g:', confs)
        confs = re.sub(r'find ', r'', confs)
        confs_number = confs.count('or ')
        confs_number += 1 
        confs = re.sub(r'or ', r'or 111__g:', confs)
        confs = confs.replace(' ','+')
        confs_link = 'http://inspirehep.net/search?cc=Conferences&sf=year&so=d&p=' + confs
        confs_link = api.shorten(confs_link)
        confs_link = '</a> [<a href=\"' + confs_link  + '">' + str(confs_number) + ' C</a>]'
        line = re.sub(r'</a>', confs_link, line)
    #line = line + '<td align="center"> <a href=\"http://inspirehep.net/search?p=' + linkTop + '&rg=100\"><i>' + y + '</i></a> '
    line = line + '<td align="center"> <a href=\"' + linkTop + '\"><i>' + y + '</i></a> '
    line = line + '</td>'
    output.write(line)
  #output.write('    <td>',expts[key][1],'</td>'
  output.write('  </tr>\n')
  output.write('  <tr>\n')
output.write('    <td align="center">Total </td> <td align="center"> </td>\n')
for jy in range(yearStart,yearEnd) :
  x = []
  y = []
  for key in sorted(category.iterkeys()) :
    x.extend(total_result[(jy,key)])
    y.extend(total_result_top[(jy,key)])
  x = list(set(x))
  y = set(y)
  x = str(len(x))
  y = str(len(y))
  line = '<td align="center"><b>' +  x + '</b></td> <td align="center"><i>' +  y + '</i></td> '
  output.write(line)
output.write('  </tr>\n')
output.write('</table>\n')
output.write('<p></p><p></p><p></p>\n')
         
output.write('<table>\n')
for key in sorted(category.iterkeys()) :
  output.write('<tr><td> ' + category[key][0] + ' </td><td> ' + category[key][2] + ' </td></tr>\n')
output.write('</table>\n')

category = ['1. Experiments at Fermilab','2. Theory','3. Facilities at Fermilab','4. Experiments elsewhere',
            '5. Science and Technology (S&T)','6. Other Fermilab experiments']

frontier = {'i' : 'Intensity Frontier', 'c' : 'Cosmic Frontier', 'e' : 'Energy Frontier',
            'acc' : 'Accelerator S&T' , 'com' : 'Computing S&T', 'det' : 'Detector S&T'}

expts = {
          'fnal-e-0875':['MINOS',    'Ongoing',frontier['i'],category[0]],
          'fnal-e-0938':['MINERvA',  'Ongoing',frontier['i'],category[0]],
          'fnal-e-0898':['MiniBooNE','Ongoing',frontier['i'],category[0]],
          'fnal-e-0906':['SeaQuest', 'Commissioning',frontier['i'],category[0]],
          'fnal-e-0830':['CDF',      'Analysis',frontier['e'],category[0]],
          'fnal-e-0823':['D0',       'Analysis',frontier['e'],category[0]],
         'fnal-e-0823-and-fnal-e-0830':['Tevatron (CDF + D0)','Analysis',frontier['e'],category[0]],
          'fnal-e-0929':['NOvA',     'Construction',frontier['i'],category[0]],
          'fnal-e-0974':['MicroBooNE','Construction',frontier['i'],category[0]],
          'fnal-e-0990':['Holometer','Construction',frontier['c'],category[0]],
          'fnal-t-0969':['GammeV',   'Completed',frontier['c'],category[0]],
          'LBNE'       :['LBNE',     'R&D',frontier['i'],category[0]],
          'fnal-e-0989':['Muon g-2', 'R&D',frontier['i'],category[0]],
          'fnal-e-0973':['mu2e',     'R&D',frontier['i'],category[0]],
          'fnal-e-0987':['DAMIC',    'Running',frontier['c'],category[0]],
          'fnal-t-0962':['ArgoNeuT', 'Analysis',frontier['i'],category[0]],
          'fnal-e-0954':['SciBooNE', 'Analysis',frontier['i'],category[0]],
          'fnal-e-0886':['A0 Photoinjector','Running','',category[2]],
          'fnal-e-0831':['FOCUS',    'Analysis',frontier['i'],category[0]],
          'cern-lhc-cms':['CMS',     'Ongoing',frontier['e'],category[3]],
          #'cern-lhc-atlas':['ATLAS',     'Ongoing',frontier['e'],category[3]],
          'mice'       :['MICE',     'Ongoing',frontier['i'],category[3]],
          'cdms'       :['CDMS',     'Ongoing',frontier['c'],category[3]],
          'fnal-e-0961':['COUPP',    'Running',frontier['c'],category[3]],
          'auger'      :['AUGER',    'Ongoing',frontier['c'],category[3]],
          'snap'       :['SNAP',     'Completed',frontier['c'],category[3]],
          'des'        :['DES',      'Construction',frontier['c'],category[3]],
          'sdss'       :['SDSS',     'Analysis',frontier['c'],category[3]],
          'fnal-e-1000':['DarkSide', 'R&D',frontier['c'],category[3]],
          'lsst'       :['LSST',     'R&D',frontier['c'],category[3]],
          'theory'     :['Particle and Particle-Astro','N/A','',category[1]],
          'theory-p'   :['Particle Theory','N/A','',category[1]],
          'theory-a'   :['Astro Theory','N/A','',category[1]],
          'lattice'    :['Lattice QCD','Running','',category[2]],
          #'accelerator' :['All','',frontier['acc'],category[4]],
          'acceleratorJ':['Conference papers only','',frontier['acc'],category[4]],
          'acceleratorP':['Refereed papers only','',frontier['acc'],category[4]],
          #'technology' :['All','','Other Technology',category[4]],
          'computing' :['Refereed papers only','',frontier['com'],category[4]],
          'detector':['Refereed papers only','',frontier['det'],category[4]],
          'fnal-e-0866':['NuSea','','',category[5]],
          'fnal-e-0815':['NuTeV','','',category[5]],
          'fnal-e-0872':['DONuT','','',category[5]],
          'fnal-e-0781':['SELEX','','',category[5]],
          'fnal-e-0832':['KTeV','','',category[5]],
          'fnal-e-0907':['MIPP','','',category[5]],
          'fnal-e-0871':['HyperCP','','',category[5]]
        }

output.write('<p></p><p></p><p></p>\n')


output.write('<table>\n')
for key in sorted(expts.iterkeys()) :
  output.write('<tr><td> ' + key + ' </td><td> ' + expts[key][0] + ' </td><td> ' + expts[key][1] + ' </td><td> ' + expts[key][2] + ' </td><td> ' + expts[key][3] + ' </td></tr>\n')
output.write('</table>\n')
output.close()
cp = 'cp ' + file + ' ' + fileDate
print cp
print 'http://hoc.web.cern.ch/hoc/fnal_exp_dash.html'
