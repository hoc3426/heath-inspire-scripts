import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

from fermilab_eprint_report_input import REPORTS

BAD_RECIDS = [1340468, 1278565]

def get_eprint(r):
    report_fermilab = ''
    eprint = ''
    reports = get_fieldvalues(r,'037__a')
    reports = reports + get_fieldvalues(r,'037__z')
    if VERBOSE:
        print reports
    for report in reports:
        if re.search("FERMILAB", report):
            report_fermilab = report
            if VERBOSE:
                print report_fermilab
    bfo = BibFormatObject(r)
    eprint = bfe_arxiv.get_arxiv(bfo, category = "no")
    if VERBOSE:
        print eprint
    if eprint: 
        eprint = eprint[0]
        if report_fermilab:
            print report_fermilab, eprint


for report in REPORTS:
    search = "037:" + report
    result = perform_request_search(p=search,cc='HEP')    
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


