#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys

from invenio.search_engine import perform_request_search, get_fieldvalues, \
     get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field, record_xml_output
from invenio.intbitset import intbitset
from invenio.bibformat_engine import BibFormatObject


verbose = 0

def find_records_containing_email():
    atsearch = '100__m:/\@/ or 700__m:/\@/ and ac 1->20 -001:1254216'
    atsearch = '100__m:/\@/ or 700__m:/\@/ -001:1254216 -001:1189466 and ac 1->20'
    return perform_request_search(p=atsearch, cc='HEP')

def get_hepnames_recid_from_email(email):
    emailsearch = '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s'
    reclist = perform_request_search(p = \
        emailsearch % (email, email, email, email), cc='HepNames')
    if len(reclist) == 1:
        return reclist[0]
    elif len(reclist) > 1:
        if verbose:
            print "WARNING: more than one hepnames record found for %s: " % (email)
            print '\t' + ', '.join([str(r) for r in reclist])
    else:
        if verbose:
            print "WARNING: no hepnames record found for %s: " % (email)
        return None

def get_hepnames_anyid_from_recid(record, type):
    authorId = None
    for item in BibFormatObject(record).fields('035__'):
        if item.has_key('9') and item['9'] == type and item.has_key('a'):
            authorId = item['a']
    if verbose and not authorId:
        print "WARNING: no %s ID found for %s: " % (type, record)
    return authorId

def get_hepnames_affiliation_from_recid(record, type):
    affiliation = None
    for item in BibFormatObject(record).fields('371__'):
        if item.has_key('z') and item['z'].lower() == type.lower() and item.has_key('a'):
            affiliation = item['a']
    if verbose and not authorId:
        print "WARNING: no %s ID found for %s: " % (type, record)
    return affiliation



def find_inspire_id_from_record(record):
    authorId = get_hepnames_anyid_from_recid(record, 'INSPIRE')
    if verbose and not authorId:
        print "WARNING: no INSPIRE ID found for %s: " % (record)
    return authorId

def find_bai_from_record(record):
    authorId = get_hepnames_anyid_from_recid(record, 'BAI')
    if verbose and not authorId:
        print "WARNING: no BAI found for %s: " % (record)
    return authorId


def convert_email_to_inspire_id(email):
    id = None
    recid = get_hepnames_recid_from_email(email)
    if recid:
        id = find_inspire_id_from_record(recid) 
    return id        
            

def create_xml(recid, tags):
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
                if code == 'm':
                    new_value = convert_email_to_inspire_id(value)        
                    if new_value:
                        value = new_value
                        code = 'i'
                        flag = True
                correct_subfields.append((code, value))
            record_add_field(correct_record, tag[0:3], tag[3], tag[4], subfields=correct_subfields)
    if flag:
        return print_rec(correct_record)
    else:
        return None

def main(recordlist):
    if not recordlist:
        if verbose: print "scanning all HEP records ..."
        recordlist = find_records_containing_email()
        if verbose: print "%d records with '@' in author fields found" % len(recordlist)
    else:
        try:
            recordlist = [int(r) for r in recordlist]
        except:
            print "ERROR: bad recid given"
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    for record in recordlist:
        if verbose > 0: print "doing %d" % (record)     
        update = create_xml(record,['100__','700__'])
        if update: output.write(update)
    output.write('</collection>') 
    output.close()

if __name__ == '__main__':
    recids = sys.argv[1:]
    try:
        main(recids)
    except KeyboardInterrupt:
        print 'Exiting'
