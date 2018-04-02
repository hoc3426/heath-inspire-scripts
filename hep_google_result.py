#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""This module returns a Google-like result"""

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from Counter import Counter
import operator
import sys

def main(search):
    """This module returns a Google-like result showing the most
       highly cited papers from a given result."""

    all_refs = []
    if not search:
        search = 'standard model'
        search = '"dark matter"'
        search = 'qcd sum rules'
    print 'Your search is', search
    result = perform_request_search(p=search, cc='HEP')
    print 'The result is', len(result)
    for recid in result:
        try:
            search = 'citedby:recid:' + str(recid)
            refs = perform_request_search(p=search, cc='HEP')
            all_refs += refs
        except:
            print 'problem with', recid
    all_refs.sort()
    counted_all_refs = Counter(all_refs)
    sorted_count = sorted(counted_all_refs.items(), key=operator.itemgetter(1),
                          reverse=True)
    for recid_count, count in sorted_count[-10:]:
        url = 'http://inspirehep.net/record/' + str(recid_count)
        print count, url
        title = get_fieldvalues(recid_count, '245__a')[0]
        try:
            author = get_fieldvalues(recid_count, '710__g')[0]
        except:
            try:
                author = get_fieldvalues(recid_count, '100__a')[0]
            except:
                author = 'No Author'
        print '  ', author, ':', title

if __name__ == '__main__':
    SEARCH = sys.argv[1:][0]
    try:
        main(SEARCH)
    except KeyboardInterrupt:
        print 'Exiting'

