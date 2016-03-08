import re
import sys
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
#from hep_convert_email_to_id import get_hepnames_recid_from_email
from hep_convert_email_to_id import find_inspire_id_from_record
from invenio.search_engine import search_unit
from invenio.search_engine import get_collection_reclist
from invenio.intbitset import intbitset

VERBOSE = False
#VERBOSE = True
LETTER = 'G'

def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename,'w')
    sys.stdout = output
    hepnames_search_ids(LETTER)
    output.close()

def email_search(email):
    email_fields = '371__m:"{0}" or 371__o:"{0}"'
    email_fields += ' or 595__o:"{0}" or 595__m:"{0}"'
    return  email_fields.format(email)

def hepnames_search_ids(letter):
    name_letter = letter + '*'
    id_search = '035__9:bai or 035__9:inspire'
    id_search += ' or 035__9:orcid or 035__9:jacow'
    field_search_list = [['035__a', id_search, 'HepNames'],
                         ['371__m', r'/\@/', 'HepNames'],
                         ['371__m', r'/\,/', 'HepNames'],
                         ['100__a', r'/[\{\}\\]/', 'HepNames'],
                         ['100__a', name_letter, 'HepNames'],
                         ['100__j', r'*0000*', 'HEP'],
                         ['700__j', r'*0000*', 'HEP'],
                         #['541__a', r'*0000*', 'HEP'],
                         #['541__b', r'*\@*', 'HEP']
                        ]

    #field_search_list = [['100__a', name_letter, 'HepNames']]
    #field_search_list = [['541__a', r'*0000*', 'HEP'],
    #                     ['541__b', r'*\@*', 'HEP']]

    for field_search in field_search_list:
        examine(field_search)

def examine(field_search):
    field = field_search[0]
    search = field_search[1]
    collection = field_search[2]
    core = perform_request_search(p='980:CORE', cc='HEP')
    search_theory = 'find fc p or fc t or fc l or fc n or fc g 980:core'
    core = perform_request_search(p=search_theory, cc='HEP')
    if re.search(r'541.*', field):
        result = search_unit(p = search, m = 'a', f = field)
        #result = result & get_collection_reclist('HEP')
        result = result & intbitset(core)
    else:
        if not re.search(r'\:', search):
            search = field + ':' + search
        result = perform_request_search(p = search, cc = collection)
        if collection == 'HEP':
            result = intbitset(result) & intbitset(core)
    if VERBOSE:
        print 'VERBOSE', field, search, collection, len(result)
    already_seen_field_values = []
    for recid in result:
        recid_print = ""
        field_values = get_fieldvalues(recid, field)
        for field_value in field_values:
            bad_id = False
            if field_value in already_seen_field_values:
                continue
            if re.search(r'INSPIRE', field_value):
                inspire_form = r'^INSPIRE-\d{8}$'
                if not re.match(inspire_form, field_value):
                    print 'Bad INSPIRE ID: ', field_value
                    bad_id = True
            elif re.search(r'^0000-', field_value):
                orcid_form = r'^0000-\d{4}-\d{4}-\d{3}[\dX]$'
                if not re.match(orcid_form, field_value):
                    print 'Bad ORCID ID: ', field_value
                    bad_id = True
            search_dup = '{0}:"{1}"'.format(field, field_value)
            if field == '371__m' or field == '541__b':
                search_dup = email_search(field_value)
                if re.search(r"\'", field_value):
                    field_value_mod = \
                        re.sub(r"\'", r".", field_value)
                    search_dup = email_search(field_value_mod)
            elif collection == 'HEP':
#field == '541__a' or field == '100__j' \
#                                   or field == '700__j':
                ignore = r'(CCID|JACoW|uid|arxiv)'
                if re.search(ignore, field_value):
                    continue
                field_value = re.sub(r'^\w+:', r'', field_value)
                search_dup = '035__a:' + field_value
                #collection = 'HepNames'
            if collection == 'HEP':
#field == '541__a' or field == '541__b':
                recid_print = "http://inspirehep.net/record/" \
                              + str(recid) + "/export/xm"
            #print search_dup
            if field_value in already_seen_field_values:
                continue
            result_dup =  perform_request_search(p = search_dup,\
                              cc = 'HepNames')
            if len(result_dup) != 1 or bad_id:
                if field == '100__a':
                    for recid_dup in result_dup:
                        author_id = \
                            find_inspire_id_from_record(recid_dup)
                        print '{0:11d} {1:40s} {2:20s}'.\
                              format(recid_dup, field_value, author_id)
                else:
                    if len(result_dup) == 0:
                        print_field_value = field_value
                        if collection == 'HEP' and \
                               re.search(r'^0000-', field_value):
                            print_field_value = 'http://orcid.org/' + \
                                          field_value
                        print '{0:40s} {1:30s}'. \
                              format(print_field_value, recid_print)
                    else:
                        print search_dup, recid_print, result_dup, bad_id
                if field == '035__a':
                    author_search = r'100__a:"{0}" or 700__a:"{0}"'
                    search_hep = author_search.format(field_value)
                    result_hep = perform_request_search(p = search_hep,\
                        cc = 'HEP')
                    if len(result_hep) > 0:
                        print 'Bad ID in HEP', search_hep, \
                            len(result_hep)
            already_seen_field_values.append(field_value)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

