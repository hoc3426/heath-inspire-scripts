import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
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
'FERMILAB-PUB-16-256-CMS',
'FERMILAB-PUB-16-262-T',
'FERMILAB-TM-2629-APC',
'FERMILAB-CONF-16-295-E',
'FERMILAB-CONF-16-298-E',
'FERMILAB-PUB-16-301-T',
'FERMILAB-PUB-16-303-A',
'FERMILAB-PUB-16-304-PPD',
'FERMILAB-PUB-16-305-CMS',
'FERMILAB-PUB-16-306-CMS',
'FERMILAB-PUB-16-307-CMS',
'FERMILAB-PUB-16-308-CMS',
'FERMILAB-PUB-16-309-CMS',
'FERMILAB-PUB-16-310-CMS',
'FERMILAB-PUB-16-311-CMS',
'FERMILAB-PUB-16-312-CMS',
'FERMILAB-PUB-16-313-CMS'
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
        print "Something funny here " + report + len(result)


