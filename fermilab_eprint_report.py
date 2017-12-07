"""Script to get the full-text for requested Fermilab report numbers."""

import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

from fermilab_eprint_report_input import REPORTS

BAD_RECIDS = [1340468, 1278565]

def get_eprint(recid):
    """Get the eprintt number from a record."""
    report_fermilab = None
    eprint = None
    reports = get_fieldvalues(recid, '037__a')
    reports = reports + get_fieldvalues(recid, '037__z')
    if VERBOSE:
        print reports
    for report in reports:
        if re.search("FERMILAB", report):
            report_fermilab = report
            if VERBOSE:
                print report_fermilab
    if not report_fermilab:
        return None
    bfo = BibFormatObject(recid)
    eprint = bfe_arxiv.get_arxiv(bfo, category = "no")
    if VERBOSE:
        print eprint
    if eprint:
        eprint = eprint[0]
        print report_fermilab, eprint
        return None
    for item in BibFormatObject(int(recid)).fields('8564_'):
        if item.has_key('y') and item.has_key('u'):
            if re.search('fermilab', item['y'].lower()):
                return None
            if item['y'].lower() == 'fulltext':
                print report_fermilab, item['u']


def main():
    """Look for eprints or other full text associated with report numbers."""

    for report in REPORTS:
        search = "037:" + report
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1:
            recid = result[0]
            if recid in BAD_RECIDS:
                continue
            else:
                get_eprint(recid)
        elif len(result) == 0:
            pass
        else:
            print "Something funny here ", report , len(result)


def conf_searches():
    """Search strings to find conferences."""

    search = '100__u:fermilab or 700__u:fermilab 0247_2:doi \
773__p:J.Phys.Conf.Ser. 8564_y:fulltext -037:fermilab*'

    print search

    search = '037:fermilab* 0247_2:doi \
773__p:J.Phys.Conf.Ser. 8564_y:fulltext -8564:fermilab*'

    print search

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
