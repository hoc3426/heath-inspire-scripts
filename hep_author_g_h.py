#!/usr/bin/python

'''A module to calculate the h-index and g-index of authors.'''

import getopt
import re
import sys
from invenio.search_engine import get_fieldvalues, perform_request_search

AUTHORS = ['Sidney.R.Coleman.1', 'R.J.Crewther.1', 'David.J.Gross.1']
BAI_REGEX = re.compile(r'[A-Z][A-z\.\-]+\.\d+$')
VERBOSE = False

def calculate_index(author):
    '''Calculate the authors indexes.'''

    search = "find ea " + author + " and primarch nucl-th"
    result = perform_request_search(p=search, cc='HEP')
    if len(result) == 0:
        #print author, 'has no citations.'
        return None
    citation_list = []
    for recid in result:
        search = 'refersto:recid:' + str(recid)
        citation_list.append(len(perform_request_search(p=search, cc='HEP')))
    citation_list.sort(reverse=True)
    total_citations = 0
    h_index = False
    g_index = False
    for index, value in enumerate(citation_list, 1):
        total_citations += value
        #print '{0:3d} {1:6d} {2:6d} {3:6d}'.format(index, value,
        #                                           total_citations,
        #                                           index*index)
        if index > value and h_index == False:
            h_index = index - 1
        if total_citations > index*index:
            g_index = index
    if h_index > 20:
        print '{0:20s} {1:7d} {2:7d}'.format(author, h_index, g_index)

def get_authors(search):
    '''Generate a list of authors'''

    if VERBOSE:
        print search
    bais = set()
    result = perform_request_search(p=search, cc='HepNames')
    for recid in result:
        id_nums = get_fieldvalues(recid, '035__a')
        for id_num in id_nums:
            if BAI_REGEX.match(id_num):
                bais.add(id_num)
    return bais 

def main(authors):
    '''Run for a list of authors.'''

    print '{0:20s} {1:7s} {2:7s}'.format('Author', 'h-index', 'g-index')
    for author in authors:
        calculate_index(author)

if __name__ == '__main__':

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 'r:s:v')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    for option, argument in OPTIONS:
        if option == '-r':
            AUTHORS = set([argument])
        elif option == '-s':
            AUTHORS = get_authors(argument)
        elif option == '-v':
            VERBOSE = True

    if VERBOSE:
        print AUTHORS    

    try:
        if AUTHORS:
            main(AUTHORS)
        else:
            print "Nothing to do."
    except KeyboardInterrupt:
        print 'Exiting'

