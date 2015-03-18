import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
#from hep_convert_email_to_id import get_hepnames_recid_from_email
from hep_convert_email_to_id import find_inspire_id_from_record

#this is a comment

VERBOSE = 1

def main():
    for counter in [1, 2, 3, 4]:
        hepnames_search_ids(counter)
        #pass
    name_duplicates('f')

def hepnames_search_ids(counter):
    list_of_ids = []
    if counter == 1:
        field = '035__a'
        search = field + ':INSPIRE*'
    elif counter == 2:
        field = '371__m'
        search = field + r':/\@/'
    elif counter == 3:
        field = '371__m'
        search = field + r':/\,/'
    elif counter == 4:
        field = '100__a'
        search = field + r':/[\{\}\\]/'
    if VERBOSE == 1:
        print search
    result = perform_request_search(p=search, cc='HepNames')
    for recid in result:
        if counter == 3:
            print 'https://inspirehep.net/record/' + str(recid)
        id_values = get_fieldvalues(recid, field)
        for id_value in id_values:
            search = field + ':' + id_value
            if counter == 1:
                if re.search(r'INSPIRE', id_value) and \
                   re.match(r'INSPIRE-\d{8}', id_value):
                    pass
                elif re.search(r'INSPIRE', id_value):
                    print 'Bad INSPIRE ID: ', id_value
            if counter == 2:
                email = id_value
                emailsearch = \
                            '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s'
                search = emailsearch % (email, email, email, email)
            if not id_value in list_of_ids:
                duplicate_id = perform_request_search(p=search, cc='HepNames')
                if len(duplicate_id) > 1 :
                    print search
                    if counter == 1:
                        search = '100__i:' + id_value + \
                                 ' or 700__i:' + id_value
                        hep_id_check = perform_request_search(p=search, \
                                                              cc='HEP')
                        if len(hep_id_check) > 1 :
                            print '  Multiple records -  (' + \
                                  str(len(hep_id_check)) + ') ' + search
                list_of_ids.append(id_value)


def name_duplicates(name):
    author_id = None
    author_name = None
    already_checked = []
    search = ''
    search = '100__a:' + name + '*'
    result = perform_request_search(p=search, cc='HepNames')
    for recid in result:
        author_name = get_fieldvalues(recid, '100__a')[0]
        if author_name not in already_checked:
            already_checked.append(author_name)
            search = 'find ea ' + author_name
            result2 = perform_request_search(p=search, cc='HepNames')
            if len(result2) > 1:
                for recid2 in result2:
                    author_id = find_inspire_id_from_record(recid2)
                    print '{0:11d} {1:40s} {2:20s}'.\
                          format(recid2, author_name, author_id)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

