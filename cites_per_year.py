'''
A script to find citations per year for an entity.
'''

import getopt
import sys

from invenio.bibrank_citation_searcher import get_cited_by_list
from invenio.intbitset import intbitset
from invenio.search_engine import perform_request_search

def set_defaults():
    '''Set defaults.'''

    return 'r', 'FERMILAB', 1970, 2020

def main(key, value, start, end):
    '''Add up all citations over a period.'''

    search = 'find {0} {1} and topcite 1+'.format(key, value)
    entity_papers = intbitset(perform_request_search(p=search, cc='HEP'))
    citation_list = get_cited_by_list(entity_papers)
    citation_dict = dict((cite[0], intbitset(cite[1])) 
                         for cite in citation_list)
    print 'The {0} papers of {1}'.format(len(entity_papers), value)

    all_papers = {}
    years = range(start, end)
    for year in years:
        search = 'earliestdate:' + str(year)
        all_papers[year] = intbitset(perform_request_search(p=search,
                                                          cc='HEP'))
    citations_year = {}
    total = 0
    for year in years:
        citations_year[year] = 0
        for entity_paper in entity_papers:
            citations_year[year] += len(citation_dict[entity_paper] &
                                      all_papers[year])
        total += citations_year[year]
        print '{0:6d} {1:6d} {2:6d}'.format(year, citations_year[year], total)




if __name__ == '__main__':

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 'k:v:s:e:')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    KEY, VALUE, START, END = set_defaults()
    for option, argument in OPTIONS:
        if option == '-k':
            KEY = argument
        if option == '-v':
            VALUE = argument
        if option == '-s':
            try:
                START = int(argument)
            except ValueError:
                print 'Non-integer for start year:', argument
        if option == '-e':
            try:
                END = int(argument)
            except ValueError:
                print 'Non-integer for end year:', argument

    try:
        main(key=KEY, value=VALUE, start=START, end=END)
    except KeyboardInterrupt:
        print 'Exiting'

