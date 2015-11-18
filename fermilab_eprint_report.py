import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
'FERMILAB-TM-2604-CD',
'FERMILAB-CONF-15-211-CD',
'FERMILAB-CONF-15-217-ND',
'FERMILAB-CONF-15-219-CD',
'FERMILAB-CONF-15-221-ND',
'FERMILAB-CONF-15-242-ND',
'FERMILAB-PUB-15-262-ND',
'FERMILAB-CONF-15-266-TD',
'FERMILAB-CONF-15-270-AD',
'FERMILAB-PUB-15-274-TD',
'FERMILAB-CONF-15-316-TD',
'FERMILAB-PUB-15-317-AD',
'FERMILAB-CONF-15-344-AD',
'FERMILAB-CONF-15-360-PPD',
'FERMILAB-PUB-15-367-APC',
'FERMILAB-CONF-15-369-AD',
'FERMILAB-TM-2610-AE-CD',
'FERMILAB-PUB-15-392-AE',
'FERMILAB-PUB-15-407-T',
'FERMILAB-PUB-15-411-A',
'FERMILAB-CONF-15-412-AD-TD',
'FERMILAB-PUB-15-421-CMS',
'FERMILAB-PUB-15-430-T',
'FERMILAB-PUB-15-441-AE',
'FERMILAB-CONF-15-446-AD-APC',
'FERMILAB-PUB-15-449-AE-E',
'FERMILAB-TEST-15-007-CD',
'FERMILAB-PUB-15-458-ND',
'FERMILAB-PUB-15-460-CMS',
'FERMILAB-PUB-15-461-CMS',
'FERMILAB-PUB-15-462-CMS',
'FERMILAB-PUB-15-463-CMS',
'FERMILAB-PUB-15-464-CMS',
'FERMILAB-PUB-15-465-CMS',
'FERMILAB-PUB-15-466-CMS',
'FERMILAB-PUB-15-467-CMS',
'FERMILAB-PUB-15-468-CMS',
'FERMILAB-PUB-15-469-CMS',
'FERMILAB-PUB-15-471-CMS',
'FERMILAB-PUB-15-472-CMS',
'FERMILAB-PUB-15-473-CMS'
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


