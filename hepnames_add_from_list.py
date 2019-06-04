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

from hepnames_add_from_list_email_to_aff import *
from hepnames_add_from_list_authors import AUTHORS, EMAILS, ORCIDS, \
                                           EXPERIMENT, SOURCE, INSPIRE

from hep_collaboration_authors import process_author_name 

#EXPERIMENT = 'FNAL-E-0974'
#EXPERIMENT = 'AUGER'
#EXPERIMENT = 'BNL-RHIC-STAR'
#EXPERIMENT = 'DUNE'
#EXPERIMENT = 'GERDA'
#EXPERIMENT = 'EXO-200'
#EXPERIMENT = 'PEN'
#EXPERIMENT = 'PADME'
#EXPERIMENT = 'XENON1T'
#EXPERIMENT = 'Baby-MIND'
#EXPERIMENT = 'HARPO'
#EXPERIMENT = None
#EXPERIMENT = 'WiggleZ'
#EXPERIMENT = 'DUNE'
#EXPERIMENT = 'HAWC'
#EXPERIMENT = 'KATRIN'
#EXPERIMENT = 'SUPER-KAMIOKANDE'
#EXPERIMENT = None
#EXPERIMENT = 'DES'


#SOURCE = 'Fermilab'
#SOURCE = 'HARPO'
#SOURCE = 'WiggleZ'
#SOURCE = 'Fermilab'
#SOURCE = 'HAWC'
#SOURCE = 'Fermilab'
#SOURCE = 'KATRIN'
#SOURCE = 'SUPER-KAMIOKANDE'
#SOURCE = 'DES'

#INSPIRE = 72053
#INSPIRE = 72499
#INSPIRE = 72524
#INSPIRE = 73359
#INSPIRE = 73383
#INSPIRE = 73787
#INSPIRE = 74388
#INSPIRE = 76741
#INSPIRE = 78756
#INSPIRE = 78849
#INSPIRE =  78890
#INSPIRE =  78916
#INSPIRE =  78935

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
        if recid:
            search = '001:' + str(recid)  + ' 693__e:' + EXPERIMENT
            result = perform_request_search(p = search, cc = 'HepNames')
            if len(result) == 0:
                print 'or', recid
        else:
            emails_unknown.append(email)
    for email in emails_unknown:
        print email
    quit()


def create_xml(author, email, affiliation, experiment, inspire_id, orcid):
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
    common_tags['035__'] = [('9', 'INSPIRE'), ('a', inspire_id)]
    if orcid:
        common_tags['035__'] = [('9', 'ORCID'), ('a', orcid)]
    if SOURCE:
        common_tags['670__'] = [('a', SOURCE)]

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
    emails = set()
    orcids = set()
    for author_info in authors:
        #print author_info
        author = author_info[0]
        email = author_info[1]
        email = email.lower()
        try:
            orcid = author_info[2]
        except IndexError:
            orcid = None
        if email in emails and email:
            print "Duplicate", email
            continue
        else:
           emails.add(email)
        if orcid in orcids and orcid:
            print "Duplicate", orcid
            continue
        else:
           orcids.add(orcid)
        recid = get_hepnames_recid_from_email(email)
        if not recid and orcid:
            recid = get_recid_from_id(orcid)
        if recid and EXPERIMENT == None:
            continue
        elif recid and EXPERIMENT:
            search = "001:" + str(recid) + " -693__e:" + EXPERIMENT
            if len(perform_request_search(p = search, cc = 'HepNames')) == 1:
                print 'or', recid
            continue
        #print 'email =', email
        affiliation = aff_from_email(email)
        #print 'affiliation =', affiliation
        if False:
        #if affiliation == None:
            try:
                affiliation = author_info[2]
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
                                EXPERIMENT, inspire_id, orcid))
        output.write('\n')
        inspire += 1
    output.close()
    print "Next INSPIRE", inspire
    print filename

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

