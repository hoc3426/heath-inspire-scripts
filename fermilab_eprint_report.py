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
or r FERMILAB-PUB-09-846-CMS
or r FERMILAB-PUB-10-727-CMS
or r FERMILAB-PUB-11-816-CMS
or r FERMILAB-PUB-13-384-CMS
or r FERMILAB-PUB-14-085-CMS
or r FERMILAB-PUB-12-913-CMS
or r FERMILAB-PUB-12-918-CMS
or r FERMILAB-PUB-08-716-CMS
or r FERMILAB-PUB-07-807-CMS
or r FERMILAB-PUB-07-808-CMS
or r FERMILAB-PUB-07-809-CMS
or r FERMILAB-PUB-06-592-CMS
or r FERMILAB-PUB-14-153-CMS
or r FERMILAB-PUB-15-109-CMS
or r FERMILAB-PUB-15-110-CMS
or r FERMILAB-PUB-15-111-CMS
or r FERMILAB-PUB-15-119-CMS
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
