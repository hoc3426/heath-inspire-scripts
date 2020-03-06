#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module adds INSPIRE IDs and ORCIDs to names in HEP records
based on email addresses.
"""

import re
from sys import argv

from invenio.search_engine import perform_request_search, get_record, \
                                  search_unit, get_all_field_values
from invenio.bibrecord import print_rec, record_get_field_instances, \
                              record_add_field, record_get_field_value
from invenio.intbitset import intbitset
from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import get_collection_reclist

from hep_convert_email_to_id_input import RECIDS, SEARCH, VERBOSE

HN = get_collection_reclist('HepNames')

EMAILS_HEPNAMES = get_all_field_values('371__m') + \
         get_all_field_values('371__o') + \
         get_all_field_values('595__m') + \
         get_all_field_values('595__o')
EMAILS_HEPNAMES = set([email_hn.lower() for email_hn in EMAILS_HEPNAMES])
EMAILS_HEP = get_all_field_values('100__m') + get_all_field_values('700__m')

COUNTER_MAX = 400

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
    email_regex = re.compile(
        r"^[\w\-\.\'\+]+@[\w\-\.]+\.(\w{2,4}|email|canon)$")
    email_regex = re.compile(
        r"^(([^<>()\[\]\.,;:\s@\"]{1,64}(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@\[*(?!.*?\.\.)(([^<>()[\]\.,;\s@\"]+\.?)+[^<>()[\]\.,;\s@\"]{2,})\]?$")

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

    #emails = set()
    #recids = set()
    #for email in EMAILS_HEP:
    #    if email not in EMAILS_HEPNAMES:
    #        continue
    #    if email.startswith('email'):
    #        continue
    #    emails.add(email)
    #    search = "100__m:{0} or 700__m:{0}".format(email)
    #    result = perform_request_search(p=search, cc='HEP')
    #    if len(result) > 1:
    #        recids.update(result)
    #print recids
    #quit()

    search = r'100__m:/\@/ or 700__m:/\@/ \
                - \
               100__m:email* - 700__m:email*'
    search = r'100__m:/\w/ or 700__m:/\w/'
    if SEARCH:
        search = SEARCH
    result = perform_request_search(p=search, cc='HEP')
    result += perform_request_search(p=search, cc='Fermilab')
    result = set(result)
    print "Checking", len(result), "records"
    return sorted(result, reverse=True)




def get_hepnames_recid_from_email(email):
    """
    Find the HEPNames recid based on email
    """

    if email.lower() not in EMAILS_HEPNAMES:
        if VERBOSE:
            print "WARNING: no hepnames record found for %s: " % (email)
        return None

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
        return [r for r in reclist]
    else:
        if VERBOSE:
            print "WARNING: no hepnames record found for %s: " % (email)
        return None

def get_recid_from_id(id_number):
    ''' Get the recid corresponding to an ID number. '''

    search = '035__a:' + id_number
    result = perform_request_search(p=search, cc='HepNames')
    if len(result) == 1:
        return result[0]
    else:
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
    orcid = None
    recid = get_hepnames_recid_from_email(email)
    if str(recid).isdigit():
        inspire_id = find_inspire_id_from_record(recid)
        orcid = get_hepnames_anyid_from_recid(recid, 'ORCID')
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
        orcid = get_hepnames_anyid_from_recid(recid, 'ORCID')
    return [inspire_id, orcid]


def create_xml(recid, tags, author_dict):
    """
    Replaces an email with an INSPIRE ID and an ORCID where possible
    """

    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    time_stamp = record_get_field_value(record, '005')
    record_add_field(correct_record, '005', controlfield_value=time_stamp)
    flag = False
    for (tag, field_instance) in \
            [(tag, field_instance) for tag in tags \
             for field_instance in record_get_field_instances(record, \
             tag[0:3], tag[3], tag[4])]:
        correct_subfields = []
        derived_orcid = None
        derived_inspire_id = None
        inspire_id = None
        orcid_flag = False
        for code, value in field_instance[0]:
            if code == 'm' and value.startswith('email:'):
                author_dict[value] = (None, None)
            elif code == 'm' and not value in author_dict:
                value = value.lower()
                value2 = re.sub(r'[\,\.\;]$', '', value)
                if value != value2:
                    if VERBOSE:
                        print value, value2
                    value = value2
                    flag = True
                if bad_id_check(value):
                    print recid, value
                    (derived_inspire_id, derived_orcid) = \
                    (None, None)
                else:
                    (derived_inspire_id, derived_orcid) = \
                     convert_email_to_inspire_id(value)
                author_dict[value] = (derived_inspire_id, derived_orcid)
            if code == 'm':
                (derived_inspire_id, derived_orcid) = author_dict[value]
                if derived_inspire_id or derived_orcid:
                    value = 'email:' + value
            correct_subfields.append((code, value))
            if code == 'j' and value.startswith('ORCID') or code == 'k':
                orcid_flag = True
            elif code == 'i':
                inspire_id = value
        if inspire_id and not orcid_flag and not derived_orcid:
            derived_orcid = get_orcid_from_inspire_id(inspire_id)[1]
        if derived_orcid and not orcid_flag:
            derived_orcid = 'ORCID:' + derived_orcid
            correct_subfields.append(('k', derived_orcid))
            flag = True
        elif derived_inspire_id and not inspire_id and not orcid_flag:
            correct_subfields.append(('i', derived_inspire_id))
            flag = True
        record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
            subfields=correct_subfields)
    if flag:
        return [print_rec(correct_record), author_dict]
    else:
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
    output = open(filename, 'w')
    output.write('<collection>')
    author_dict = {}
    counter = 0
    for record in recordlist:
        if VERBOSE > 0:
            print "doing %d" % (record)
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
