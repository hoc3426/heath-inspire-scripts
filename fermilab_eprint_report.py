import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
'FERMILAB-CONF-16-360-AD',
'FERMILAB-TEST-16-002-CD',
'FERMILAB-PUB-16-371-ND',
'FERMILAB-PUB-16-376-CMS',
'FERMILAB-PUB-16-378-CMS',
'FERMILAB-CONF-16-390-TD',
'FERMILAB-PUB-16-399-TD',
'FERMILAB-CONF-16-401-ND',
'FERMILAB-PUB-16-403-CMS',
'FERMILAB-PUB-16-407-CD',
'FERMILAB-PUB-16-409-APC',
'FERMILAB-CONF-16-410-AD',
'FERMILAB-PUB-16-420-A',
'FERMILAB-TM-2638',
'FERMILAB-CONF-16-431-AD',
'FERMILAB-CONF-16-437-AD',
'FERMILAB-CONF-16-439-AD',
'FERMILAB-CONF-16-446-AD',
'FERMILAB-PUB-16-454-AE',
'FERMILAB-CONF-16-462-APC',
'FERMILAB-PUB-16-475-CMS',
'FERMILAB-PUB-16-560',
'FERMILAB-PUB-16-568',
'FERMILAB-PUB-16-598-AD-APC',
'FERMILAB-PUB-16-614-AE',
'FERMILAB-TM-2642-ND',
'FERMILAB-TEST-17-001-LBNF',
'FERMILAB-CONF-16-628-ND',
'FERMILAB-PUB-16-636-CMS',
'FERMILAB-TEST-17-002-LBNF',
'FERMILAB-PUB-17-025-AE',
'FERMILAB-PUB-17-026-CD',
'FERMILAB-PUB-17-034-CMS-E',
'FERMILAB-CONF-17-036-TD',
'FERMILAB-PUB-17-042-PPD',
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
'FERMILAB-POSTER-17-010-TD',
'FERMILAB-SLIDES-17-007-TD',
'FERMILAB-CONF-17-127-ND',
'FERMILAB-CONF-17-130-PPD',
'FERMILAB-SLIDES-17-008-TD',
'FERMILAB-PUB-17-136-PPD',
'FERMILAB-CONF-14-597-ND',
'FERMILAB-CONF-17-141-APC',
'FERMILAB-CONF-17-142-AD',
'FERMILAB-CONF-17-157-AD',
'FERMILAB-CONF-17-158-ND',
'FERMILAB-POSTER-17-012-AD',
'FERMILAB-PUB-17-168-PPD',
'FERMILAB-PUB-17-180-AE',
'FERMILAB-CONF-17-184-LBNF',
'FERMILAB-PUB-16-687-CMS-E',
'FERMILAB-PUB-17-190-T',
'FERMILAB-PUB-17-194-LBNF-ND-T',
'FERMILAB-PUB-17-195-ND-T',
'FERMILAB-PUB-17-196-T',
'FERMILAB-TM-2655-APC',
'FERMILAB-PUB-17-198-ND',
'FERMILAB-CONF-17-201-E',
'FERMILAB-PUB-17-202-PPD-T',
'FERMILAB-PUB-17-203-A',
'FERMILAB-PUB-17-204-AE',
'FERMILAB-CONF-16-691-E',
'FERMILAB-CONF-17-207-PPD',
'FERMILAB-PUB-17-208-AE',
'FERMILAB-PUB-17-209-E',
'FERMILAB-PUB-16-695-AE-PPD',
'FERMILAB-PUB-17-210-T',
'FERMILAB-PUB-16-696-PPD',
'FERMILAB-CONF-15-664-PPD',
'FERMILAB-PUB-15-665-AD-PPD',
'FERMILAB-PUB-16-698-TD'
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


