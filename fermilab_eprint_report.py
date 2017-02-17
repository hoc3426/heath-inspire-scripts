import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
'FERMILAB-TM-2638',
'FERMILAB-CONF-16-431-AD',
'FERMILAB-CONF-16-437-AD',
'FERMILAB-CONF-16-439-AD',
'FERMILAB-CONF-16-446-AD',
'FERMILAB-PUB-16-450-AE',
'FERMILAB-PUB-16-454-AE',
'FERMILAB-CONF-16-462-APC',
'FERMILAB-PUB-16-475-CMS',
'FERMILAB-PUB-16-527',
'FERMILAB-PUB-16-554-T',
'FERMILAB-PUB-16-560',
'FERMILAB-PUB-16-566-AD',
'FERMILAB-PUB-16-568',
'FERMILAB-PUB-16-596-PPD',
'FERMILAB-PUB-16-598-AD-APC',
'FERMILAB-PUB-16-614-AE',
'FERMILAB-TM-2642-ND',
'FERMILAB-PUB-17-005-T',
'FERMILAB-TEST-17-001-LBNF',
'FERMILAB-CONF-16-628-ND',
'FERMILAB-PUB-16-636-CMS',
'FERMILAB-CONF-16-638-CD',
'FERMILAB-TEST-17-002-LBNF',
'FERMILAB-CONF-17-022-AD',
'FERMILAB-PUB-17-025-AE',
'FERMILAB-PUB-17-026-CD',
'FERMILAB-PUB-17-027-AE',
'FERMILAB-PUB-17-034-CMS-E',
'FERMILAB-CONF-17-036-TD',
'FERMILAB-PUB-16-650',
'FERMILAB-PUB-16-653',
'FERMILAB-PUB-17-039-A-AE-PPD',
'FERMILAB-PUB-15-657-APC',
'FERMILAB-CONF-17-040-T',
'FERMILAB-PUB-17-042-PPD',
'FERMILAB-CONF-17-044-CD',
'FERMILAB-PUB-17-047',
'FERMILAB-PUB-16-654-A'
]

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


for report in reports:
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


