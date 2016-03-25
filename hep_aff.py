#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys

from invenio.search_engine import perform_request_search, get_fieldvalues, \
     get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field, record_xml_output
from invenio.intbitset import intbitset
from afftranslator2 import *


verbose = 0

def find_records():
    atsearch = '100__u:/UNDEFINED/ or 700__u:/UNDEFINED/'
    atsearch = '100__v:Fermilab or 700__v:Fermilab'
    atsearch = '700__v:/fermi.*batavia/ - 700__u:fermilab'
    return perform_request_search(p=atsearch, cc='HEP')

def get_aff(aff):
    bm = bestmatch(aff,'ICN')
    a = bm[0]
    affNew = a[1]
    affNew = re.sub(';', '</subfield><subfield code="u">', affNew)
    return affNew

def create_xml(recid, tags, forceFlag):
    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    flag = None
    for tag in tags:
        field_instances = record_get_field_instances(record, tag[0:3], tag[3], tag[4])
        correct_subfields = []
        for field_instance in field_instances:
            correct_subfields = []
            for code, value in field_instance[0]:
                if code == 'u' or code == 'v':
                    if  re.search(r'UNDEFINED', value) or forceFlag:
                        new_value = get_aff(value)        
                        if new_value:
                            correct_subfields.append(('v', value))
                            value = new_value
                            code = 'u'
                            flag = True
                correct_subfields.append((code, value))
            record_add_field(correct_record, tag[0:3], tag[3], tag[4], subfields=correct_subfields)
    #return print_rec(correct_record)
    if flag:
        print print_rec(correct_record)

def main(recordlist):
    if not recordlist:
        forceFlag = False
        forceFlag = True
        if verbose: print "scanning all HEP records ..."
        recordlist = find_records()
        if verbose: print "%d records with '@' in author fields found" % len(recordlist)
    else:
        forceFlag = True
        try:
            recordlist = [int(r) for r in recordlist]
        except:
            print "ERROR: bad recid given"
    for record in recordlist:
        if verbose > 0: print "doing %d" % (record)     
        #print create_xml(record,['100__','700__'])
        create_xml(record, ['100__','700__'], forceFlag)


if __name__ == '__main__':
    recids = sys.argv[1:]
    try:
        main(recids)   
    except KeyboardInterrupt:
        print 'Exiting'
    except:
        main(find_records())

