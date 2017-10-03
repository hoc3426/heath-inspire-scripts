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
#VERBOSE = True

ALREADY_SEEN = {}

def find_records():
    """Find records that have raw string affilations."""

    atsearch = '100__v:/batavia/ or 700__v:/batavia/ \
or 100__v:/60510/ or 700__v:/60510/ \
#or 100__v:/jlab/ or 700__v:/JLAB/ \
#or 100__v:/slac/ or 700__v:/slac/ \
#or 100__v:/cern/ or 700__v:/cern/ \
-100__u:/\\w/ \
-700__u:/\\w/'
    print atsearch
    result = perform_request_search(p=atsearch, cc='HEP')
    result.reverse()
    result = result[:50]
    return result

def get_aff(aff):
    """Convert raw string affilation to INSPIRE form."""
    return bestmatch(aff, 'ICN')[0][1].split(';')


def create_xml(recid, tags):
    """Create xml file to replace to 100, 700 block."""

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
                if code == 'v':
                    try:
                        if VERBOSE:
                            print len(ALREADY_SEEN)
                        if not value in ALREADY_SEEN:
                            new_values = get_aff(value)
                            ALREADY_SEEN[value] = new_values
                        for new_value in ALREADY_SEEN[value]:
                            correct_subfields.append(('u', \
                                                     new_value.lstrip(' ')))
                        flag = True
                    except TypeError:
                        pass
                correct_subfields.append((code, value))
            record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                             subfields=correct_subfields)
    if flag:
        return print_rec(correct_record)

def main(recordlist):
    """Take input in terms or recid list or generate a list."""

    if not recordlist:
        recordlist = find_records()

    try:
        recordlist = [int(r) for r in recordlist]
    except TypeError:
        print "ERROR: bad recid given"
        return None

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    for record in recordlist:
        if VERBOSE > 0:
            print "doing %d" % (record)
        update = create_xml(record, ['100__', '700__'])
        if update:
            output.write(update)
    output.write('</collection>')
    output.close()
    print 'Number of affiliations:', len(ALREADY_SEEN)
    print filename


if __name__ == '__main__':
    RECIDS = sys.argv[1:]
    try:
        main(RECIDS)
    except KeyboardInterrupt:
        print 'Exiting'

