'''
A script to get information from arXiv.
Based on
https://static.arxiv.org/static/arxiv.marxdown/0.1/help/api/
examples/python_arXiv_parsing_example.txt

'''

import feedparser
import getopt
import logging
import re
import sys
import textwrap
from time import sleep
import urllib

from invenio.bibrecord import print_rec, record_add_field

from invenio.search_engine import get_fieldvalues, search_unit

from hep_ads_xml_input import ARXIV_REGEX, ARXIV_REGEX_NEW
from hep_compare_arxiv_inspire_input import IGNORE_EPRINTS

LOGFILE = 'tmp_' + __file__
LOGFILE = re.sub('.py', '.log', LOGFILE)
logging.basicConfig(filename=LOGFILE, filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

INPUT_FILE = 'tmp_hep_ads_xml_missing_eprint.in'
MAX_COUNT = 10
URL_BASE = 'http://export.arxiv.org/api/query?id_list='
DOI_REGEX = re.compile(r'^10.\d{4,9}/\S+$')

def clean_eprint(eprint):
    '''Remove possible prefix from eprint.'''

    regex = re.compile('^arxiv:', re.I)
    return regex.sub('', eprint)

def create_xml(recid, input_dict):
    '''Create marcxml file from.'''

    record = {}
    record_add_field(record, '001', controlfield_value=str(recid))

    eprint = input_dict['eprint']
    input_dict['035__a'] = 'oai:arXiv.org:' + eprint
    input_dict['037__a'] = eprint
    if ARXIV_REGEX_NEW.match(eprint):
        input_dict['037__a'] = 'arXiv:' + eprint

    for tag in input_dict:
        if tag in ('eprint', 'primarch', '0247_a'):
            continue
        if tag.startswith('65017a'):
            class_number = 2
        else:
            class_number = 9
        subfields = []
        if tag != '269__c':
            subfields.append((class_number, 'arXiv'))
        subfields.append((tag[5], input_dict[tag]))
        if tag == '037__a':
            subfields.append(('c', input_dict['primarch']))
        record_add_field(record, tag[0:3], tag[3], tag[4],
                         subfields=subfields)
    return print_rec(record)

def get_metadata_from_arxiv(eprint):
    '''Send metadata from arXiv.'''

    sleep(3)
    url = URL_BASE + eprint
    data = urllib.urlopen(url).read()

    feed = feedparser.parse(data)
    record = {}
    for entry in feed.entries:
        record['eprint'] = eprint
        record['269__c'] = entry.published.split('T')[0]
        record['246__a'] = entry.title
        record['primarch'] = entry.arxiv_primary_category['term']
        for category in [tag['term'] for tag in entry.tags]:
            if re.search(r'\d', category):
                continue
            record['65017a' + category] = category
        try:
            record['500__a'] = entry.arxiv_comment
        except AttributeError:
            pass
        try:
            record['520__a'] = entry.summary
        except AttributeError:
            pass
        try:
            record['0247_a'] = entry.arxiv_doi
        except AttributeError:
            pass
    for key, value in record.items():
        if isinstance(value, str):
            record[key] = textwrap.fill(re.sub(r'\s+', ' ', value))

    return record

def get_recid_from_inspire(id_string):
    '''
    Takes an ID string and returns an INSPIRE recid or it returns None.
    '''

    id_string = str(id_string)
    id_string = clean_eprint(id_string)
    if ARXIV_REGEX.match(id_string):
        field = '037__a'
    elif ARXIV_REGEX_NEW.match(id_string):
        field = '037__a'
        id_string = 'arXiv:' + id_string
    elif DOI_REGEX.match(id_string):
        field = '0247_a'
    elif id_string.isdigit():
        field = '001'
    else:
        logging.info('Unknown ID: ' + id_string)
        return False
    result = search_unit(p=id_string, f=field, m='a')
    if len(result) > 1:
        print 'Duplicate: {0} {1}'.format(id_string, result)
        quit()
    if len(result) == 1:
        return str(result[0])
    return None

def get_metadata_from_inspire(id_string):
    '''Get metadata from an INSPIRE record'''

    record = {}
    recid = get_recid_from_inspire(id_string)
    title = get_fieldvalues(recid, '245__a')[0]
    record['245__a'] = title
    return record

def base_title(title):
    '''Create a version of the title suitable for comparison.'''

    title = title.lower()
    title = re.sub(r'^(the|a) ', '', title)
    title = re.sub(r'\b(the|a)\b', '', title)
    title = re.sub(r'[\W_]', '', title)
    return title

def compare_arxiv_inspire(eprint, recid):
    '''
    Compare arXiv and INSPIRE metadata and return metadata.
    If the title is an exact match it returns True for title match.

    '''

    eprint_record = get_metadata_from_arxiv(eprint)
    eprint_title = eprint_record['246__a']
    inspire_record = get_metadata_from_inspire(recid)
    try:
        inspire_title = inspire_record['245__a']
    except TypeError:
        inspire_title = \
        '** NO INFORMATION IN INSPIRE for {0}'.format(recid)
    inspire_title_base = base_title(inspire_title)
    eprint_title_base = base_title(eprint_title)
    if inspire_title_base == eprint_title_base:
        title_match = True
    else:
        title_match = False
        message = '\nTitle mismatch\n{0} {1}\nA: {2}\nI: {3}\n\n'.\
           format(eprint, recid,
           eprint_title.capitalize(), inspire_title.capitalize())
        logging.info(message)
    return (title_match, eprint_record, inspire_record)

def main(max_count=10):
    '''Get metadata for an eprint.'''

    print 'max_count =', max_count
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename, 'w')
    output.write('<collection>')

    filename_check = 'tmp_' + __file__
    filename_check = re.sub('.py', '_check_append.out', filename_check)
    output_check = open(filename_check, 'w')
    output_check.write('<collection>')

    with open(INPUT_FILE) as file_h:
        counter = 0
        for line in file_h:
            match_obj = re.match(r'Need eprint: (\S+) (\S+)', line)
            eprint = match_obj.group(1)
            doi = match_obj.group(2)
            eprint = clean_eprint(eprint)
            if eprint in IGNORE_EPRINTS:
                continue
            recid = get_recid_from_inspire(eprint)
            if recid:
                logging.info('We have this eprint: ' + eprint + recid)
                continue
            elif recid == False:
                logging.info('Malformed eprint: ' + eprint)
                continue
            recid = get_recid_from_inspire(doi)
            if not recid:
                logging.info('We do not have this DOI:' + doi)
                continue
            diff = compare_arxiv_inspire(eprint, recid)
            if diff[0]:
                output.write(create_xml(recid, diff[1]))
                counter += 1
            else:
                output_check.write(create_xml(recid, diff[1]))
                counter += 1
            if counter > max_count:
                break

    output_check.write('</collection>')
    output_check.close()
    output.write('</collection>')
    output.close()
    print filename
    print filename_check
    print LOGFILE

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
