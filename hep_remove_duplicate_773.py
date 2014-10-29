"""
Script for getting records with multiple 773 fields due to full pub note
being appended to a record with a "Submitted to" 773 field. Keeps the
full pubnote.
"""

from invenio.search_engine_utils import get_fieldvalues
from invenio.search_engine import get_record
from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_get_field_instances, \
         record_add_field

import re

from hep_ads_xmltree import JOURNAL_DICT

def create_xml(recid):
    """
    Searches for duplicate instances of 773 and keeps the good one.
    """
    tag = '773__'
    tag_value = tag + 'p'
    journal = get_fieldvalues(recid, tag_value)
    if len(journal) == 2 and journal[0] == journal[1]:
        record = get_record(recid)
        correct_record = {}
        record_add_field(correct_record, '001', \
            controlfield_value=str(recid))
        field_instances = record_get_field_instances(record, \
                              tag[0:3], tag[3], tag[4])
        correct_subfields = []
        c_value = False
        for field_instance in field_instances:
            for code, value in field_instance[0]:
                if value == 'To appear in the proceedings of':
                    pass
                elif (code, value) not in correct_subfields:
                    if code == 'c':
                        if c_value:
                            if len(value) > len(c_value):
                                c_value = value
                        else:
                            c_value = value
                    else:
                        correct_subfields.append((code, value))
        if c_value:
            correct_subfields.append(('c', c_value))
        record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                    subfields=correct_subfields)
        return print_rec(correct_record)
    return None

def main():
    """
    Searches for papers in journals
    """
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    for key in JOURNAL_DICT:
        journal = JOURNAL_DICT[key]
        print journal
        search = '773__p:"' + journal + '" 035__9:ads'
        result = perform_request_search(p=search, cc = 'HEP')
        output_counter = 1
        if len(result):
            for recid in result:
                if output_counter == 101:
                    break
                record_update = create_xml(recid)
                if record_update:
                    output.write(record_update)
                    output_counter += 1
    output.write('</collection>')
    output.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
