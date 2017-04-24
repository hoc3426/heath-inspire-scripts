import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
'FERMILAB-POSTER-17-002-CD',
'FERMILAB-PUB-16-662-CMS',
'FERMILAB-CONF-15-658-CMS',
'FERMILAB-CONF-15-659-CMS',
'FERMILAB-CONF-15-660-CMS',
'FERMILAB-CONF-14-592-CMS',
'FERMILAB-CONF-14-593-CMS',
'FERMILAB-CONF-14-594-CMS',
'FERMILAB-CONF-14-595-CMS',
'FERMILAB-POSTER-17-003-DI',
'FERMILAB-PUB-17-077-T',
'FERMILAB-PUB-17-080-A',
'FERMILAB-SLIDES-17-003-CD',
'FERMILAB-POSTER-17-004-DI',
'FERMILAB-SLIDES-17-004-LDRD',
'FERMILAB-SLIDES-17-005-FESS',
'FERMILAB-POSTER-17-005-CMS',
'FERMILAB-POSTER-17-006-AE',
'FERMILAB-POSTER-17-007-ESH',
'FERMILAB-TM-2650-E',
'FERMILAB-TM-2651-E',
'FERMILAB-TEST-17-003-LDRD',
'FERMILAB-PUB-16-667-PPD',
'FERMILAB-PUB-17-088',
'FERMILAB-PUB-17-092-CD',
'FERMILAB-PUB-17-099-APC',
'FERMILAB-PUB-17-113-CMS',
'FERMILAB-PUB-17-120-CMS',
'FERMILAB-FN-1030-ND',
'FERMILAB-PUB-17-122-T',
'FERMILAB-POSTER-17-010-TD',
'FERMILAB-SLIDES-17-007-TD',
'FERMILAB-PUB-17-125-A',
'FERMILAB-PUB-16-669-CD-ND'
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


