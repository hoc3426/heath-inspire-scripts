#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module adds INSPIRE IDs and ORCIDs to names in HEP records
for people on experimental collaborations.
"""


import sys
import os

from invenio.search_engine import perform_request_search, get_record, \
     get_fieldvalues
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field, record_get_field_value
from hep_convert_email_to_id import find_inspire_id_from_record, \
                                    get_hepnames_anyid_from_recid
from hep_convert_experiment_to_id_constants import EXPERIMENTS, \
                                                   VERBOSE, \
                                                   COUNT_MAX

def get_hepnames_recid_from_search(search):
    """Find recid in HEPNames from a search."""

    reclist = perform_request_search(p=search, cc='HepNames')
    if len(reclist) == 1:
        return reclist[0]
    elif len(reclist) > 1:
        if VERBOSE:
            print "WARNING: more than one hepnames record found for %s: " \
                  % (search)
            print '\t' + ', '.join([str(r) for r in reclist])
        return None
    else:
        if VERBOSE:
            print "WARNING: no hepnames record found for %s: " % (search)
        return None

def convert_search_to_inspire_id(search):
    """Convert a search to an INSPIRE ID."""

    inspire_id = None
    orcid = None
    recid = get_hepnames_recid_from_search(search)
    if recid:
        inspire_id = find_inspire_id_from_record(recid)
        orcid = get_hepnames_anyid_from_recid(recid, 'ORCID')
    return [inspire_id, orcid]


def create_xml(recid, tags, experiment, author_dict):
    """Create the new author list with IDs."""

    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    time_stamp = record_get_field_value(record, '005')
    record_add_field(correct_record, '005', controlfield_value=time_stamp)
    flag = None
    for tag in tags:
        field_instances = record_get_field_instances(record, tag[0:3],
                                                     tag[3], tag[4])
        correct_subfields = []
        for field_instance in field_instances:
            correct_subfields = []
            for code, value in field_instance[0]:
                if code == 'a':
                    if value not in author_dict:
                        search = 'find a ' + value + ' and exp ' + experiment
                        if VERBOSE:
                            print search
                        author_dict[value] = \
                           convert_search_to_inspire_id(search)
                        if VERBOSE:
                            print author_dict[value]
                    if author_dict[value][0]:
                        flag = True
                        correct_subfields.append(('i', author_dict[value][0]))
                    if author_dict[value][1]:
                        flag = True
                        orcid_value = 'ORCID:' + author_dict[value][1]
                        correct_subfields.append(('k', orcid_value))
                correct_subfields.append((code, value))
            record_add_field(correct_record, tag[0:3], tag[3], tag[4],
                             subfields=correct_subfields)
    #return print_rec(correct_record)
    if flag:
        #print print_rec(correct_record)
        return [print_rec(correct_record), author_dict]
    else:
        return [None, author_dict]

def find_records_with_no_id(experiment):
    """Find records in HEP that have no INSPIRE IDs or ORCIDs."""

    print experiment
    search = "693__e:" + experiment + " date:2010->2020"
    search += " -100__i:INSPIRE* -700__i:INSPIRE* \
                -100__j:ORCID* -700__j:ORCID* \
                -100__k:ORCID* -700__k:ORCID*"
    result = perform_request_search(p=search, cc='HEP')
    if VERBOSE:
        print len(result)
    clean_result = []
    for recid in result:
        if len(get_fieldvalues(recid, '693__e')) == 1:
            clean_result.append(recid)
    return clean_result

def experiment_convert(experiment):
    """Update the HEP entries for an experiment with author IDs."""

    i_count = 1
    author_dict = {}
    recordlist = find_records_with_no_id(experiment)
    if recordlist:
        if VERBOSE:
            print experiment + \
                  ": %d records with no author ids found" % len(recordlist)
        file_name = 'tmp_hep_convert_experiment_to_id_' + experiment + \
                   '_correct.out'
        output = open(file_name, 'w')
        for record in recordlist:
            if i_count > COUNT_MAX:
                break
            if VERBOSE > 0:
                print "%d doing %d" % (i_count, record)
            #print create_xml(record,['100__', '700__'])
            #create_xml(record, ['100__', '700__'], experiment)
            new_author_list = create_xml(record, ['100__', '700__'], \
                                         experiment, author_dict)
            if new_author_list[0]:
                output.write(new_author_list[0])
                output.write("\n")
                i_count += 1
            author_dict = new_author_list[1]
        output.close()
        if os.stat(file_name)[6] == 0:
            os.unlink(file_name)
    else:
        if VERBOSE:
            print "No " + experiment + " records with no author ids found"

def main(experiments_input):
    """Run the script."""

    if not experiments_input:
        experiment_list = EXPERIMENTS
    else:
        try:
            experiment_list = experiments_input
        except IOError:
            print "ERROR: bad input"
    for experiment in experiment_list:
        experiment_convert(experiment)

if __name__ == '__main__':
    EXPERIMENTS_INPUT = sys.argv[1:]
    try:
        main(EXPERIMENTS_INPUT)
    except KeyboardInterrupt:
        print 'Exiting'
