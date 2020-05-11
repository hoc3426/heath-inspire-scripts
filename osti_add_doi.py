'''Script to add an OSTI-based DOI to INSPIRE records.'''

import os
import re


from invenio.bibrecord import print_rec, record_add_field
from invenio.search_engine import perform_request_search
from invenio.intbitset import intbitset

from osti_web_service import get_osti_id
#from check_url import checkURL

COUNTER = 0
COUNTER_END = 500
SEARCH = r'037:fermilab-* 035__9:osti -0247:doi -037:arXiv -773__p:/\w/'
SEARCH = r'035__9:osti du:2020 -0247:doi -037:arXiv -773__p:/\w/'
RESULT_HEP = perform_request_search(p=SEARCH, cc='HEP')
RESULT_FERMILAB = perform_request_search(p=SEARCH, cc='Fermilab')
RESULT = intbitset(RESULT_HEP) | intbitset(RESULT_FERMILAB)
#RESULT = [1253262]
print "Number of records:", len(RESULT)
RESULT = reversed(RESULT)
OSTI_IDS = set()

FILENAME = 'tmp_' + __file__
FILENAME = re.sub('.py', '_append.out', FILENAME)
OUTPUT = open(FILENAME,'w')

def bad_url(url):
    curl = 'curl --output /dev/null --silent --head --fail '
    if os.system(curl + url) != 0:
        return True
    return False
 
for recid in RESULT:
    if COUNTER > COUNTER_END:
        break
    common_fields = {}
    common_tags = {}
    osti_id = get_osti_id(recid)
    if osti_id in OSTI_IDS:
        print "Duplicate: recid, osti_id =", recid, osti_id
        break
    if not osti_id:
        print "No OSTI ID: recid =", recid
        continue
    OSTI_IDS.add(osti_id)
    doi = '10.2172/' + osti_id
    url = 'https://doi.org/api/handles/' + doi
    if bad_url(url):
        if bad_url('https://www.osti.gov/biblio/' + osti_id):
            print "OSTI link does not work: recid, osti_id =", recid, osti_id
        continue
    
    #try:
    #    checkURL(url)
    #except ValueError:
    #    try:
    #        checkURL('https://www.osti.gov/biblio/' + osti_id)
    #    except ValueError:
    #        print "OSTI link does not work: recid, osti_id =", recid, osti_id
    #    continue
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


