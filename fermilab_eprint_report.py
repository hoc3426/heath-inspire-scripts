import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.bibformat_engine import BibFormatObject
import invenio.bibformat_elements.bfe_INSPIRE_arxiv as bfe_arxiv

VERBOSE = True
VERBOSE = False

search = '035:/astro-ph/'
search = 'find primarch astro-ph not tc p not tc c and date < 2009'
search = 'find r fermilab and date 2014-05'
search = """find r CERN-TH-3368
or r FERMILAB-CONF-15-199-CD-ND-PPD
or r FERMILAB-CONF-15-202-ND
or r FERMILAB-CONF-15-203-ND
or r FERMILAB-CONF-15-204-ND
or r FERMILAB-TM-2604-CD
or r FERMILAB-CONF-15-211-CD
or r FERMILAB-CONF-15-217-ND
or r FERMILAB-CONF-15-218-A-CD
or r FERMILAB-CONF-15-219-CD
or r FERMILAB-CONF-15-221-ND
or r FERMILAB-CONF-15-233-AD
or r FERMILAB-CONF-15-242-ND
or r FERMILAB-PUB-15-262-ND
or r FERMILAB-CONF-15-263-PPD
or r FERMILAB-CONF-15-266-TD
or r FERMILAB-CONF-15-270-AD
or r FERMILAB-PUB-15-274-TD
or r FERMILAB-PUB-15-301-T
or r FERMILAB-PUB-15-302-ND
or r FERMILAB-PUB-15-307-AE
or r FERMILAB-CONF-15-316-TD
or r FERMILAB-PUB-15-317-AD
or r FERMILAB-PUB-15-318-A
or r FERMILAB-PUB-15-320-PPD
or r FERMILAB-CONF-15-321-AE
or r FERMILAB-PUB-15-323-T
or r FERMILAB-PUB-15-324-CMS
or r FERMILAB-PUB-15-325-CMS
or r FERMILAB-PUB-15-326-CMS
or r FERMILAB-PUB-15-327-CMS
or r FERMILAB-PUB-15-328-CMS
or r FERMILAB-PUB-15-329-CMS
or r FERMILAB-PUB-15-330-CMS
or r FERMILAB-PUB-15-331-CMS
or r FERMILAB-PUB-15-332-CMS
or r FERMILAB-PUB-15-333-CMS
or r FERMILAB-PUB-15-334-CMS
or r FERMILAB-PUB-15-335-CMS
or r FERMILAB-PUB-15-336-CMS
"""

x = perform_request_search(p=search,cc='HEP')
print "Found", len(x), "Fermilab reports"
if VERBOSE:
    print search
    print len(x)


for r in x:
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
#        out += format_bibtex_field("eprint",
#                                   eprints[0],
#                                   name_width,
#                                   value_width)
#        out += format_bibtex_field("archivePrefix",
#                                   "arXiv",
#                                   name_width,
#                                   value_width)
