# -*- coding: utf-8 -*-
"""
This module looks for duplicate names and bad IDs in HEPNames.
"""

import numpy
import re
import sys

from invenio.search_engine import get_collection_reclist
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_all_field_values
from invenio.intbitset import intbitset

#from invenio.bibauthorid_dbinterface \
#     import _select_from_aidpersoniddata_where
from invenio.dbquery import run_sql



from hep_convert_email_to_id import find_inspire_id_from_record, \
                                    bad_id_check, \
                                    get_hepnames_anyid_from_recid

LETTER = None
RECIDS_HEPN = get_collection_reclist('HepNames')
RECIDS_INST = get_collection_reclist('Institutions')
RECIDS_EXPT = get_collection_reclist('Experiments')

GOOD_IDENTIFIERS = set([x.lower() for x in ['ARXIV', 'BAI', 'CERN',
'DESY', 'GoogleScholar', 'INSPIRE', 'JACOW', 'KAKEN', 'ORCID',
'ResearcherID', 'SCOPUS', 'SLAC', 'Wikipedia']])


BAI_URL = 'https://inspirehep.net/author/manage_profile/'

def bad_identifiers():
    """Looks for bad 035__9 fields"""

    identifiers = set([y.lower() for y in
                       get_fieldvalues(RECIDS_HEPN, '035__9')])
    for identifier in identifiers - GOOD_IDENTIFIERS:
        search = '035__9:' + identifier
        result = perform_request_search(p=search, cc='HepNames')
        if not result:
            continue
        print search
        for recid in result:
            print 'https://inspirehep.net/record/' + str(recid)

def bad_orcid_bai():
    """Check ORCIDs have correct form in BAI."""

    #orcids = run_sql('select data from aidPERSONIDDATA where \
    #                  tag="extid:ORCID"')
    #for orcid in orcids:
    #    if not ORCID_REGEX.match(orcid[0]):
    #        print '"{0}"'.format(orcid[0])
    #badorcids = set()
    #pids = run_sql('select personid from aidPERSONIDDATA')
    #for pid in pids:
    #    orcid = _select_from_aidpersoniddata_where(select=['data'], \
    #            pid=pid[0], tag='extid:ORCID')
    #    try:
    #        orcid = orcid[0][0]
    #    except IndexError:
    #        orcid = None
    #    if orcid and not ORCID_REGEX.match(orcid):
    #        badorcids.add((pid[0], orcid))
    orcids = run_sql('select personid, data from aidPERSONIDDATA \
                      where tag="extid:ORCID"')
    for pid, orcid in orcids:
        if bad_id_check(orcid):
            print '{0}\t"{1}"'.format(BAI_URL + str(pid), orcid)

def check_ids(letter=None):
    """Go through HEPNames looking for bad IDs."""

    already_seen = {}
    duplicates = set()
    bad_id_set = set()
    fields = ['035__a', '035__z', '371__m']
    print 'check_ids: letter =', letter
    if letter:
        fields.append('100__a')

    for recid, field in [(recid, field) for recid in RECIDS_HEPN \
                                        for field in fields]:
        skip = False
        field_values = get_fieldvalues(recid, field)
        if field == '100__a':
            try:
                if not field_values[0].startswith(letter):
                    skip = True
            except IndexError:
                print "No name on record:", recid
        if not skip:
            for field_value in field_values:
                if field_value in already_seen:
                    duplicates.add(field + ':"' + field_value + '"')
                    continue
                already_seen[field_value] = field
                if bad_id_check(field_value):
                    bad_id_set.add(field + ':"' + field_value + '"')

    print "Duplicates"
    for duplicate in sorted(duplicates):
        if duplicate.startswith('100__a'):
            result = perform_request_search(p=duplicate, cc='HepNames')
            for recid in result:
                #name = duplicate.replace('100__a:"', '')
                #name = name.replace('"', '')
                print '{0:37s} {1:18s} {2:20s}'.\
                       format(duplicate, \
                         find_inspire_id_from_record(recid), \
                         get_hepnames_anyid_from_recid(recid, 'ORCID'))
        elif duplicate.startswith('035__a'):
            print duplicate
            #search = r'100__a:{0} or 700__a:{0}'.\
            #         format(duplicate.strip('035__a:'))
            search = r'100:{0} or 700:{0}'.\
                     format(duplicate.strip('035__a:'))
            result = perform_request_search(p=duplicate, cc='HEP')
            if len(result) > 0:
                print "Duplicate ID in HEP records"
                print "  ", search
        else:
            print duplicate


    print "Bad metadata"
    for bad_id in sorted(bad_id_set):
        print bad_id

    print "Bad ORCIDS in BAI"
    bad_orcid_bai()

    print "Finding new ORCIDs in HEP"
    new_orcids(already_seen)

