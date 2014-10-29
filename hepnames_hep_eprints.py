#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import unicodedata
import re
import sys

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import get_record
#from invenio.search_engine import get_all_field_values
#from invenio.bibformat_engine import BibFormatObject
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field 
#record_xml_output
from hep_convert_email_to_id import get_hepnames_recid_from_email


verbose = 0
list_of_authors = []
list_of_emails = []
inspire_to_arxiv = {'Astrophysics':'astro-ph', 'Experiment-HEP':'hep-ex', 'Gravitation and Cosmology':'gr-qc', 
'Lattice':'hep-lat', 'Math and Math Physics':'math', 'Theory-Nucl':'nucl-th', 'Phenomenology-HEP':'hep-ph',
'Theory-HEP':'hep-th', 'Experiment-Nucl':'nucl-ex'}


def find_records_to_check():
    search = '100__m:/\@/ or 700__m:/\@/ 980:CORE'
    #search = 'find tc t and date 2000->2009'
    #search = 'find cat jkemp or cleggm1 and primarch hep-ex and ac 1'
    #search = 'find fc g or fc l or fc n  and cat luba and date 2010->2014'
    return perform_request_search(p=search, cc='HEP')

#print '<?xml version="1.0" ?>'
#print '<collection>'

def handle_tags(recid, tags, d):
    record = get_record(recid)
    correct_record = {}
    need_email = False
    need_author = False

    for tag in tags:
        original_tag = tag
        field_instances = \
            record_get_field_instances(record, tag[0:3], tag[3], tag[4])
        correct_subfields = []
        #correct_subfields_aff = []
        for field_instance in field_instances:
            correct_record = {}
            correct_subfields = []
            for code, value in field_instance[0]:
                if code == 'm' or code == 'u':
                    tag = '371__'
                    if code == 'u': code = 'a'
                    if code == 'm' and not value in list_of_emails:
                        list_of_emails.append(value)
                        inHepnames_email = get_hepnames_recid_from_email(value)
                        if verbose: print 'inHepnames_email=', inHepnames_email
                        #if not inHepnames_email: need_email = value
                else:
                    tag = original_tag
                if tag == '700__' : tag = '100__'
                if code != 'v':
                    correct_subfields = [(code, value)]
                if  tag == '371__':
                    correct_subfields.append(('z', 'current'))
                if code == 'a' and tag == '100__' and not value in list_of_authors:              
                    list_of_authors.append(value)
                    nicename = re.sub(r'(.*)\, (.*)',r'\2 \1',value)                    
                    correct_subfields.append(('q', nicename))
                    search = "find a " + value
                    search = search + " or ea " + value
                    inHepnames_author = \
                        perform_request_search(p=search, cc='HepNames')
                    if verbose: print 'inHepnames_author=', inHepnames_author
                    if not inHepnames_author: need_author = True
                    if re.search(r"'",value): need_author = False
                if code == 'i' : need_author = False
                record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                    subfields=correct_subfields)
            if d:
                correct_record.update(d)
                if need_author or need_email:
                    if verbose and inHepnames_author:
                        print "Margaret: This author is already in", \
                               inHepnames_author, need_email
                    print print_rec(correct_record)
                    need_email = False
                    need_author = False
    return correct_record

def create_xml(recid):
    #new_author = {}
    #new_info = {}
    common_fields = {}
    common_tags = {}

    primarch = get_fieldvalues(recid,'65017a')
    if primarch: 
        primarch = primarch[0]
        for key in inspire_to_arxiv:
            if primarch == key:
                primarch = inspire_to_arxiv[key]
        common_tags['65017'] = [('2', 'INSPIRE'), ('a', primarch)]
    experiment = get_fieldvalues(recid,'693__e')
    if experiment: common_tags['693__'] = [('e', experiment[0])]
    advisor = get_fieldvalues(recid,'701__a')
    if advisor:  
        common_tags['701__'] = [('a', advisor[0]), ('g', 'PhD')]         
    thesis_aff = get_fieldvalues(recid,'502__c')
    thesis_year = get_fieldvalues(recid,'502__d')
    thesis_rank = get_fieldvalues(recid,'502__b')
    if thesis_rank == 'Master': thesis_rank = 'MAS'
    elif thesis_rank == 'Diploma': thesis_rank = 'UG'
    if thesis_aff and thesis_year and thesis_rank:
        common_tags['371__'] = [('a', thesis_aff[0]), ('r', thesis_rank[0]), ('t', thesis_year[0])]



    common_tags['670__'] = [('a', 'eprint')]
    common_tags['980__'] = [('a', 'HEPNAMES')]

    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    for tag_author in [['100__'], ['700__']]:
        handle_tags(recid, tag_author, common_fields)


def main(recordlist):
    if not recordlist:
        if verbose: print "scanning all HEP records ..."
        recordlist = find_records_to_check()
        if verbose: print "%d records with found" % len(recordlist)
    else:
        try:
            recordlist = [int(r) for r in recordlist]
        except:
            print "ERROR: bad recid given"
    for record in recordlist:
        if verbose > 0: print "doing %d" % (record)
        #print create_xml(record)
        create_xml(record)


if __name__ == '__main__':
    RECIDS = sys.argv[1:]
    try:
        main(RECIDS)
    except KeyboardInterrupt:
        print 'Exiting'

