#!/usr/bin/env python
# coding: utf-8
# TS 5/2018

import re
import sys
sys.path.insert(0, '/home/hoc/heath-inspire-scripts')

from invenio.dbquery import run_sql

from invenio.bibauthorid_dbinterface import get_name_by_bibref
#from invenio.search_engine import get_record
from invenio.bibcheck_task import AmendableRecord
from invenio.bibedit_utils import get_bibrecord
from invenio.search_engine import get_fieldvalues #, perform_request_search

from hep_convert_email_to_id import get_recid_from_id, \
                                    get_hepnames_anyid_from_recid

def show_papers(personid, external_id=None, orcid=None, inspire=None):
    search = 'select * from aidPERSONIDPAPERS where personid='
    search += str(personid) + ' and flag>-2'
    result = run_sql(search)
    hep_records = ''
    for personid, table, bibref, bibrec, author, match, flag, cul, date \
                       in result:
    #for personid, table, bibref, bibrec, author in result:
        #rec = AmendableRecord(get_bibrecord(bibrec))
        position = -1
        author_name = get_name_by_bibref((table, bibref))
        for key, value in AmendableRecord(get_bibrecord(bibrec)).\
                   iterfields(['{0}__%'.format(table, )]):
            if (key[0] == '700__a' or key[0] == '100__a') and \
                                            value == author_name:
                position = key[1]
        if position >= 0:
            for key, value in AmendableRecord(get_bibrecord(bibrec)).\
                   iterfields(['{0}__%'.format(table, )]):
                if key[1] == position and key[0] in \
                      ('{0}__a'.format(table), '{0}__i'.
                       format(table), '{0}__j'.format(table),
                       '{0}__k'.format(table), '{0}__m'.format(table), ):
                    if value.replace('ORCID:', '') == external_id and \
                       value.replace('ORCID:', '') != orcid and \
                       value != inspire:
                       hep_records += "    " + " ".join([str(bibrec),
                                                         author, value, '\n'])
    if hep_records:
        return hep_records
    return None

def find_dup_extid(extid='ORCID'):
    """
    Find profiles which share same external identifier
    """
    dups = run_sql('select personid, data from aidPERSONIDDATA where' +
                   ' tag="extid:{0}"'.format(extid) +
                   ' and data in (select data from aidPERSONIDDATA where' +
                   ' tag="extid:{0}"'.format(extid) +
                   ' group by data having count(*) > 1) order by data')
    return dups


def multiple_ids(extid="INSPIREID"):
    """
    Find profiles with multiple external IDs of same type
    """

    res = run_sql("""
    select personid, tag, data from aidPERSONIDDATA where personid in (
    select personid as c from aidPERSONIDDATA where tag="extid:{0}"
    group by personid having count(*) > 1) and tag <> "arxiv_papers"
    """.format(extid))

    return res


def create_report(filename='', extid='ORCID'):
    """
    Write list of profile info with identifier duplicates
    """
    if not filename:
        print('Must provide a filename for the report')
        return
    i = 0
    eidold = ''
    with open(filename, 'w') as output:
        for pid, eid in find_dup_extid(extid=extid):
            if eidold != eid and i > 1:
                output.write('-'*30 + "\n\n")
                eidold = eid
            output.write("https://inspirehep.net/author/profile/%s\n\n" % pid)
            author = orcid = inspire = None
            for tag, data in run_sql(
                             "select tag, data from aidPERSONIDDATA where" +
                             " personid={0} and tag <> 'arxiv_papers'".
                             format(pid)):
                recid = None
                if tag == 'canonical_name':
                    canonical_name = data
                    recid = get_recid_from_id(canonical_name)
                if recid:
                    #bai = get_hepnames_anyid_from_recid(recid, 'BAI')
                    orcid = get_hepnames_anyid_from_recid(recid, 'ORCID')
                    inspire = get_hepnames_anyid_from_recid(recid, 'INSPIRE')
                    author = get_fieldvalues(recid, '100__a')[0]
                output.write("{0}{1:18s}{2:22s}\n".\
                        format(' '*4, tag, data))
            output.write("{0}{1:20s}{2:20s}{3:20}\n".\
                     format('    HEPNames: ', orcid, inspire, author))
            hep_records = show_papers(pid, eid, orcid, inspire)
            if hep_records:
                output.write('\n    HEP records with wrong IDs\n')
                output.write(hep_records)
            #try:
            #    output.write(show_papers(pid, eid))
            #except TypeError:
            #    pass
            i += 1
            output.write("\n")


if __name__ == '__main__':


    FILENAME = 'tmp_' + __file__

    for id_type in ('ORCID', 'INSPIREID'):
        filename_id = re.sub('.py', '_' + id_type + '.out', FILENAME)
        create_report(filename=filename_id, extid=id_type)

        filename_id = re.sub('.py', '_multiple_' + id_type + '.out', FILENAME)
        with open(filename_id, 'w') as fhandle:
            oldpid = ''
            for row in multiple_ids(extid=id_type):
                if row[0] != oldpid:
                    fhandle.write("-" * 30)
                fhandle.write("{0}\t{1}\t{2}".format(*row) + '\n')
                oldpid = row[0]

    #oldpid = ''
    #for row in multiple_ids():
    #
    #    if row[0] != oldpid:
    #        print("-" * 30)
    #    print("{0}\t{1}\t{2}".format(*row))
    #    oldpid = row[0]

    #oldpid = ''
    #for row in multiple_ids(extid='ORCID'):
    #    if row[0] != oldpid:
    #        print("-" * 30)
    #    print("{0}\t{1}\t{2}".format(*row))
    #    oldpid = row[0]
