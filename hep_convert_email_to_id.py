#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module adds INSPIRE IDs and ORCIDs to names in HEP records
based on email addresses.
"""

import re
from sys import argv

from invenio.search_engine import perform_request_search, get_record, \
                                  search_unit
from invenio.bibrecord import print_rec, record_get_field_instances, \
                              record_add_field
from invenio.intbitset import intbitset
from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import get_collection_reclist

from hep_convert_email_to_id_input import RECIDS, SEARCH, VERBOSE

HN = get_collection_reclist('HepNames')

COUNTER_MAX = 100

def generate_check_digit(base_digits):
    '''
    Taken from https://github.com/tjwds/generate-orcid-checksum
    '''
    total = 0
    for digit in str(base_digits):
        total = (total + int(digit)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    if result == 10:
        result = "X"
    return result



def bad_id_check(id_num):
    """Check various IDs for correct format."""

    email_regex = re.compile(r"^[\w\-\.\'\+]+@[\w\-\.]+\.\w{2,4}$")
    bitnet_regex = re.compile(r"^[\w\-\.\'\+]+@[\w\-]+\.bitnet$")
    orcid_regex = re.compile(r'^0000-\d{4}-\d{4}-\d{3}[\dX]$')
    inspire_regex = re.compile(r'^INSPIRE-\d{8}$')

    if id_num.startswith('INSP') and not re.match(inspire_regex, id_num):
        return True
    elif re.search(r'000\-', id_num) and re.match(orcid_regex, id_num):
        base_digits = id_num.replace('-', '')[0:15]
        check_digit = id_num.replace('-', '')[15]
        if check_digit != str(generate_check_digit(base_digits)):
            return True
    elif re.search(r'000\-', id_num) and not re.match(orcid_regex, id_num):
        return True
    elif re.search(r'\@', id_num) and not \
         re.match(email_regex, id_num) and not \
         re.match(bitnet_regex, id_num):
        return True
    else:
        return False

def find_records_containing_email():
    """
    Searches for HEP records with emails
    """

    search = r'100__m:/\@/ or 700__m:/\@/'
    if SEARCH:
        search = SEARCH
    result = perform_request_search(p=search, cc='HEP')
    return sorted(result, reverse=True)

def get_hepnames_recid_from_email(email):
    """
    Find the HEPNames recid based on email
    """

#    emailsearch = '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s'
#    reclist = perform_request_search(p = \
#        emailsearch % (email, email, email, email), cc='HepNames', ap=-9)

    emailsearch = '371__m:%s or 371__o:%s'
    reclist = perform_request_search(p=emailsearch % (email, email),
                                     cc='HepNames')
    hidden_m = search_unit(email, f='595__m', m='a')
    hidden_o = search_unit(email, f='595__o', m='a')
    reclist_hidden = hidden_m or hidden_o & HN
    reclist = intbitset(reclist) or reclist_hidden

    if len(reclist) == 1:
        return reclist[0]
    elif len(reclist) > 1:
        if VERBOSE:
            print "WARNING: more than one hepnames record found for %s: " \
                  % (email)
            print '\t' + ', '.join([str(r) for r in reclist])
    else:
        if VERBOSE:
            print "WARNING: no hepnames record found for %s: " % (email)
        return None

def get_hepnames_anyid_from_recid(record, id_type):
    """
    Returns any id with a HEPNames recid
    """

    record = int(record)
    author_id = None
    for item in BibFormatObject(record).fields('035__'):
        if item.has_key('9') and item['9'] == id_type and item.has_key('a'):
            author_id = item['a']
    if VERBOSE and not author_id:
        print "WARNING: no %s ID found for %s: " % (id_type, record)
    return author_id

def get_hepnames_aff_from_recid(record, id_type):
    """
    Returns the current affiliation
    """

    record = int(record)
    affiliation = None
    for item in BibFormatObject(record).fields('371__'):
        if item.has_key('z') and item['z'].lower() == id_type.lower() \
                             and item.has_key('a'):
            affiliation = item['a']
    if VERBOSE and not affiliation:
        print "WARNING: no %s ID found for %s: " % (id_type, record)
    return affiliation



def find_inspire_id_from_record(recid):
    """
    Returns the INSPIRE ID of a HEPNames record
    """

    author_id = get_hepnames_anyid_from_recid(recid, 'INSPIRE')
    if VERBOSE and not author_id:
        print "WARNING: no INSPIRE ID found for %s: " % (recid)
    return author_id

def find_bai_from_record(record):
    """
    Returns the BAI of a HEPNames record
    """

    author_id = get_hepnames_anyid_from_recid(record, 'BAI')
    if VERBOSE and not author_id:
        print "WARNING: no BAI found for %s: " % (record)
    return author_id


def convert_email_to_inspire_id(email):
    """
    Returns the INSPIRE ID and the ORCID from an email
    """

    inspire_id = None
    orcid      = None
    recid = get_hepnames_recid_from_email(email)
    if recid:
        inspire_id = find_inspire_id_from_record(recid)
        orcid      = get_hepnames_anyid_from_recid(recid, 'ORCID')
    return [inspire_id, orcid]

def get_orcid_from_inspire_id(inspire_id):
    """
    Returns the INSPIRE ID and the ORCID from an INSPIRE ID
    """

    orcid = None
    recid = None
    search = '035__a:' + inspire_id
    result = perform_request_search(p=search, cc='HepNames')
    if len(result) == 1:
        recid = result[0]
    if recid:
        inspire_id = find_inspire_id_from_record(recid)
        orcid      = get_hepnames_anyid_from_recid(recid, 'ORCID')
    return [inspire_id, orcid]


def create_xml(recid, tags, author_dict):
    """
    Replaces an email with an INSPIRE ID and an ORCID where possible
    """

    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    flag = False
    flag_record = False
    for tag in tags:
        #print '1 flag_record, flag', flag_record, flag
        field_instances = record_get_field_instances(record, \
                                                     tag[0:3], tag[3], tag[4])
        #correct_subfields = []
        #seen_subfields = []
        for field_instance in field_instances:
            correct_subfields = []
            seen_subfields = []
            orcid_flag = False

            for code, value in field_instance[0]:
                if code == 'j' and value.startswith('ORCID') or code == 'k':
                    orcid_flag = True

            if orcid_flag:
                flag = False
                for code, value in field_instance[0]:
                    if code == 'm' and get_hepnames_recid_from_email(value):
                        #pass
                        correct_subfields.append(('9', 'email_known'))
                    #else:
                    correct_subfields.append((code, value))
                record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                                 subfields=correct_subfields)
                continue

            for code, value in field_instance[0]:
                if VERBOSE:
                    print 'code, value =', code, value
                new_value = [None, None]
                if code == 'm':
                    value = value.lower()
                if code == 'j' and value.startswith('ORCID') or code == 'k':
                    flag = False
                    continue
                elif code == 'm' and value not in author_dict:
                    if bad_id_check(value):
                        print 'Bad email:', recid, value
                        #quit()
                    try:
                        author_dict[value] = \
                            convert_email_to_inspire_id(value)
                    except KeyError:
                        print 'Problem with: ', value, \
                                    convert_email_to_inspire_id(value)
                        quit()
                    new_value = author_dict[value]
                    if author_dict[value][0] or author_dict[value][1]:
                        flag = True
                elif code == 'i' and value not in author_dict:
                    #flag = False
                    if bad_id_check(value):
                        print 'Bad INSPIRE ID:', value
                        #quit()
                    author_dict[value] = get_orcid_from_inspire_id(value)
                    new_value = author_dict[value]
                    if author_dict[value][1]:
                        flag = True
                    #print '1 flag', flag
                elif code == 'm' or code == 'i' :
                    try:
                        new_value = author_dict[value]
                    except KeyError:
                        print value
                        print author_dict[value]
                        quit()
                    if code == 'm' and new_value[0]:
                        flag = True
                    elif code == 'i' and new_value[1]:
                        flag = True
                    #print 'new_value, flag =', new_value, flag
                #print 'new_value =', new_value
                if new_value[0]:
                    value = new_value[0]
                    code = 'i'
                    if not (code, value) in seen_subfields:
                        correct_subfields.append((code, value))
                        seen_subfields.append((code, value))
                        #flag = True
                #print '2 flag', flag
                if new_value[1]:
                    value = 'ORCID:' + new_value[1]
                    code = 'k'
                    if not (code, value) in seen_subfields:
                        correct_subfields.append((code, value))
                        seen_subfields.append((code, value))
                    #flag = True
                #print '3 flag', flag
                if not (code, value) in seen_subfields:
                    correct_subfields.append((code, value))
                    seen_subfields.append((code, value))
                #print '4 flag', flag
            record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                     subfields=correct_subfields)
            if flag_record == False:
                flag_record = flag
    #print '2 flag_record, flag', flag_record, flag
    if flag_record:
        #return print_rec(correct_record)
        return [print_rec(correct_record), author_dict]
    else:
        #return None
        return [None, author_dict]

def main(recordlist):
    """Run the script."""

    if not recordlist:
        if VERBOSE:
            print "scanning all HEP records ..."
        recordlist = find_records_containing_email()
        if VERBOSE:
            print "%d records with '@' in author fields found" \
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
    author_dict = {}
    counter = 0
    for record in recordlist:
        if VERBOSE > 0:
            print "doing %d" % (record)
        #update = create_xml(record, ['100__', '700__'])
        update = create_xml(record, ['100__', '700__'], author_dict)
        if update[0] and counter < COUNTER_MAX:
            output.write(update[0])
            output.write('\n')
            counter += 1
        elif counter > COUNTER_MAX:
            break
        author_dict = update[1]
    output.write('</collection>')
    output.close()
    print "Number of email addresses:", len(author_dict)
    print filename

if __name__ == '__main__':

    if not RECIDS:
        RECIDS = argv[1:]
    try:
        main(RECIDS)
    except KeyboardInterrupt:
        print 'Exiting'
