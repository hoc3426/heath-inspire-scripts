import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
'FERMILAB-TEST-17-003-LDRD',
'FERMILAB-PUB-16-667-PPD',
'FERMILAB-PUB-17-088',
'FERMILAB-PUB-17-092-CD',
'FERMILAB-PUB-17-099-APC',
'FERMILAB-PUB-17-113-CMS',
'FERMILAB-PUB-17-120-CMS',
'FERMILAB-POSTER-17-010-TD',
'FERMILAB-SLIDES-17-007-TD',
'FERMILAB-CONF-17-127-ND',
'FERMILAB-CONF-17-130-PPD',
'FERMILAB-SLIDES-17-008-TD',
'FERMILAB-PUB-17-136-PPD',
'FERMILAB-CONF-14-597-ND',
'FERMILAB-CONF-17-141-APC',
'FERMILAB-CONF-17-142-AD',
'FERMILAB-CONF-17-153-AD',
'FERMILAB-CONF-17-155-AD',
'FERMILAB-CONF-17-157-AD',
'FERMILAB-CONF-17-158-ND',
'FERMILAB-POSTER-17-012-AD',
'FERMILAB-PUB-17-168-PPD',
'FERMILAB-PUB-17-179-PPD',
'FERMILAB-PUB-17-180-AE',
'FERMILAB-PUB-17-183-AE-E-PPD',
'FERMILAB-CONF-17-184-LBNF',
'FERMILAB-PUB-16-687-CMS-E',
'FERMILAB-PUB-17-190-T',
'FERMILAB-PUB-17-194-LBNF-ND-T',
'FERMILAB-PUB-17-195-ND-T',
'FERMILAB-PUB-17-196-T',
'FERMILAB-PUB-16-689-AE-CD'
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


