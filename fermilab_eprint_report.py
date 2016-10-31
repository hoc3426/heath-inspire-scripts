import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

reports = [
'FERMILAB-PUB-16-399-TD',
'FERMILAB-CONF-16-401-ND',
'FERMILAB-PUB-16-403-CMS',
'FERMILAB-CONF-16-405-AD',
'FERMILAB-CONF-16-406-AD',
'FERMILAB-PUB-16-407-CD',
'FERMILAB-PUB-16-409-APC',
'FERMILAB-CONF-16-410-AD',
'FERMILAB-PUB-16-420-A',
'FERMILAB-TM-2638',
'FERMILAB-CONF-16-431-AD',
'FERMILAB-CONF-16-437-AD',
'FERMILAB-CONF-16-439-AD',
'FERMILAB-CONF-16-446-AD',
'FERMILAB-PUB-16-450-AE',
'FERMILAB-PUB-16-454-AE',
'FERMILAB-PUB-16-458-T',
'FERMILAB-CONF-16-462-APC',
'FERMILAB-PUB-16-465-T',
'FERMILAB-FN-1025-T',
'FERMILAB-PUB-16-472',
'FERMILAB-PUB-16-475-CMS',
'FERMILAB-PUB-16-478-CMS',
'FERMILAB-PUB-16-479-AE-PPD',
'FERMILAB-PUB-16-480-CMS',
'FERMILAB-PUB-16-481-CMS',
'FERMILAB-PUB-16-482-CMS',
'FERMILAB-PUB-16-483-CMS',
'FERMILAB-PUB-16-484-CMS',
'FERMILAB-PUB-16-485-CMS',
'FERMILAB-PUB-16-486-CMS',
'FERMILAB-PUB-16-487-CMS',
'FERMILAB-PUB-16-488-CMS',
'FERMILAB-PUB-16-489-CMS',
'FERMILAB-PUB-16-490-CMS',
'FERMILAB-PUB-16-491-CMS',
'FERMILAB-PUB-16-492-CMS',
'FERMILAB-PUB-16-493-CMS',
'FERMILAB-PUB-16-494-CMS',
'FERMILAB-PUB-16-495-CMS',
'FERMILAB-PUB-16-496-CMS'
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


