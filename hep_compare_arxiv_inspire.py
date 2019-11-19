'''
A script to get information from arXiv.
Based on
https://static.arxiv.org/static/arxiv.marxdown/0.1/help/api/
examples/python_arXiv_parsing_example.txt

'''

import feedparser
import getopt
import re
from time import sleep
import sys
import urllib

from invenio.bibrecord import print_rec,\
                              record_add_field

from invenio.search_engine import get_fieldvalues,\
                                  perform_request_search,\
                                  search_unit,

from hep_ads_xml_input import ARXIV_REGEX, ARXIV_REGEX_NEW

INPUT_FILE = 'tmp_hep_ads_xml_missing_eprint.out'
MAX_COUNT = 10
URL_BASE = 'http://export.arxiv.org/api/query?id_list='

def create_xml(input_dict):

    record = {}
    for tag in input_dict:
        subfields = [(9, 'arXiv'), ('a', input_dict[tag])]
        record_add_field(record, tag[0:3], tag[3], tag[4],
                         subfields=subfield)
    return print_rec(record)

def get_metadata_from_arxiv(eprint):
    '''Send metadata from arXiv.'''

    url = URL_BASE + eprint
    data = urllib.urlopen(url).read()

    feed = feedparser.parse(data)
    record = {}
    for entry in feed.entries:
        record['eprint'] = re.sub(r'v\d+$', '', entry.id.split('/abs/')[-1])
        record['269__c'] = entry.published.split('T')[0]
        record['246__a'] = entry.title
        try:
            record['500__a'] = entry.arxiv_comment
        except AttributeError:
            record['500__a'] = ''
        record['primarch'] = entry.arxiv_primary_category['term']
        record['520__a'] = entry.summary
        try:
            record['0247_a'] = entry.arxiv_doi
        except AttributeError:
            record['0247_a'] = ''
    for key, value in record.items():
        record[key] = re.sub(r'\s+', ' ', value)
    return record

def get_recid_from_inspire(id_string):

    if ARXIV_REGEX.match(id_string):
        field = '037__a:'
    elif ARXIV_REGEX_NEW.match(id_string):
        field = '037__a:'
        id_string = 'arXiv:' + id_string
    elif re.match(r'^10\.\d+/', id_string):
        field = '0247_a'
    elif id_string.isdigit():
        field = '001'
    search = field + ':"' + id_string + '"'
    result = perform_request_search(p=search, cc='HEP')
    if len(result) == 1:
        return (result[0], 'HEP')
    if len(result) > 1:
        print 'Duplicate: {0} {1}'.format(id_string, result)
        quit()
    result = search_unit(p=id_string, f=field, m='a')    
    if len(result) == 1:
        recid = result[0]
        return (recid, get_fieldvalues(recid, '980__a'))


def get_metadata_from_inspire(id_string):
    '''Get metadata from an INSPIRE record'''

    record = {}
    recid = get_recid_from_inspire(id_string)
    title = get_fieldvalues(recid, '245__a')[0]
    record['245__a'] = title
    return record

def compare_arxiv_inspire(arxiv, inspire):
    '''Compare arXiv and INSPIRE metadata.'''

    eprint_record = get_metadata_from_arxiv(arxiv)
    eprint_title = eprint_record['246__a'].lower()
    inspire_record = get_metadata_from_inspire(inspire)
    try:
        inspire_title = inspire_record['245__a'].lower()
    except TypeError:
        inspire_title = \
        '** NO INFORMATION IN INSPIRE for {0}'.format(inspire)
    inspire_title_base = re.sub(r'[\W_]', '', inspire_title)
    eprint_title_base = re.sub(r'[\W_]', '', eprint_title)
    if inspire_title_base == eprint_title_base:
        #return '{0} {1}\n{2}\n\n'.format(arxiv, 
        #        inspire, 'Titles are an exact match.')
        return None
    return '{0} {1}\nA: {2}\nI: {3}\n\n'.format(arxiv, inspire,
           eprint_title.capitalize(), inspire_title.capitalize())

def main(max_count=10):
    '''Get metadata for an eprint.'''

    print 'max_count =', max_count
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename, 'w')

    with open(INPUT_FILE) as file_h:
        for cnt, line in enumerate(file_h):
            match_obj = re.match(r'Need eprint: (\S+) (\S+)', line)
            eprint = match_obj.group(1)
            doi = match_obj.group(2)
            diff = compare_arxiv_inspire(arxiv=eprint, inspire=doi)
            if diff:
                output.write(diff)
            sleep(3)
            if cnt > max_count:
                break

    output.close()
    print filename

if __name__ == '__main__':

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 'c:')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    EPRINT = None
    for option, argument in OPTIONS:
        if option == '-c':
            MAX_COUNT = argument
            if not MAX_COUNT.isdigit():
                print '{0} is not a number'.format(MAX_COUNT)
                quit()
    try:
        main(int(MAX_COUNT))
    except KeyboardInterrupt:
        print 'Exiting'
