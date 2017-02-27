# -*- coding: utf-8 -*-
"""
This module looks for duplicate names and bad IDs in HEPNames.
"""

import re
import sys

from invenio.search_engine import get_collection_reclist
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import perform_request_search
from invenio.bibauthorid_dbinterface \
     import _select_from_aidpersoniddata_where
from invenio.dbquery import run_sql



from hep_convert_email_to_id import find_inspire_id_from_record
from hep_convert_email_to_id import get_hepnames_anyid_from_recid

#EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@\.]+\w$")
EMAIL_REGEX = re.compile(r"^[\w\-\.\'\+]+@[\w\-\.]+\.\w{2,4}$")
ORCID_REGEX = re.compile(r'^0000-\d{4}-\d{4}-\d{3}[\dX]$')
INSPIRE_REGEX = re.compile(r'^INSPIRE-\d{8}$')
LETTER = None
RECIDS = get_collection_reclist('HepNames')
BAI_URL = 'https://inspirehep.net/author/manage_profile/'

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
        if not ORCID_REGEX.match(orcid):
            print '{0}\t"{1}"'.format(BAI_URL + str(pid), orcid)

def bad_id_check(id_num):
    """Check various IDs for correct format."""

    if id_num.startswith('INSP') and not \
       re.match(INSPIRE_REGEX, id_num):
        return True
    elif re.search(r'000\-', id_num) and not \
         re.match(ORCID_REGEX, id_num):
        return True
    elif re.search(r'\@', id_num) and not \
         re.match(EMAIL_REGEX, id_num):
        return True
    else:
        return False

def check_ids(letter=None):
    """Go through HEPNames looking for bad IDs."""

    already_seen = {}
    duplicates   = set()
    bad_id_set   = set()
    fields = ['035__a', '371__m']
    print letter
    if letter:
        fields.append('100__a')

    for recid, field in [(recid, field) for recid in RECIDS \
                                        for field in fields]:
        field_values = get_fieldvalues(recid, field)
        if field == '100__a' and not field_values[0].startswith(letter):
            continue
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
                print '{0:40s} {1:20s} {2:20s}'.\
                       format(duplicate, \
                         find_inspire_id_from_record(recid), \
                         get_hepnames_anyid_from_recid(recid, 'ORCID'))
        elif duplicate.startswith('035__a'):
            print duplicate
            search = r'100__a:{0} or 700__a:{0}'.\
                     format(duplicate.strip('035__a:'))
            result = perform_request_search(p=duplicate, cc='HEP')
            if len(result) > 0:
                print "Duplicate ID in HEP records"
                print "  ", search

    print "Bad metadata"
    for bad_id in sorted(bad_id_set):
        print bad_id

    print "Bad ORCIDS in BAI"
    bad_orcid_bai()

    print "Finding new ORCIDs in HEP"
    new_orcids(already_seen)

def new_orcids(already_seen):
    """Search for new ORCIDs in HEP."""

    fields = ('100__j', '700__j')
    search = "{0}:ORCID:* or {1}:ORCID:* 980:CORE".format(fields[0],
                                                          fields[1])
    result = perform_request_search(p=search, cc='HEP')
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


def main(input_value):
    """Runs the script, outputting to a file."""

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    print filename
    output = open(filename,'w')
    sys.stdout = output
    check_ids(input_value)
    output.close()


if __name__ == '__main__':
    try:
        LETTER = str(sys.argv[1:][0])
        main(LETTER.upper())
    except IndexError:
        main(None)
    except KeyboardInterrupt:
        print 'Exiting'



