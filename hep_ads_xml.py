"""
Script for getting records from ADS and adding any missing information to the
corresponding records in INSPIRE.
http://ads.harvard.edu/pubs/arXiv/ADSmatches.xml
http://ads.harvard.edu/pubs/arXiv/ADSmatches_updates.xml

"""

from invenio.search_engine import perform_request_search, \
                                  get_all_field_values, \
                                  search_unit
from invenio.bibrecord import print_rec, record_add_field
from hep_ads_xml_bibcodes import BIBCODE_DICT, JOURNAL_DICT
from hep_ads_xml_input import DOCUMENT, \
                              CORE_JOURNALS, \
                              CORE_JOURNALS_DOI, \
                              OUTPUT_COUNTER_MAX

import xml.etree.ElementTree as ET
import re
import random
import time
import datetime
import logging

LOGFILE = 'tmp_' + __file__
LOGFILE = re.sub('.py', '.log', LOGFILE)
logging.basicConfig(filename=LOGFILE, filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

ADS_REGEX = re.compile(r"^\d{4}([a-z&]+)[\d.]+[a-z.\d]+$",
                       re.IGNORECASE)
ADS_J_REGEX = \
re.compile(r'(.*[a-zJ][a-z\.]|JHEP|JCAP)([A-EGX]?)\.?(\d+)\:(\d+)\,(\d+)')
ARXIV_REGEX = re.compile(r"^[a-z]+\-?[a-z]+\.?[A-Z]*/\d{7}$")
ARXIV_REGEX_NEW = re.compile(r'^\d{4}\.\d{4}\d?$')
BIBCODERE = re.compile(r'^(\d{4}[.&0-9A-Za-z]{15})$')

INSPIRE_EPRINTS = set()
INSPIRE_BIBCODES = set()
INSPIRE_DOIS = set()
EPRINT_UNION = set(get_all_field_values('035__a')) | \
               set(get_all_field_values('035__z')) | \
               set(get_all_field_values('037__a'))
for item in EPRINT_UNION:
    if item.startswith('oai:arXiv.org:'):
        INSPIRE_EPRINTS.add(item.replace('oai:arXiv.org:', ''))
    elif item.startswith('arXiv:'):
        INSPIRE_EPRINTS.add(item.replace('arXiv:', ''))
    elif re.match(ARXIV_REGEX, item):
        INSPIRE_EPRINTS.add(item)
    elif len(item) != 19:
        continue
    if re.match(ADS_REGEX, item):
        INSPIRE_BIBCODES.add(item)
for item in get_all_field_values('0247_a'):
    if item.startswith('10.'):
        INSPIRE_DOIS.add(item)
INSPIRE_JOURNALS = set(get_all_field_values('711__a'))
INSPIRE_EPRINT_RECIDS = search_unit('arxiv', f='037__9', m='a')
INSPIRE_DOI_RECIDS = search_unit('doi', f='0247_2', m='a')
INSPIRE_IDENTIFIER_RECID_DICT = {}

print 'Eprints', len(INSPIRE_EPRINTS), random.sample(INSPIRE_EPRINTS, 1)
print 'Bibcodes', len(INSPIRE_BIBCODES), random.sample(INSPIRE_BIBCODES, 1)
print 'DOIs', len(INSPIRE_DOIS), random.sample(INSPIRE_DOIS, 1)
print 'Journals', len(INSPIRE_JOURNALS), random.sample(INSPIRE_JOURNALS, 1)

def check_doi_eprint(identifier):
    "Check to see if we already have a DOI eprint pairing."

    if identifier.startswith('10.'):
        result = search_unit(identifier, f='0247_a', m='a')
        if len(result) == 1:
            INSPIRE_IDENTIFIER_RECID_DICT[identifier] = result[0]
            result = result & INSPIRE_EPRINT_RECIDS
    elif any((re.match(ARXIV_REGEX, identifier),
              re.match(ARXIV_REGEX_NEW, identifier))):
        prefix = ''
        if re.match(ARXIV_REGEX_NEW, identifier):
            prefix = 'arXiv:'
        result = search_unit(prefix + identifier, f='037__a', m='a')
        if len(result) == 1:
            INSPIRE_IDENTIFIER_RECID_DICT[identifier] = result[0]
            result = result & INSPIRE_DOI_RECIDS
    else:
        return None
    if len(result):
        return True
    return None

def journal_fix(journal, bibcode=None):
    """
    Puts the journal name into INSPIRE form.
    """

    try:
        return BIBCODE_DICT[re.match(ADS_REGEX, bibcode).group(1)]
    except (AttributeError, KeyError, NameError):
        pass
    if journal in INSPIRE_JOURNALS:
        return journal
    try:
        return JOURNAL_DICT[journal]
    except KeyError:
        return None

def core_journal_check(doi, journal=None):
    """Tests to see if this is one of our core journals."""

    for core_doi in CORE_JOURNALS_DOI:
        if doi.startswith(core_doi):
            return True
    if journal in CORE_JOURNALS:
        return True
    return False

def bad_journal_check(journal, bibcode):
    """
    Tests to see if this is a journal whose publication note
    cannot be properly parsed in the ADS xml document.
    """

    #Recent articles in IJMP have 7 digit article IDs, don't work in ADS dump
    #{'journal_bibcode': '2019IJMPA..3450061B', 'preprint_id': '1810.13051',
    #'journal_ref': 'Int.J.Mod.Phys.A.34:0061,2019', 'eprint_bibcode':
    #'2018arXiv181013051B', 'doi': '10.1142/S0217751X19500611', 'time_stamp':
    #'2019-6-3'}
    match_obj = re.match(r'\d{4}IJMP[A-ES]\.\.(\d{7})[A-z]', bibcode)
    if match_obj:
        logging.info('Check IJMP: ' + bibcode)
        return True
    if '.tmp.' in bibcode:
        return True
    if journal in ('PhDT', 'IJGMM'):
        return True
    return False

def get_page_letter(bibcode):
    "Determines the letter preceeding a page number."

    page_letter = ''
    if re.search(r'\.\.?\d+L\.', bibcode):
        page_letter = 'L'
    elif re.search(r'\.\.\d+A\.', bibcode):
        page_letter = 'A'
    return page_letter

def extract_metadata(input_dict):
    """
    This function creates an article dictionary from ADS input.
    """

    article_dict = {}
    eprint = input_dict['preprint_id']
    bibcode = input_dict['journal_bibcode']
    journal_ref = input_dict['journal_ref']
    doi = input_dict['doi']
    journal = volume = page = year = ''

    journal_ref = journal_ref.replace('Phys.Rev.L.', 'Phys.Rev.Lett.')
    #Phys.Rev.B.89:094506,2014
    #Eur.Phys.J.A.55:70,2019
    #Astroph.J.
    match_obj = re.match(ADS_J_REGEX, journal_ref)
    if not match_obj:
        logging.info('Problem with journal_ref: ' + str(input_dict))
        return None
    journal = match_obj.group(1)
    volume = match_obj.group(2) + match_obj.group(3)
    page = match_obj.group(4)
    year = match_obj.group(5)
    page = get_page_letter(bibcode) + page
    journal = journal_fix(journal, bibcode)
    if not journal:
        logging.info('Unidentified journal: ' + str(input_dict))
    else:
        journal = re.sub(r'::[A-EGX]', '', journal)
    if not journal or bad_journal_check(journal, bibcode) or \
       core_journal_check(doi, journal):
        return None

    article_dict['doi'] = doi
    if bibcode not in INSPIRE_BIBCODES:
        article_dict['bibcode'] = bibcode
    search = 'find j {0},{1},{2}'.format(journal, volume, page)
    result = perform_request_search(p=search, cc='HEP')
    journal_recid = 0
    if len(result) == 0:
        article_dict['journal'] = journal
        article_dict['volume'] = volume
        article_dict['page'] = page
        article_dict['year'] = year
    elif len(result) > 1:
        logging.info('Multiple {0},{1},{2}'.format(journal, volume, page))
        return None
    else:
        journal_recid = result[0]

    if eprint not in INSPIRE_IDENTIFIER_RECID_DICT:
        logging.info('Problem searching eprint: ' + str(eprint))
        return None
    eprint_recid = INSPIRE_IDENTIFIER_RECID_DICT[eprint]
    if journal_recid not in (0, eprint_recid):
        logging.info('Mismatch in eprint, JVP: ' + str(input_dict))
        return None
    article_dict['recid'] = eprint_recid
    return article_dict

def create_xml(input_dict):
    """
    This function create_xml takes a metadata dictionary.
    """

    metadata_dict = extract_metadata(input_dict)
    if not metadata_dict:
        return None
    record = {}
    try:
        record_add_field(record, '001',
                         controlfield_value=str(metadata_dict['recid']))
    except KeyError:
        logging.info('Problem with finding recid: ' + str(input_dict))
    try:
        journal = metadata_dict['journal']
        volume = metadata_dict['volume']
        page = metadata_dict['page']
        year = metadata_dict['year']
        pubnote = [('p', journal), ('v', volume), ('c', page)]
        if journal == 'ICRC':
            journal = journal + ' ' + year
            pubnote = [('q', journal), ('v', volume), ('c', page)]
        else:
            pubnote.append(('y', year))
    except KeyError:
        logging.info('Problem with extracting j,v,p,y: ' + str(input_dict))
        return None
    record_add_field(record, '773', '', '', subfields=pubnote)
    try:
        doi = [('a', metadata_dict['doi']), ('2', 'DOI'), ('9', 'ADS')]
    except KeyError:
        logging.info('Problem with extracting doi: ' + str(input_dict))
        return None
    record_add_field(record, '024', '7', '', subfields=doi)
    try:
        bibcode = [('a', metadata_dict['bibcode']), ('9', 'ADS')]
    except KeyError:
        logging.info('Not adding bibcode: ' + str(input_dict))
        return None
    record_add_field(record, '035', '', '', subfields=bibcode)
    return print_rec(record)

def get_eprint_doi_needed(ads_eprints, ads_dois, doi_to_eprint):
    """
       Take in the eprints and DOIs of the ADS document and
       return the ones needed for INSPIRE.
    """

    #ads_eprints = set(eprint_dict.keys())
    #ads_dois = set(doi_to_eprint.keys())
    eprint_y = ads_eprints & INSPIRE_EPRINTS
    eprint_n = ads_eprints - INSPIRE_EPRINTS
    doi_y = ads_dois & INSPIRE_DOIS
    doi_n = ads_dois - INSPIRE_DOIS
    #Convert doi_y and doi_n to their corresponding eprint numbers
    #in order to add them to the eprint sets.
    doi_y_eprint = set([doi_to_eprint[doi] for doi in doi_y])
    doi_n_eprint = set([doi_to_eprint[doi] for doi in doi_n])

    eprint_needed = eprint_n & doi_y_eprint
    doi_needed = eprint_y & doi_n_eprint
    return (eprint_needed, doi_needed)

def process_ads_xml_file(document):
    """Looks through the ADS xml file for new information."""

    output_counter = 0
    eprint_dict = doi_to_eprint = {}
    ads_eprints = ads_dois = set()
    output_check_doi_eprint = output_missing_eprint = output_xml = ''

    #tree = ET.parse(document)
    #root = tree.getroot()
    for child in ET.parse(document).getroot():
        if 'doi' not in child.attrib:
            continue
        if 'preprint_id' not in child.attrib:
            continue
        eprint = child.attrib['preprint_id']
        doi = child.attrib['doi']
        if not any((eprint, doi)):
            continue
        eprint_dict[eprint] = child
        doi_to_eprint[doi] = eprint
        ads_eprints.add(eprint)
        ads_dois.add(doi)

    (eprint_needed, doi_needed) = \
    get_eprint_doi_needed(ads_eprints, ads_dois, doi_to_eprint)

    print 'Eprints needed:', len(eprint_needed)
    for eprint in eprint_needed:
        child = eprint_dict[eprint]
        doi = child.attrib['doi']
        if check_doi_eprint(doi):
            output_check_doi_eprint += \
            'Check match: ' + eprint + ' ' + doi + '\n'
            continue
        output_missing_eprint += \
        'Need eprint: ' + eprint + ' ' + doi + '\n'
        continue

    print 'DOIs not in INSPIRE (could include core journals):', len(doi_needed)
    for eprint in doi_needed:
        child = eprint_dict[eprint]
        if output_counter > OUTPUT_COUNTER_MAX:
            break
        doi = child.attrib['doi']
        if check_doi_eprint(eprint):
            output_check_doi_eprint += \
            'Check match: ' + eprint + ' ' + doi + '\n'
            continue
        record_update = create_xml(child.attrib)
        if record_update:
            try:
                output_xml += record_update
                output_counter += 1
            except TypeError:
                logging.error('CANNOT print record: ' + str(child.attrib))
    print 'Number of records to be updated:', output_counter
    return (output_xml, output_missing_eprint, output_check_doi_eprint)

def main():
    """
    Go through an ADS xml and print out any information missing
    from INSPIRE.
    """

    output_xml, output_missing_eprint, output_check_doi_eprint\
    = process_ads_xml_file(DOCUMENT)

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename, 'w')
    output.write('<collection>\n')
    #output.write("{0:25}{1:16}{2:7}{3:12}{4:7}{5:5}\n".format('journal',
    #                                        'journal_letter',
    #                                        'volume', 'page_letter',
    #                                        'page', 'year'))
    output.write(output_xml)
    output.write('</collection>')
    output.close()
    print filename

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_missing_eprint.out', filename)
    output = open(filename, 'w')
    output.write(output_missing_eprint)
    output.close()
    print filename


    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_check_doi_eprint.out', filename)
    output = open(filename, 'w')
    output.write(output_check_doi_eprint)
    output.close()
    print filename
    print LOGFILE

if __name__ == '__main__':
    try:
        TIME_1 = time.time()
        main()
        TIME_2 = time.time()
        TOTAL_TIME = TIME_2 - TIME_1
        RUN_TIME = 'Run time = ' + str(datetime.timedelta(seconds=TOTAL_TIME))
        print RUN_TIME
        logging.info(RUN_TIME)
    except KeyboardInterrupt:
        print 'Exiting'

