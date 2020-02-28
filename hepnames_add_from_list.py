"""
Script to add names to HEPNames, or append experiment tags.
"""

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import csv
import getopt
import logging
import random
import re
import sys

from invenio.search_engine import perform_request_search, get_all_field_values
from hep_convert_email_to_id import get_hepnames_recid_from_email, \
                                    get_recid_from_id
from invenio.bibrecord import print_rec, record_add_field

from hep_collaboration_authors import EMAIL_REGEX
from hepnames_add_from_list_email_to_aff import aff_from_email
from hepnames_add_from_list_authors import AUTHORS, EMAILS, ORCIDS, \
                                           EXPERIMENT, SOURCE, INSPIRE

from hep_collaboration_authors import process_author_name, ORCID_REGEX

MIS_URL = 'https://inspirehep.net/search?cc=HepNames&p=find+recid+'
ORCID_REGEX_NODASH = re.compile(r'^\d{15}[\dX]$')

def get_all_orcids():
    '''Get all the ORCIDs in INSPIRE'''

    all_orcids = set()
    for value in get_all_field_values('035__a'):
        if ORCID_REGEX.match(value):
            all_orcids.add(value)
    return all_orcids

INSPIRE_ORCIDS = get_all_orcids()


def generate_inspire_ids(inspire):
    ''' Generate a list of INSPIRE IDs.'''

    for _ in range(2000):
        inspire_id = 'INSPIRE-00' + str(inspire) + str(random.randint(1, 9))
        print inspire_id
        inspire += 1

def orcid_lookup():
    '''Check to see if we have ORCIDs in HEPNames.'''

    for (name, orcid) in ORCIDS:
        if orcid in INSPIRE_ORCIDS:
            pass
        elif perform_request_search(p='035:' + orcid, cc='HepNames'):
            pass
        else:
            print name, '\t', orcid

def email_lookup():
    '''Check to see if we have email addresses in HEPNames.'''

    emails_unknown = []
    for email in EMAILS:
        recid = get_hepnames_recid_from_email(email)
        if recid and EXPERIMENT:
            search = '001:' + str(recid)  + ' 693__e:' + EXPERIMENT
            result = perform_request_search(p=search, cc='HepNames')
            if len(result) == 0:
                print 'or', recid
        else:
            emails_unknown.append(email)
    for email in emails_unknown:
        print email
    quit()


