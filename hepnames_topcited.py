import re
import collections
from Counter import Counter
import operator

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

from hep_convert_email_to_id import get_hepnames_anyid_from_recid

authors = ['A.W.Thomas.1', 'E.Witten.1', 'C.D.Roberts.1']
SEARCH = '65017a:hep-ph or 65017a:hep-th or 65017a:gr-qc or \
65017a:hep-lat or 65017a:nucl-th 035__9:bai'


def find_authors():
    search = SEARCH
    print search
    result = perform_request_search(p=search,cc='HepNames')
    authors = []
    for recid in result:
        bai = get_hepnames_anyid_from_recid(recid, 'BAI')
        if bai:
            authors.append(bai)
    return authors

authors = find_authors()
topcited_authors = []
for author in authors:
    search = 'refersto:(exactauthor:' + author + ' authorcount:1->20 -title:rpp)'
    #print search
    result = perform_request_search(p=search,cc='HEP')
    citations = len(result)
    if citations > 999:
        topcited_authors.append((citations, author))
topcited_authors.sort(reverse=True)

counter = 1
for author in topcited_authors:
    print counter, author
    counter += 1

