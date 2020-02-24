"""
Script to add names to HEPNames, or append experiment tags.
"""

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import getopt
import re
import random
import sys

from invenio.search_engine import perform_request_search
from hep_convert_email_to_id import get_hepnames_recid_from_email, \
                                    get_recid_from_id
from invenio.bibrecord import print_rec, record_add_field

from hep_baiprofiledups import get_all_orcids
from hep_collaboration_authors import EMAIL_REGEX
from hepnames_add_from_list_email_to_aff import *
from hepnames_add_from_list_authors import AUTHORS, EMAILS, ORCIDS, \
                                           EXPERIMENT, SOURCE, INSPIRE

from hep_collaboration_authors import process_author_name, ORCID_REGEX 

def generate_inspire_ids(inspire):
    ''' Generate a list of INSPIRE IDs.'''

    for _ in range(2000):
        inspire_id = 'INSPIRE-00' + str(inspire) + str(random.randint(1, 9))
        print inspire_id
        inspire += 1

def orcid_lookup():
    '''Check to see if we have ORCIDs in HEPNames.'''

    for (name, orcid) in ORCIDS:
        if perform_request_search(p = '035:' + orcid, cc = 'HepNames'):
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
            result = perform_request_search(p = search, cc = 'HepNames')
            if len(result) == 0:
                print 'or', recid
        else:
            emails_unknown.append(email)
    for email in emails_unknown:
        print email
    quit()


def create_xml(author, email, affiliation, experiment, inspire_id, orcid,
               native_name):
    '''Create the xml file to upload.'''

    common_fields = {}
    common_tags = {}
    author2 = re.sub(r'(.*)\, (.*)', r'\2 \1', author)
    common_tags['980__'] = [('a', 'HEPNAMES')]
    common_tags['100__'] = [('a', author), ('q', author2), ('g', 'ACTIVE')]
    if affiliation:
        if isinstance(affiliation, (list,)):
            for aff in affiliation:
                common_tags['371__'] = [('m', email), ('a', aff),
                                        ('z', 'current')]
        else:
            common_tags['371__'] = [('m', email), ('a', affiliation),
                                    ('z', 'current')]
    else:
        common_tags['371__'] = [('m', email), ('z', 'current')]
    if experiment:
        common_tags['693__'] = [('e', experiment), ('z', 'current')]
    if orcid:
        common_tags['035__'] = [('9', 'ORCID'), ('a', orcid)]
    else:
        common_tags['035__'] = [('9', 'INSPIRE'), ('a', inspire_id)]
    if SOURCE:
        common_tags['670__'] = [('a', SOURCE)]
    if native_name:
        common_tags['880__'] = [('a', native_name)]
    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields = common_tags[key])
    #return common_fields
    return print_rec(common_fields)


def main(authors, inspire):
    '''Create a list of people to add to potentially HEPNames'''

    print "Experiment:", EXPERIMENT
    print "Starting INSPIRE", inspire
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '.out', filename)
    output = open(filename, 'w')

    filename_append = 'tmp_' + __file__ + '_append'
    filename_append = re.sub('.py', '.out', filename_append)
    output_append = open(filename_append, 'w')


    already_seen = set()
    for author_info in authors:
        author = email = orcid = None
        affiliation = native_name = None
        recid_email = recid_orcid = None
        author = author_info[0]
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
                print "Duplicate", value
                continue
            if not EMAIL_REGEX.match(value) and not \
            ORCID_REGEX.match(value):
                print('Bad format: {0}'.format(value))
            already_seen.add(value)
 
        if email:
            recid_email = get_hepnames_recid_from_email(email)
        if orcid:
            recid_orcid = get_recid_from_id(orcid)
        if recid_email and not recid_orcid and orcid:
            output_append.write('Need {0} on {1}'.format(orcid, recid_email))
        elif recid_orcid and not recid_email and email:
            output_append.write('Need {0} on {1}'.format(email, recid_orcid))
        if recid_email and recid_orcid and recid_email != recid_orcid:
            print('Mismatch {0} {1}  {2} {3}'.
                  format(email, recid_email, orcid, recid_orcid))
            continue
        recid = recid_email or recid_orcid
        if recid and EXPERIMENT == None:
            continue
        elif recid and EXPERIMENT:
            search = "001:" + str(recid) + " -693__e:" + EXPERIMENT
            if len(perform_request_search(p = search, cc = 'HepNames')) == 1:
                print 'or', recid
            continue
        #print 'email =', email
        if not affiliation:
            affiliation = aff_from_email(email)
        #print 'affiliation =', affiliation
        if False:
        #if affiliation == None:
            try:
                affiliation = author_info[4]
                affiliation = get_aff(affiliation)
            except IndexError:
                pass
        #print 'affiliation =', affiliation

        #if ", " not in author:
        #    author = re.sub(r'(.*) (\S+)', r'\2, \1', author)
        #author = author.replace(',', ', ')
        #author = re.sub(r'\s+', ' ', author)
        author = process_author_name(author)
        inspire_id = 'INSPIRE-00' + str(inspire) + \
                     str(random.randint(1, 9))
        output.write(create_xml(author, email, affiliation,
                                EXPERIMENT, inspire_id, orcid, native_name))
        output.write('\n')
        inspire += 1
    output.close()
    output_append.close()
    print "Next INSPIRE", inspire
    print filename
    print filename_append

if __name__ == '__main__':

    TEST = True
    TEST = False

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 't,v')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

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

