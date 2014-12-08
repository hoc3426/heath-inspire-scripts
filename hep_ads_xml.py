"""
Script for getting records from ADS and adding any missing information to the
corresponding records in INSPIRE.
http://ads.harvard.edu/pubs/arXiv/ADSmatches.xml
http://ads.harvard.edu/pubs/arXiv/ADSmatches_updates.xml

"""

from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field
from hep_ads_xml_bibcodes import JOURNAL_DICT
from hep_ads_xml_bibcodes import BIBCODE_DICT
from hep_published import JOURNAL_PUBLISHED_DICT

import xml.etree.ElementTree as ET
import re

VERBOSE = 0
DEBUG = 0

DOCUMENT = 'ADSmatches_updates.xml'
#DOCUMENT = 'ADS_astro2.xml'
#DOCUMENT = 'ADS_cond.xml'
#DOCUMENT = 'ADS_math.xml'
#DOCUMENT = 'ADSmatches.xml'
DOCUMENT = '/afs/cern.ch/project/inspire/TEST/hoc/ADSmatches.xml'
#DOCUMENT = '/afs/cern.ch/project/inspire/TEST/hoc/ADSmatches_updates.xml'

BADRECS = [1299943, 1263270, 782224, 799038, 834458]
BADRECS = []
#INPUT_COUNTER = 66885
#INPUT_COUNTER = 891510
#INPUT_COUNTER = 79900
INPUT_COUNTER = 350000
OUTPUT_COUNTER = 11



def journal_fix(journal):
    """
    Puts the journal name into INSPIRE form.
    """
    if journal == 'PhDT':
        return None
    if re.match(r'^[A-Z]\w*\&?\w+$', journal):
        for key in BIBCODE_DICT:
            if journal == key:
                return BIBCODE_DICT[key]
    #for key in JOURNAL_DICT:
    #        if journal == key:
    #            return JOURNAL_DICT[key]
    #journal = re.sub(r'^Acta\.', r'Acta ', journal)
    #search = '711__a:"' + journal + '"'
    #result = perform_request_search(p=search, cc='Journals')
    #if len(result) == 1:
    #    return journal
    #elif re.search(r'\.$', journal):
    #    journal = re.sub(r'\.$', r'', journal)
    #    journal_iter = journal_fix(journal)
    #    return journal_iter   
    #else:
        if VERBOSE > 0:
            print 'BAD JOURNAL', journal
    return None

