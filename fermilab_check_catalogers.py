'''
Script for checking the work of catalogers regarding affiliations.
'''

import re

from invenio.search_engine import get_all_field_values,\
                                  perform_request_search,\
                                  get_fieldvalues

URL = 'https://inspirehep.net/record/edit/?ln=en#state=edit&recid='

def get_all_affs():
    '''Find all the ICNs'''

    return set(get_all_field_values('110__u'))

def find_bad_affs(cataloger, all_affs):
    '''Find bad affiliations in the work of a catalogers'''

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_' + cataloger + '.out', filename)
    output = open(filename, 'w')
    output.write('Records for {0}\n'.format(cataloger))
    search = 'find cat {0}'.format(cataloger)
    result = perform_request_search(p=search, cc='HEP')
    cataloger_affs = set()
    for recid in result:
        cataloger_affs = set()
        for aff in get_fieldvalues(recid, '100__u') + \
                   get_fieldvalues(recid, '700__u'):
            cataloger_affs.add(aff)
        if cataloger_affs - all_affs:
            output.write('{0}{1}\n'.format(URL, recid))
            for aff in cataloger_affs - all_affs:
                output.write('    {0}\n'.format(aff))
    output.close()
    print filename

def main():
    '''Find bad affiliations in the work of catalogers'''

    all_affs = get_all_affs()
    find_bad_affs('mcook', all_affs)
    find_bad_affs('teresa', all_affs)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
