#!/usr/bin/python

'''A module to calculate the h-index and g-index of authors.'''

import sys
from invenio.search_engine import perform_request_search

AUTHORS = ['Sidney.R.Coleman.1', 'R.J.Crewther.1', 'David.J.Gross.1']

def calculate_index(author):
    '''Calculate the authors indexes.'''

    search = "find ea " + author
    result = perform_request_search(p=search, cc='HEP')
    if len(result) == 0:
        print author, 'has no citations.'
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
    print '{0:20s} {1:7d} {2:7d}'.format(author, h_index, g_index)


def main(authors):
    '''Run for a list of authors.'''

    print '{0:20s} {1:7s} {2:7s}'.format('Author', 'h-index', 'g-index')
    for author in authors:
        calculate_index(author)

if __name__ == '__main__':

    try:
        AUTHORS_INPUT = []
        AUTHOR = sys.argv[1:][0]
        AUTHORS_INPUT.append(AUTHOR)
        AUTHORS = AUTHORS_INPUT
    except IndexError:
        pass

    try:
        if AUTHORS:
            main(AUTHORS)
        else:
            print "Nothing to do."
    except KeyboardInterrupt:
        print 'Exiting'

