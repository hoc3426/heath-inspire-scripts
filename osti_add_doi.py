'''Script to add an OSTI-based DOI to INSPIRE records.'''

import re

from invenio.bibrecord import print_rec, record_add_field
from invenio.search_engine import perform_request_search
from invenio.intbitset import intbitset

from osti_web_service import get_osti_id
from check_url import checkURL

COUNTER = 1
COUNTER_END = 500
SEARCH = r'037:fermilab-* 035__9:osti -0247:doi -037:arXiv -773__p:/\w/'
RESULT_HEP = perform_request_search(p=SEARCH, cc='HEP')
RESULT_FERMILAB = perform_request_search(p=SEARCH, cc='Fermilab')
RESULT = intbitset(RESULT_HEP) | intbitset(RESULT_FERMILAB)
print "Number of records:", len(RESULT)
RESULT = reversed(RESULT)
DOIS = set()

FILENAME = 'tmp_' + __file__
FILENAME = re.sub('.py', '_append.out', FILENAME)
OUTPUT = open(FILENAME,'w')

for recid in RESULT:
    if COUNTER > COUNTER_END:
        break
    common_fields = {}
    common_tags = {}
    doi = get_osti_id(recid)
    if doi in DOIS:
        print "Duplicate: recid, doi =", recid, doi
        break
    if not doi:
        print "No OSTI ID: recid =", recid
        continue
    DOIS.add(doi)
    doi = '10.2172/' + doi
    url = 'https://doi.org/api/handles/' + doi
    try:
        checkURL(url)
    except ValueError:
        continue
    COUNTER += 1
    record_add_field(common_fields, '001', controlfield_value=str(recid))
    common_tags['0247_'] = [('a', doi), ('2', 'DOI'), ('9', 'OSTI')]
    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    OUTPUT.write(print_rec(common_fields))


OUTPUT.close()
print "Number of records:", COUNTER
print FILENAME
quit()