def create_xml(recid=None, author=None, email=None, affiliation=None,
               inspire_id=None, orcid=None, native_name=None):
    '''Create the xml file to upload.'''

    record = {}
    common_tags = {}
    if recid:
        record_add_field(record, '001', controlfield_value=str(recid))
    else:
        common_tags['980__'] = [('a', 'HEPNAMES')]
        if SOURCE:
            common_tags['670__'] = [('a', SOURCE)]
    if author:
        author2 = re.sub(r'(.*)\, (.*)', r'\2 \1', author)
        common_tags['100__'] = [('a', author), ('q', author2), ('g', 'ACTIVE')]
    if affiliation and email:
        if isinstance(affiliation, (list,)):
            for aff in affiliation:
                common_tags['371__'] = [('m', email), ('a', aff),
                                        ('z', 'current')]
        else:
            common_tags['371__'] = [('m', email), ('a', affiliation),
                                    ('z', 'current')]
    elif email:
        common_tags['371__'] = [('m', email), ('z', 'current')]
    if EXPERIMENT:
        common_tags['693__'] = [('e', EXPERIMENT), ('z', 'current')]
    if orcid:
        common_tags['035__'] = [('9', 'ORCID'), ('a', orcid)]
    elif inspire_id:
        common_tags['035__'] = [('9', 'INSPIRE'), ('a', inspire_id)]
    if native_name:
        common_tags['880__'] = [('a', native_name)]
    for key in common_tags:
        tag = key
        record_add_field(record, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    #return record
    return print_rec(record)

def get_authors(filename):
    '''Read spreadsheet and convert it to a dictionary for the authors.'''

    with open(filename, 'r') as csvfile:
        csvfile.seek(0)
        reader = csv.reader(csvfile)
        author_lines = list(reader)
    return author_lines


def main(authors, inspire):
    '''Create a list of people to add to potentially HEPNames'''

    print "Experiment:", EXPERIMENT
    print "Starting INSPIRE", inspire


    logfile = 'tmp_' + __file__
    logfile = re.sub('.py', '.log', logfile)
    logging.basicConfig(filename=logfile, filemode='w',
                    format='%(message)s',
                    level=logging.INFO)

    filename = 'tmp_' + __file__
    filename_insert = re.sub('.py', '_insert.out', filename)
    output_insert = open(filename_insert, 'w')
    filename_append = re.sub('.py', '_append.out', filename)
    output_append = open(filename_append, 'w')


    already_seen = set()
    for author_info in authors:
        author = email = orcid = inspire_id = None
        affiliation = native_name = None
        recid_email = recid_orcid = None
        author = author_info[0]
        author = process_author_name(author)
        for element in author_info[1:]:
            if '@' in element:
                email = element
            elif element.startswith('000'):
                orcid = element
            else:
                try:
                    element.decode('ascii')
                except UnicodeDecodeError:
                    native_name = element
                else:
                    affiliation = element
        for value in (email, orcid):
            if not value:
                continue
            if value in already_seen:
                logging.warn('Duplicate {0}'.format(value))
                continue
            if not any([EMAIL_REGEX.match(value), ORCID_REGEX.match(value)]):
                if ORCID_REGEX_NODASH.match(value):
                    possible_orcid = '-'.join(value[i:i+4]
                                     for i in range(0, len(value), 4))
                    logging.warn('''Dashless ORCID: {0}
  {1}
  https://orcid.org/{2}'''.\
                          format(value, author, possible_orcid))
                else:
                    logging.warn('Bad format: {0}'.format(value))
            already_seen.add(value)
        if affiliation:
            affiliation = get_aff(affiliation)
        elif email:
            affiliation = aff_from_email(email)
        if email:
            recid_email = get_hepnames_recid_from_email(email)
        if orcid:
            recid_orcid = get_recid_from_id(orcid)
        if recid_email and not recid_orcid and orcid:
            output_append.write(create_xml(recid=recid_email, orcid=orcid))
            output_append.write('\n')
        elif recid_orcid and not recid_email and email:
            output_append.write(create_xml(recid=recid_orcid, email=email,
                                           affiliation=affiliation))
            output_append.write('\n')
        if recid_email and recid_orcid and recid_email != recid_orcid:
            logging.warn('{0}{1}+or+{2}&of=hd'.
                  format(MIS_URL, recid_email, recid_orcid))
            continue
        recid = recid_email or recid_orcid
        if recid and EXPERIMENT == None:
            continue
        elif recid:
            search = "001:" + str(recid) + " -693__e:" + EXPERIMENT
            if len(perform_request_search(p=search, cc='HepNames')) == 1:
                print 'or', recid
            continue
        if not affiliation:
            affiliation = aff_from_email(email)
        else:
            affiliation = get_aff(affiliation)
        if not orcid:
            inspire_id = 'INSPIRE-00' + str(inspire) + \
                         str(random.randint(1, 9))
        output_insert.write(create_xml(author=author, email=email,
                                       affiliation=affiliation,
                                       inspire_id=inspire_id,
                                       orcid=orcid, native_name=native_name))
        output_insert.write('\n')
        inspire += 1
    output_insert.close()
    output_append.close()
    print "Next INSPIRE", inspire
    print filename_insert
    print filename_append
    print logfile


if __name__ == '__main__':

    INPUT_FILE = None
    TEST = False

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 'f:t')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    for option, argument in OPTIONS:
        if option == '-f':
            INPUT_FILE = argument
            AUTHORS = get_authors(INPUT_FILE)
        if option == '-t':
            TEST = True

    if TEST:
        def get_aff(aff):
            """Does nothing to affiliation."""
            return [aff]
    else:
        from hep_aff import get_aff

    try:
        main(AUTHORS, INSPIRE)
    except KeyboardInterrupt:
        print 'Exiting'

