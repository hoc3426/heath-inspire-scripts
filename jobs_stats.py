#!/usr/bin/python

from invenio.search_engine import perform_request_search

ranks = ('Student', 'Postdoc', 'Junior', 'Senior', 'Staff')
regions = ('Africa', 'Asia', 'Australasia', 'Europe', 'Middle East', \
               'North America', 'South America')
fields = ('astro-ph','gr-qc','hep-ex','hep-lat','hep-ph','hep-th', \
               'nucl-ex','nucl-th','physics.acc-ph','physics.ins-det')

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

