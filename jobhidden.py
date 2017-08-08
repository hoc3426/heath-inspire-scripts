from invenio.bibrecord import print_rec, record_add_field
from invenio.search_engine import perform_request_search
import re

VERBOSE = True
VERBOSE = False

for i in open('tmp_jobhidden.in','r').readlines() :
    recid = 0
    i = i.replace('%20', ' ')
    matchObj = re.search(r"Remove[ \+]posting[ \+]in[ \+]HEPJobs[ \+](\d+)", i)
    if matchObj:
        recid = matchObj.group()
        recid = re.sub(r'\D', r'', recid)
    else:
        matchObj = re.search(r"Remove\-listing\-(JOBSUBMIT\-JOB\-\S+)", i)
        if matchObj:
            if VERBOSE:
                print 'VERBOSE', matchObj.group()
            submission_id = matchObj.group(1)
            search = '037__a:' + submission_id
            if VERBOSE:
                print 'VERBOSE', search
            result = perform_request_search(p = search, cc = "Jobs")
            if len(result) == 1:
                recid = result[0]
    if recid:
        common_fields = {}
        common_tags = {}
        record_add_field(common_fields, '001', controlfield_value=str(recid))
        common_tags['980__'] = [('a', 'JOBHIDDEN')]
        for key in common_tags:
            tag = key
            record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
        print print_rec(common_fields)

