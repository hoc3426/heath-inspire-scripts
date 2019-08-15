#!/usr/bin/python

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_collection_reclist
from invenio.intbitset import intbitset

ranks = ('Student', 'Postdoc', 'Junior', 'Senior', 'Staff')
regions = ('Africa', 'Asia', 'Australasia', 'Europe', 'Middle East', \
               'North America', 'South America')
fields = ('astro-ph','gr-qc','hep-ex','hep-lat','hep-ph','hep-th', \
               'nucl-ex','nucl-th','physics.acc-ph','physics.ins-det')
ANY = \
'"programming language" or "computer programming" or "computing language".\
" or software'
ANY = ''
LANGUAGES = ['perl', 'python', 'c++', 'fortran', 'java',
             ANY]

def job_languages():
    grand_total = 0
    print "{0:>5s} {1:>8s} {2:>8s} {3:>8s} {4:>8s} {5:>8s} {6:>8s}".\
          format('Year', 'Perl', 'Python', 'C++', 'Fortran', 'Java', 'any')

    for year in range(2003, 2020):
        total = {}
        for language in LANGUAGES:
            search = language + ' ' + 'dadd:' + str(year)
            #print search
            x = perform_request_search(p=search, cc='Jobs')
            y = perform_request_search(p=search, cc='Jobs Hidden')
            total[language] = len(x+y)
        print "{0:>5d} {1:8d} {2:8d} {3:8d} {4:8d} {5:8d} {6:8d}".format(year,
            total['perl'], total['python'], total['c++'],
            total['fortran'], total['java'], total[ANY])
job_languages()
quit()

def job_stats():
    grand_total = 0
    print "{0:16s} {1:5s} {2:5s} {3:5s}".format('search', 'open', 
                                                'closed', 'total')
    for month in range(4, 7):
        if month < 10:
            month = '0' +  str(month)
        search = 'dadd:2019-' + str(month)
        x = perform_request_search(p=search, cc='Jobs')
        y = perform_request_search(p=search, cc='Jobs Hidden')
        total = len(x+y)
        grand_total += total
        print "{0:20s} {1:5d} {2:5d} {3:5d} {4:5d}".format(search,
            len(x), len(y), total, grand_total)
 

def eprints():
    total = 0
    fermilab = get_collection_reclist('Fermilab')
    print '{0:4s} {1:3s} {2:3s} {3:3s}'.format('Date', 'All', 'FNA',
                                                   '%')
    date_range = ['1904', '1905', '1906']
    #date_range = range(1, 20)
    for yymm in date_range:
        yymm = str(yymm)
        if len(yymm) == 1:
            yymm = '0' + yymm
        search_f = '037__a:fermilab* 037__c:physics.acc-ph 037__a:"arXiv:' + \
                   yymm + '*"'
        search = '037__c:physics.acc-ph 037__a:"arXiv:' + yymm + '*"'
        x = perform_request_search(p=search, cc='HEP')
        search = '037__c:acc-phys 037__a:"acc-phys/' + yymm + '*"'
        y = perform_request_search(p=search, cc='HEP')
        x_f = intbitset(x) & fermilab
        y_f = intbitset(y) & fermilab
        length = len(x) + len(y)
        length_f = len(x_f) + len(y_f)
        try:
            ratio = float(length_f)/float(length)*100.0
        except ZeroDivisionError:
            ratio = 0
        print '{0:4s} {1:3d} {2:3d} {3:3f}'.format(yymm, length, length_f, 
                                                   ratio)
        total += length
    print "Total =", total

eprints()
#job_stats()
quit()


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

