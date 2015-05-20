import re
import sys
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
#from hep_convert_email_to_id import get_hepnames_recid_from_email
from hep_convert_email_to_id import find_inspire_id_from_record
from invenio.search_engine import search_unit

#this is a comment

VERBOSE = False
#VERBOSE = True

def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    orig_stdout = sys.stdout
    output = open(filename,'w')
    sys.stdout = output
    
    #for counter in [1, 2, 3, 4]:
    for counter in range(1, 9):
        hepnames_search_ids(counter)
        #pass
    name_duplicates('P')

    output.close()


def hepnames_search_ids(counter):
    list_of_ids = []
    collection = 'HepNames'
    if counter == 1:
        field = '035__a'
        search = '035__9:bai or 035__9:inspire or 035__9:orcid or 035__9:jacow'
    elif counter == 2:
        field = '371__m'
        search = field + r':/\@/'
    elif counter == 3:
        field = '371__m'
        search = field + r':/\,/'
    elif counter == 4:
        field = '100__a'
        search = field + r':/[\{\}\\]/'
    elif counter == 5:
        collection = 'HEP'
        field = '100__j'
        search = field + r':/\d/'
    elif counter == 6:
        collection = 'HEP'
        field = '700__j'
        search = field + r':/\d/'
    elif counter == 7:
        collection = 'HEP'
        field = '541__a'
        search = r'*0000*'
    elif counter == 8:
        collection = 'HEP'
        field = '541__m'
        search = r'/\@/'
    original_field = field
    result = perform_request_search(p=search, cc=collection)
    if re.search(r'541.*', field):
        result = search_unit(p = search, m = 'a', f = field)
    if VERBOSE:
        print "search = %s field = %s collection = %s result = %d" \
              % (search, field, collection, len(result))
    for recid in result:
        if counter == 3:
            print 'https://inspirehep.net/record/' + str(recid)
        id_values = get_fieldvalues(recid, field)
        for id_value in id_values:
            if re.search(r'(CCID|JACoW|uid)', id_value):
                continue
            search = field + ':' + id_value
            if counter == 1:
                if re.search(r'INSPIRE', id_value) and \
                   re.match(r'INSPIRE-\d{8}', id_value):
                    pass
                elif re.search(r'INSPIRE', id_value):
                    print 'Bad INSPIRE ID: ', id_value
            if counter == 2 or counter == 8:
                email = id_value
                emailsearch = \
                            '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s'
                search = emailsearch % (email, email, email, email)
            if counter == 5 or counter == 6 or counter == 7 or counter == 8:
                search = '035__a:' + id_value
                search = re.sub(r'ORCID:', r'', search)
                search = re.sub(r'orcid:', r'', search)
            if not id_value in list_of_ids:
                if VERBOSE:
                    print search
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
                elif len(duplicate_id) == 0:
                    id_value_stripped = re.sub(r'orcid:', r'', id_value)
                    id_value_stripped = re.sub(r'ORCID:', r'', id_value_stripped)
                    if VERBOSE:
                        print id_value, id_value_stripped
                    #print '%6s:%24s' % (original_field, id_value)
                    print '%-6s:%-25s  035__ $$9ORCID$$a%-16s  https://inspirehep.net/record/%s/export/hm  http://orcid.org/%s' % (original_field, id_value, id_value_stripped, recid, id_value_stripped)
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