def create_xml(input_dict):
    """
    The function create_xml takes an article dictionary from ADS and
    checks to see if it has information that should be added to INSPIRE.
    If so, it builds up that information.
    """

    elements = ['doi', 'preprint_id', 'journal_bibcode', 'journal_ref']
    element_dict = {}
    pubyear = ''
    for element in elements:
        element_dict[element] = ''
        if element in input_dict:
            element_dict[element] = input_dict[element]
        #print element, '=', element_dict[element]
    eprint        = element_dict['preprint_id']
    doi           = element_dict['doi']
    bibcode       = element_dict['journal_bibcode']
    journal_ref   = element_dict['journal_ref']
    journal       = ''
    volume        = ''
    volume_letter = ''
    page          = ''
    page_letter   = ''
    if VERBOSE == 2:
        print element_dict
    if eprint:
        eprint  = re.sub(r'arXiv:([a-z])', r'\1', eprint)
        search  =  '037__a:' + eprint + ' or 037__a:arXiv:' + eprint
        result = perform_request_search(p=search, cc='HEP')
        if VERBOSE == 2:
            print search, result
        if len(result) == 0:
            return None
    if doi:
        if re.search(r'10.1103/PhysRev[CD]', doi):
            return None
        if re.search(r'10.1016/j.nuclphysb', doi):
            return None
        search  =  '0247_a:' + doi
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1:
            return None
        match_obj = re.search(r'10.1051/epjconf/(\d{4})(\d\d)(\d{5})', doi)
        if match_obj:
            journal = 'EPJ Web Conf.'
            volume  = match_obj.group(2)
            page    = match_obj.group(3)
            pubyear = match_obj.group(1)
    if bibcode:
        search  = '035__a:' + bibcode
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1:
            return None
        if re.search(r'PhRv[CD]', bibcode):
            return None
        match_obj = re.match(r'^\d{4}(\w+\&?\w+)', bibcode)
        if match_obj:
            if VERBOSE == 2:
                print 
            journal = journal_fix(match_obj.group(1))
            if VERBOSE == 2:
                print journal
            if journal:
                match_obj = re.match(r'(.*)\:\:(\w+)', journal)
                if match_obj:
                    journal = match_obj.group(1)
                    volume_letter = match_obj.group(2)
        if re.search(r'\.\.\d+L\.', bibcode):
            page_letter = 'L'
        elif re.search(r'\.\.\d+A\.', bibcode):
            page_letter = 'A'
        if VERBOSE == 2:
            print 'page_letter = ', page_letter
    if journal_ref:
        #Phys.Rev.A.86:013639,2012
        #J.Appl.Phys.100:084104,2006
        match_obj = re.search(r'(.*\w\.)(\d+)\:(\w+)\,(\d{4})', journal_ref)
        if match_obj:
            volume  = match_obj.group(2)
            page    = match_obj.group(3)
            pubyear = match_obj.group(4)
            if not journal:
                journal = match_obj.group(1)
                match_obj = re.match(r'^(.*\.)(\w)\.$', journal)
                if match_obj:
                    letter   = match_obj.group(2)
                    if letter in ['A', 'B', 'C', 'D', 'E', 'G', 'X']:
                        volume_letter = letter
                        journal  = match_obj.group(1)
                if VERBOSE == 2:
                    print journal
                journal = journal_fix(journal)
                if VERBOSE == 2:
                    print journal
        if VERBOSE == 2:
            print journal, volume, page, pubyear
    if eprint and journal and volume and page and pubyear:
        volume  = volume_letter + volume
        page    = page_letter + page
        search = 'find j "' + journal + ',' + volume + ',' + page + '"'
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1:
            return None
        search = "find eprint " + eprint + " not tc p"
        if VERBOSE == 2:
            print search
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1 :
            recid = result[0]
            for badrec in BADRECS:
                if recid == badrec:
                    return None
            record = {}
            record_add_field(record, '001', controlfield_value=str(recid))
            pubnote = [('p', journal), ('v', volume), ('c', page)]
            if journal == 'ICRC':
                journal = journal + ' ' + pubyear
                pubnote = [('q', journal), ('v', volume), ('c', page)]
            else:
                pubnote.append(('y', pubyear))
            record_add_field(record, '773', '', '', subfields=pubnote)
            if journal in JOURNAL_PUBLISHED_DICT:
                collection = [('a', 'Published')]
                record_add_field(record, '980', '', '', subfields=collection)
            if doi:
                doi  = [('a', doi), ('2', 'DOI'), ('9', 'ADS')]
                record_add_field(record, '024', '7', '', subfields=doi)
            if bibcode:
                bibcode  = [('a', bibcode), ('9', 'ADS')]
                record_add_field(record, '035', '', '', subfields=bibcode)
            return print_rec(record)
        else:
            return None
    else:
        return None

def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    tree = ET.parse(DOCUMENT)
    root = tree.getroot()
    input_counter  = 1
    output_counter = 1
    for child in root:
        if input_counter < INPUT_COUNTER:
            input_counter  += 1
        else:
            if output_counter == OUTPUT_COUNTER: break
            if 'doi' in child.attrib:
                record_update = create_xml(child.attrib)
                if record_update:
                    try:
                        if DEBUG == 1:
                            print record_update
                        else:
                            output.write(record_update)
                            output_counter += 1
                    except:
                        print 'CANNOT print record', child.attrib
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

