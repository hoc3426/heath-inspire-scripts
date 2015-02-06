#!/usr/bin/python
# -*- coding: UTF-8 -*-

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from Counter import Counter
import collections
import sys

def main(search):
    all_refs = []
    if not search:
        search = 'standard model'
        search = '"dark matter"'
        search = 'qcd sum rules'
    print 'Your search is', search
    x = perform_request_search(p=search, cc='HEP')
    print 'The result is', len(x)
    for r in x:
        try:
            search = 'citedby:recid:' + str(r)
            refs = perform_request_search(p=search, cc='HEP')
            all_refs += refs
        except:
            print 'problem with', r
    d = Counter(all_refs)
    l = list(set(all_refs))
    topcites = {}
    for key in d:
        #if d[key] > 200:
        topcites[d[key]] = key
    od = collections.OrderedDict(sorted(topcites.items()))
    for k, v in od.iteritems():
        print k, v
        title = get_fieldvalues(v, '245__a')[0]
        print '  ', title


if __name__ == '__main__':
    SEARCH = sys.argv[1:][0]
    try:
        main(SEARCH)
    except KeyboardInterrupt:
        print 'Exiting'

