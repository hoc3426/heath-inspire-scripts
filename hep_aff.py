#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Converts the raw affiliation strings into proper INSPIRE format."""


import re
import sys

from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field
from afftranslator2 import bestmatch


VERBOSE = False
VERBOSE = True

def find_records():
    """Find records that have raw string affilations."""
    atsearch = '100__u:/UNDEFINED/ or 700__u:/UNDEFINED/'
    atsearch = '100__v:Fermilab or 700__v:Fermilab'
    atsearch = '700__v:/fermi.*batavia/ - 700__u:fermilab'
    #atsearch = '001:1475323'
    return perform_request_search(p=atsearch, cc='HEP')

def get_aff(aff):
    """Convert raw string affilation to INSPIRE form."""
    #best_match = bestmatch(aff,'ICN')
    #affiliation = best_match[0]
    #aff_new = affiliation[1]
    #aff_new = re.sub(';', '</subfield><subfield code="u">', aff_new)
    #return aff_new
    return bestmatch(aff, 'ICN')[0][1].split(';')


def create_xml(recid, tags, force_flag=False):
    """Create xml file to replace to 100, 700 block."""

    if VERBOSE:
        print 'force_flag =', force_flag
    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    flag = None
    for tag in tags:
        field_instances = record_get_field_instances(record, tag[0:3], \
                                                     tag[3], tag[4])
        correct_subfields = []
        for field_instance in field_instances:
            correct_subfields = []
            for code, value in field_instance[0]:
                if code == 'u' or code == 'v':
                    if  re.search(r'UNDEFINED', value) or force_flag:
                        new_value = get_aff(value)
                        if new_value:
                            correct_subfields.append(('v', value))
                            value = new_value
                            code = 'u'
                            flag = True
                correct_subfields.append((code, value))
            record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                             subfields=correct_subfields)
    #return print_rec(correct_record)
    if flag:
        print correct_record
        return print_rec(correct_record)

def main_old(recordlist):
    """Old."""
    if not recordlist:
        force_flag = False
        force_flag = True
        if VERBOSE:
            print "scanning all HEP records ..."
        recordlist = find_records()
        if VERBOSE:
            print "%d records with unprocessed affiliations fields found" % \
                    len(recordlist)
    else:
        force_flag = True
        try:
            recordlist = [int(r) for r in recordlist]
        except TypeError:
            print "ERROR: bad recid given"
    for record in recordlist:
        if VERBOSE > 0:
            print "doing %d" % (record)
        create_xml(record, ['100__','700__'], force_flag)


def main(recordlist):
    """Take input in terms or recid list or generate a list."""

    force_flag = True
    if not recordlist:
        force_flag = True
        if VERBOSE:
            print "scanning all HEP records ..."
        recordlist = find_records()
        if len(recordlist) == 0:
            return None
        if VERBOSE:
            print "%d records found" \
                   % len(recordlist)
    else:
        try:
            recordlist = [int(r) for r in recordlist]
        except TypeError:
            print "ERROR: bad recid given"
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    for record in recordlist:
        if VERBOSE > 0:
            print "doing %d" % (record)
        update = create_xml(record, ['100__', '700__'], force_flag)
        if update:
            output.write(update)
    output.write('</collection>')
    output.close()



if __name__ == '__main__':
    RECIDS = sys.argv[1:]
    try:
        main(RECIDS)
    except KeyboardInterrupt:
        print 'Exiting'
    except:
        main(find_records())

