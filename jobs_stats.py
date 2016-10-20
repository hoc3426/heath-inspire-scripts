#!/usr/bin/python

from invenio.search_engine import perform_request_search

ranks = ('Student', 'Postdoc', 'Junior', 'Senior', 'Staff')
regions = ('Africa', 'Asia', 'Australasia', 'Europe', 'Middle East', \
               'North America', 'South America')
fields = ('astro-ph','gr-qc','hep-ex','hep-lat','hep-ph','hep-th', \
               'nucl-ex','nucl-th','physics.acc-ph','physics.ins-det')

search = 'dadd:2016-06-01->2016-10-01'
print "{0:16s} {1:5s} {2:5s} {3:5s}".format('search', 'open', 'closed', 'total')

#if False:
#for field in fields:
if True:
  #search = '65017:' + field
  x = perform_request_search(p=search, cc='Jobs')
  y = perform_request_search(p=search, cc='Jobs Hidden')
  total = len(x+y)
  print "{0:20s} {1:5d} {2:5d} {3:5d}".format(search, len(x), len(y), total)

if False:
#for rank in ranks:
  search = '656:' + rank
  x = perform_request_search(p=search, cc='Jobs')
  y = perform_request_search(p=search, cc='Jobs Hidden')
  total = len(x+y)
  print "{0:20s} {1:5d} {2:5d} {3:5d}".format(search, len(x), len(y), total)



if False:
#for year in range(2012, 2017):
  #for month in range(1, 13):
  #  if month < 10:
  #      month = '0' + str(month)
    date = str(year)
  #  date = str(year) + '-' + str(month)
    search = 'dadd:' + date
    search1 = '037__a:jobsubmit-job-' + date + '*'
    x = perform_request_search(p=search, cc='Jobs')
    y = perform_request_search(p=search, cc='Jobs Hidden')              
    x1 = perform_request_search(p=search1, cc='Jobs')
    y1 = perform_request_search(p=search1, cc='Jobs Hidden')
    total = len(x+y)
    total1 = len(x1+y1)
    print "{0:12s} {1:5d} {2:5d} {3:5d} {4:5d} {5:5d} {6:5d}".\
          format(search, len(x1), len(y1), total1, len(x), len(y), total)



if False:
  for r in range(2007, 2015):
    for region in regions:
        #print 'Year', 'region'.ljust(15), 'rank'.ljust(10), 'field'.ljust(15), 'open'.rjust(6), \
        #    'filled'.rjust(6),'total'.rjust(6)
        print 'Year', 'region'.ljust(15), 'rank'.ljust(10), 'open'.rjust(6), \
            'filled'.rjust(6),'total'.rjust(6) 
        for rank in ranks:
            #for field in fields:
                region = region.replace('Australasia','Austral*')
                if r < 2010:
                  rank = rank.replace('Junior','Tenure-track')
                  rank = rank.replace('Senior','Tenured')
                if r < 2012:
                    search = '961__x:' + str(r) + '-* region:"' + region +\
                        '" rank:' + rank #+ ' subject:' + field

                else:
                    search = 'dadd:' + str(r) + ' region:"' + region +\
                        '" rank:' + rank #+ ' subject:' + field
                x = perform_request_search(p=search, cc='Jobs')
                y = perform_request_search(p=search, cc='Jobs Hidden')
                total = len(x+y)
                rank = rank.replace('Tenure-track','Junior')
                rank = rank.replace('Tenured','Senior')
                region = region.replace('Austral*','Australasia')
                #print r, region.ljust(15), rank.ljust(10), field.ljust(15), \
                #str(len(x)).rjust(6), str(len(y)).rjust(6), str(total).rjust(6)
                print r, region.ljust(15), rank.ljust(10), \
                str(len(x)).rjust(6), str(len(y)).rjust(6), str(total).rjust(6)

