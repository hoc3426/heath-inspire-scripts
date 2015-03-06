from invenio.bibrecord import print_rec, record_add_field, record_xml_output
import re

for i in open('tmp_jobhidden.in','r').readlines() :
    matchObj = re.search("Remove posting in HEPJobs (\d+)", i)
    if matchObj : 
        recid = matchObj.group()
        recid = re.sub(r'\D', r'', recid)
        common_fields = {}
        common_tags = {}
        record_add_field(common_fields, '001', controlfield_value=str(recid))
        common_tags['980__'] = [('a', 'JOBHIDDEN')]
        for key in common_tags:
            tag = key
            record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
        print print_rec(common_fields)


