#!/usr/bin/python
# -*- coding: utf-8 -*-

# import re
import sys
import os

from invenio.search_engine import perform_request_search, get_fieldvalues, \
     get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field, record_xml_output
from invenio.intbitset import intbitset
from hep_convert_email_to_id import find_inspire_id_from_record

VERBOSE = False
#VERBOSE = True

bad_experiments = ['CERN-LEP-DELPHI',
'BIGBOSS',
'BOREXINO',
'DAYA-BAY',
'ICARUS', 
'MEG',
'VERITAS',
'XENON']

experiments = ['AMANDA',
'AUGER',
#'BEPC-BES-III',
'BNL-RHIC-PHENIX',
'BNL-RHIC-PHOBOS', 
'BNL-RHIC-STAR',
'CDMS',
'CERN-LHC-ALICE',
'CERN-LHC-ATLAS',
'CERN-LHC-CMS', 
'CERN-LHC-LHCB',
'CERN-LHC-TOTEM',
#'CERN-NA-049',
#'CERN-NA-058',
#'CERN-NA-061', 
#'CERN-WA-096',
#'DESY-HERA-H1',
#'DESY-HERA-HERMES',
#'DESY-HERA-ZEUS',
#'FERMI-LAT', 
'FNAL-E-0740',
#'FNAL-E-0741',
'FNAL-E-0799',
'FNAL-E-0799',
'FNAL-E-0823', 
'FNAL-E-0823',
'FNAL-E-0830',
'FNAL-E-0832',
'FNAL-E-0871',
'FNAL-E-0875', 
'FNAL-E-0898',
'FNAL-E-0898',
'FNAL-E-0907',
'FNAL-E-0929',
'FNAL-E-0938',
'DES',
'FNAL-E-0954', 
'FNAL-E-0973',
'FNAL-E-0974',
'FNAL-E-0987',
'FNAL-T-0962',
#'FRASCATI-DAFNE-KLOE', 
#'FREJUS-NEMO-3',
#'GSI-FAIR-PANDA',
#'GSI-HADES',
'IceCube',
#'KAMLAND',
'KEK-BF-BELLE',
'KEK-BF-BELLE-II',
'KEK-T2K',
'LBNE',
#'LIGO',
#'MAGIC',
#'MAJORANA',
#'MICE',
#'OPERA', 
#'PAMELA',
#'PLANCK',
'SDSS',
'SLAC-PEP2-BABAR',
'SUPER-KAMIOKANDE',
#'TRIUMF-614', 
#'WASA-COSY'
]

#experiments = ['FNAL-E-0740', 'DES']
#experiments = ['FNAL-E-0740']

def get_hepnames_recid_from_search(search):
    reclist = perform_request_search(p = search, cc='HepNames')
    if len(reclist) == 1:
        return reclist[0]
    elif len(reclist) > 1:
        if VERBOSE:
            print "WARNING: more than one hepnames record found for %s: " % (search)
            print '\t' + ', '.join([str(r) for r in reclist])
        return None
    else:
        if VERBOSE:
            print "WARNING: no hepnames record found for %s: " % (search)
        return None

def convert_search_to_inspire_id(search):
    id = None
    recid = get_hepnames_recid_from_search(search)
    if recid:
        id = find_inspire_id_from_record(recid) 
    return id        
            

def create_xml(recid, tags, experiment):
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
                if code == 'a':
                    search = 'find a ' + value + ' and exp ' + experiment
                    new_value = convert_search_to_inspire_id(search)        
                    if new_value:
                        flag = True
                        correct_subfields.append(('i',new_value))
                correct_subfields.append((code, value))
            record_add_field(correct_record, tag[0:3], tag[3], tag[4], subfields=correct_subfields)
    #return print_rec(correct_record)
    if flag:
        #print print_rec(correct_record)
        return print_rec(correct_record)

def find_records_with_no_id(experiment):
   print experiment
   osearch = "find exp " + experiment + " and date > 2011"
   osearch = "find exp " + experiment
   #osearch = "693__e:fnal-e-0740 -693__e:fnal-e-0823 -693__:fnal-e-0741"
   oresult = perform_request_search(p=osearch, cc='HEP')
   psearch = '693__e:' + experiment + ' -100__i:INSPIRE* -700__i:INSPIRE*'
   if VERBOSE: print psearch
   presult = perform_request_search(p=psearch, cc='HEP')
   oresult = intbitset(oresult)
   presult = intbitset(presult)
   result = oresult & presult
   if VERBOSE: print len(result)
   result = result[:400]
   return result

def experiment_convert(experiment):
    i_count = 1
    recordlist = find_records_with_no_id(experiment)
    if recordlist:
        if VERBOSE: print experiment + ": %d records with no author ids found" % len(recordlist)
        fileName = 'tmp_hep_convert_experiment_to_id_' + experiment + '_correct.out'
        output = open(fileName,'w')
        for record in recordlist:
            if i_count > 20:
                break
            if VERBOSE > 0: print "%d doing %d" % (i_count, record)
            #print create_xml(record,['100__','700__'])
            #create_xml(record, ['100__','700__'], experiment)
            new_author_list = create_xml(record, ['100__','700__'], experiment)
            if new_author_list:
                output.write(new_author_list)
                output.write("\n")
                i_count += 1
        output.close()
        if (os.stat(fileName)[6] == 0) : os.unlink(fileName)
    else:
      if VERBOSE: print "No " + experiment + " records with no author ids found" 

def main(input):
    if not input:
        experiment_list = experiments
    else:
        try:
            experiment_list = input
        except:
            print "ERROR: bad input"
    for experiment in experiment_list:
        experiment_convert(experiment)

if __name__ == '__main__':
    experiments_input = sys.argv[1:]
    try:
        main(experiments_input)
    except KeyboardInterrupt:
        print 'Exiting'
