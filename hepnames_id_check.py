# -*- coding: utf-8 -*-
"""
This module looks for duplicate names and bad IDs in HEPNames.
"""

import numpy
import re
import sys

from invenio.bibrecord import print_rec, record_add_field, \
                              record_get_field_instances
from invenio.search_engine import get_collection_reclist
from invenio.search_engine import get_fieldvalues, get_record
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_all_field_values
from invenio.intbitset import intbitset

#from invenio.bibauthorid_dbinterface \
#     import _select_from_aidpersoniddata_where


from invenio.dbquery import run_sql



from hep_convert_email_to_id import find_inspire_id_from_record, \
                                    bad_id_check, \
                                    get_hepnames_anyid_from_recid,\
                                    get_recid_from_id

from hepnames_id_check_import import CORE

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

def check_id(recid, already_seen, duplicates, bad_id_set):
    '''Check the IDs in a single record.'''

    for id_type in ('INSPIRE', 'ORCID', 'BAI'):
        idnum = get_hepnames_anyid_from_recid(recid, id_type)
        if not idnum:
            continue
        if bad_id_check(idnum):
            bad_id_set.add('Bad {0} on {1}: {2}'.format(id_type,
                                                        recid, idnum))
    for field in ('035__a', '035__z', '371__m'):
        field_values = get_fieldvalues(recid, field)
        for field_value in field_values:
            if field_value in already_seen:
                duplicates.add(field + ':"' + field_value + '"')
                continue
            already_seen[field_value] = field
            if bad_id_check(field_value):
                bad_id_set.add(field + ':"' + field_value + '"')
    return (already_seen, duplicates, bad_id_set)

def check_ids():
    """Go through HEPNames looking for bad IDs."""

    already_seen = {}
    duplicates = set()
    bad_id_set = set()

    for recid in RECIDS_HEPN:
        already_seen, duplicates, bad_id_set = \
        check_id(recid, already_seen, duplicates, bad_id_set)

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
    

def bad_inspire_id():
    '''Find bad INSPIRE IDs in HEP'''

    print 'Check for bad INSPIRE IDs in HEP'
    inspire_id_hep = set(get_all_field_values('100__i') + \
                     get_all_field_values('700__i'))
    id_hepnames = set(get_all_field_values('035__a'))
    bad_inspire_ids = inspire_id_hep - id_hepnames
    if not bad_inspire_ids:
        return None
    baddies = set()
    for bad_inspire_id in bad_inspire_ids:
        search = '100__i:"{0}" or 700__i:"{0}"'.format(bad_inspire_id)
        result = perform_request_search(p=search, cc='HEP')
        if not len(result):
            continue
        for recid in result:
            if bad_inspire_id in get_fieldvalues(recid, '100__i') + \
                                 get_fieldvalues(recid, '700__i'):
                baddies.add(search)
    if not len(baddies):
        return None
    for baddie in baddies:
        print baddie

def new_orcids(already_seen={}):
    """Search for new ORCIDs in HEP."""

    #check to see all ORCIDs in HEP are well-formed
    fields = ('100__j', '700__j', '100__k', '700__k')
    orcids_in_hep = {}
    bad_orcids = set()
    for field in fields:
        orcids_in_hep[field] = set(get_all_field_values(field))
        for orcid in orcids_in_hep[field]:
            if orcid in orcids_in_hep:
                continue
            if not re.search('00-000', orcid):
                continue
            if not orcid.startswith('ORCID:'):
                search = field + ':' + orcid
                recid = perform_request_search(p=search, cc='HEP')
                if len(recid):
                    print 'Needs to start with "ORCID:"', recid, orcid
                continue
            orcid = orcid.replace('ORCID:', '')
            if bad_id_check(orcid, 'ORCID'):
                search = field + ':' + orcid
                recid = perform_request_search(p=search, cc='HEP')
                if len(recid):
                    print 'Bad ORCID', recid, orcid

    #Check to see if there are any CORE ORCIDs not in HEPNames
    fields = fields[:2]
    all_identifiers = set(get_all_field_values('035__a'))
    search_core = CORE
    core = intbitset(perform_request_search(p=search_core, cc='HEP'))
    search = "{0}:ORCID:* or {1}:ORCID:*".format(fields[0], fields[1])
    result = intbitset(perform_request_search(p=search, cc='HEP'))
    result = result & core
    new_orcids = set()
    hepnames_to_add_dict = {}
    orcid_counter = 0
    for recid in result:
        record = get_record(recid)
        for (tag, field_instance) in \
                [(tag, field_instance) for tag in fields \
                 for field_instance in record_get_field_instances(record, \
                 tag[0:3], tag[3], tag[4])]:
            aff = author = email = orcid = None
            hepnames_recid = hepnames_orcid = None
            for code, value in field_instance[0]:
                #print recid, code, value
                if code == 'j' and value.startswith('ORCID:'):
                    orcid = value.strip('ORCID:')
                    if orcid in all_identifiers:
                        orcid = None
                        break
                    if orcid in new_orcids:
                        orcid = None
                        break
                    if get_recid_from_id(orcid):
                        orcid = None
                        break
                    new_orcids.add(orcid)
                elif code == 'a':
                    author = value
                elif code == 'i':
                    hepnames_recid = get_recid_from_id(value)
                    if not hepnames_recid:
                       print 'Bad INSPIRE ID on HEP record', recid, value
                       continue
                elif code == 'm':
                    hepnames_recid = get_recid_from_id(value)
                    email = value
                elif code == 'u':
                    aff = value
            if hepnames_recid:
                hepnames_orcid = get_hepnames_anyid_from_recid(recid, 'ORCID')
                if hepnames_orcid:
                    print "Mismatch:", recid, orcid, hepnames_orcid, \
                                       hepnames_recid
                    continue
            if orcid and author and hepnames_recid:
                print '*', recid, author, orcid, hepnames_orcid, hepnames_recid
                hepnames_to_add_dict[hepnames_recid] = orcid
            elif orcid and author:
                #This ORCID must be added by hand
                print "inspirehep.net/record/{0} orcid.org/{1}".format(
                      str(recid), orcid)
                print "  {0:30}{1:30}{2}".format(author, email, aff)
                orcid_counter += 1
                continue


    print 'New orcids:', orcid_counter
    orcids = len(hepnames_to_add_dict)
    if not orcids:
        return
    print 'Appending orcids:', orcids
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_orcids_append.out', filename)
    output = open(filename, 'w')
    for recid, orcid in hepnames_to_add_dict.items():
        record = {}
        record_add_field(record, '001', controlfield_value=str(recid))
        subfields = (('a', orcid), ('9', 'ORCID'), ('2', 'from HEP'))
        record_add_field(record, '035', '_', '_', subfields=subfields)
        output.write(print_rec(record))
    output.close()
    print filename
    

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


def main():
    """Runs the script, outputting to a file."""

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    print filename
    output = open(filename, 'w')
    sys.stdout = output
    bad_identifiers()
    bad_inspire_id()
    check_ids()
    #bad_experiments_affilations()
    #bad_url_z()
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'