def new_orcids(already_seen):
    """Search for new ORCIDs in HEP."""

    orcid_counter = 0
    fields = ('100__j', '700__j', '100__k', '700__k')
    for field in fields:
        for orcid in get_all_field_values(field):
            if not re.search('00-000', orcid):
                continue
            if not orcid.startswith('ORCID:'):
                search = field + ':' + orcid
                recid = perform_request_search(p=search, cc='HEP')
                if len(recid):
                    print 'Needs to start with "ORCID:"', recid, orcid
                continue
            orcid = orcid.replace('ORCID:', '')
            if bad_id_check(orcid):
                search = field + ':' + orcid
                recid = perform_request_search(p=search, cc='HEP')
                if len(recid):
                    print 'Bad ORCID', recid, orcid


    search = "{0}:ORCID:* or {1}:ORCID:* or {2}:ORCID:* \
              or {3}:ORCID:* 980:core".format(fields[0],
                  fields[1], fields[2], fields[3])
    search = "{0}:ORCID:* or {1}:ORCID:* or {2}:ORCID:* \
              or {3}:ORCID:* (037__c:hep-* or 037__c:nucl-* \
              or 037__c:math*)".format(fields[0],
                  fields[1], fields[2], fields[3])
    search = "{0}:ORCID:* or {1}:ORCID:* or {2}:ORCID:* \
              or {3}:ORCID:* 037__c:/^hep-[pt]h$/".format(fields[0],
                  fields[1], fields[2], fields[3])


    result = perform_request_search(p=search, cc='HEP')
    #search = "{0}:ORCID:* or {1}:ORCID:* or {2}:ORCID:* \
    #          or {3}:ORCID:*".format(fields[0],
    #              fields[1], fields[2], fields[3])
    #result = perform_request_search(p=search, cc='Fermilab')

    for recid, field in [(recid, field) for recid in result \
                                        for field in fields]:
        for orcid in get_fieldvalues(recid, field):
            if not orcid.startswith('ORCID:'):
                continue
            orcid = orcid.strip('ORCID:')
            if orcid in already_seen:
                continue
            if bad_id_check(orcid):
                print "Bad ORCID in HEP:", orcid
            already_seen[orcid] = recid
            print "http://inspirehep.net/record/{0}\thttp://orcid.org/{1}".\
                  format(str(recid), orcid)
            orcid_counter += 1
            #search = '001:' + str(recid) + ' 980:CORE'
            #if perform_request_search(p=search, cc='HEP'):
            #  print "http://inspirehep.net/record/{0}\thttp://orcid.org/{1}".\
            #      format(str(recid), orcid)
    print 'New orcids:', orcid_counter

def bad_url_z():
    """Check to make sure $$z field is correct."""

    field = '8564_z'
    good_values = set(['postprint', 'openaccess'])
    for value in get_all_field_values(field):
        search = field + ':' + value
        result = perform_request_search(p=search, cc='Fermilab')
        if len(result) == 0:
            continue
        if value in good_values:
            print value, len(result)
        else:
            print value, result

def bad_experiments_affilations():
    """Check to see bad metadata."""

    metadata = {'Institutions':{'HepNames':'371__a', 'Truth':'110__u'},
                'Experiments':{'HepNames':'693__e', 'Truth':'119__a'}}

    for aff in metadata:
        for value in numpy.setdiff1d(get_all_field_values(
                                     metadata[aff]['HepNames']),
                                     get_all_field_values(
                                     metadata[aff]['Truth'])):
            search = metadata[aff]['HepNames'] + ':"' + value + '"'
            result = perform_request_search(p=search, cc='HepNames')
            result = intbitset(result) & RECIDS_HEPN
            if len(result) > 0:
                if perform_request_search(
                p=metadata[aff]['Truth'] + ':"' + value + '"', cc=aff) == []:
                    print search, result


def main(input_value=None):
    """Runs the script, outputting to a file."""

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    print filename
    print 'main: letter =', input_value
    output = open(filename, 'w')
    sys.stdout = output
    bad_identifiers()
    check_ids(letter=input_value)
    #bad_experiments_affilations()
    bad_url_z()
    output.close()


if __name__ == '__main__':
    try:
        LETTER = str(sys.argv[1:][0]).upper()
    except IndexError:
        LETTER = None
    try:
        main(input_value=LETTER)
    except KeyboardInterrupt:
        print 'Exiting'



