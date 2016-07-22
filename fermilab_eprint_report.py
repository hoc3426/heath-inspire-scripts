import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
'FERMILAB-PUB-16-259-CMS',
'FERMILAB-PUB-16-260-CMS',
'FERMILAB-PUB-16-261-T',
'FERMILAB-PUB-16-262-T',
'FERMILAB-PUB-16-263-A'
'FERMILAB-PUB-15-367-APC',
'FERMILAB-CONF-15-369-AD',
'FERMILAB-CONF-15-412-AD-TD',
'FERMILAB-PUB-15-421-CMS',
'FERMILAB-PUB-15-441-AE',
'FERMILAB-TEST-15-007-CD',
'FERMILAB-PUB-15-458-ND',
'FERMILAB-CONF-15-481-CD-T',
'FERMILAB-PUB-15-515-CMS',
'FERMILAB-CONF-14-580-ND',
'FERMILAB-CONF-15-564-ND',
'FERMILAB-PUB-08-729-CMS',
'FERMILAB-PUB-16-004-T',
'FERMILAB-CONF-16-015-ND',
'FERMILAB-CONF-15-620-ND',
'FERMILAB-PUB-16-021-AE',
'FERMILAB-FN-1007-CD',
'FERMILAB-CONF-16-078-PPD',
'FERMILAB-PUB-16-110-PPD',
'FERMILAB-PUB-16-112-ND',
'FERMILAB-TEST-16-001-LDRD',
'FERMILAB-PUB-16-145-ND',
'FERMILAB-TM-2626-CMS-E',
'FERMILAB-CONF-16-163-AD',
'FERMILAB-CONF-16-167-FESS',
'FERMILAB-PUB-16-170-CD',
'FERMILAB-PUB-16-172-ND',
'FERMILAB-PUB-16-191-CMS',
'FERMILAB-PUB-16-193-CMS',
'FERMILAB-FN-1018-TD',
'FERMILAB-PUB-16-220',
'FERMILAB-TM-2628-ND',
'FERMILAB-CONF-16-236-AD',
'FERMILAB-PUB-16-248-TD',
'FERMILAB-PUB-16-249-TD',
'FERMILAB-PUB-16-251-T',
'FERMILAB-PUB-16-256-CMS',
'FERMILAB-PUB-16-262-T',
'FERMILAB-PUB-16-264-A',
'FERMILAB-TM-2629-APC',
'FERMILAB-PUB-16-267-T',
'FERMILAB-PUB-16-278-T',
'FERMILAB-PUB-15-648-CD-ND'
]

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
        get_eprint(result[0])
    elif len(result) == 0:
        pass
    else:
        print "Something funny here " + report + len(result)


