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
or r FERMILAB-TM-2604-CD
or r FERMILAB-CONF-15-211-CD
or r FERMILAB-CONF-15-217-ND
or r FERMILAB-CONF-15-219-CD
or r FERMILAB-CONF-15-221-ND
or r FERMILAB-CONF-15-233-AD
or r FERMILAB-CONF-15-242-ND
or r FERMILAB-PUB-15-262-ND
or r FERMILAB-CONF-15-266-TD
or r FERMILAB-CONF-15-270-AD
or r FERMILAB-PUB-15-274-TD
or r FERMILAB-PUB-15-301-T
or r FERMILAB-CONF-15-316-TD
or r FERMILAB-PUB-15-317-AD
or r FERMILAB-PUB-15-320-T
or r FERMILAB-PUB-15-323-T
or r FERMILAB-CONF-15-342-T
or r FERMILAB-CONF-15-344-AD
or r FERMILAB-PUB-15-353-T
or r FERMILAB-PUB-15-358-TD
or r FERMILAB-PUB-15-359-A
or r FERMILAB-CONF-15-360-PPD
or r FERMILAB-PUB-15-361-E
or r FERMILAB-CONF-15-362-TD
or r FERMILAB-PUB-14-578-AE
or r FERMILAB-PUB-15-363-T
or r FERMILAB-PUB-15-367-APC
or r FERMILAB-CONF-15-369-AD
or r FERMILAB-PUB-15-374-T
or r FERMILAB-PUB-15-375-ND-PPD-T
or r FERMILAB-PUB-15-376-CMS
or r FERMILAB-PUB-15-377-CMS
or r FERMILAB-PUB-15-378-CMS
or r FERMILAB-PUB-15-379-CMS
or r FERMILAB-PUB-15-380-CMS
or r FERMILAB-PUB-15-381-CMS
or r FERMILAB-PUB-15-382-CMS
or r FERMILAB-PUB-15-383-CMS
or r FERMILAB-PUB-15-384-T
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
