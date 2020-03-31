'''
Script for checking the work of catalogers regarding affiliations.
'''

import re

from invenio.search_engine import get_collection_reclist, \
                                  perform_request_search,\
                                  get_fieldvalues
                                   
CATALOGERS = ['mcook', 'teresa', 'karin', 'carnold', 'fnalspi4', 'xml']
URL = 'https://old.inspirehep.net/record/edit/?ln=en#state=edit&recid='
URL_XML = 'https://inspirehep.net/record/'

CASE_MIXUPS = ['BeiHang U.', 'NIKHEF, Amsterdam']

def get_all_affs():
    '''Find all the ICNs'''

    #all_affs = set(get_all_field_values('110__u'))
    #all_affs.add('Nikhef, Amsterdam')
    recids = get_collection_reclist('Institutions')
    all_affs = set()
    for recid in recids:
        all_affs.add(get_fieldvalues(recid, '110__u')[0])
    for aff in CASE_MIXUPS:
        all_affs.add(aff)
    return all_affs

ALL_AFFS = get_all_affs()

def find_xml_papers():
    '''Find all the papers that use an authors.xml file'''

    search = 'find cn alice or atlas or cms or lhcb or cdf or d0 or \
              bessiii or auger and ac 100+'
    result = perform_request_search(p=search, cc='HEP')
    return set(result)

def find_bad_affs(cataloger, xml_papers):
    '''Find bad affiliations in the work of a catalogers'''

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_' + cataloger + '.out', filename)
    output = open(filename, 'w')
    output.write('Records for {0}\n'.format(cataloger))
    if cataloger == 'xml':
        result = xml_papers
        url = URL_XML
    else:
        url = URL
        search = 'find cat {0}'.format(cataloger)
        result = perform_request_search(p=search, cc='HEP')
        result = set(result) - xml_papers
    cataloger_affs = set()
    for recid in sorted(result, reverse=True):
        cataloger_affs = set()
        for aff in get_fieldvalues(recid, '100__u') + \
                   get_fieldvalues(recid, '700__u'):
            cataloger_affs.add(aff)
        bad_affs = cataloger_affs - ALL_AFFS
        if bad_affs:
            output.write('{0}{1}\n'.format(url, recid))
            if cataloger == 'xml':
                collaboration = get_fieldvalues(recid, '710__g')                
                output.write('{0}\n'.format(', '.join(collaboration)))
            for aff in bad_affs:
                if perform_request_search(p='100__u' + aff, cc='Institutions'):
                    ALL_AFFS.add(aff)
                    continue
                output.write('    {0}\n'.format(aff))
    output.close()
    print filename

def main():
    '''Find bad affiliations in the work of catalogers'''

    for cataloger in CATALOGERS:
        find_bad_affs(cataloger, find_xml_papers())

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
