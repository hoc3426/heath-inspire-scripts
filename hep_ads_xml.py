"""
Script for getting records from ADS and adding any missing information to the
corresponding records in INSPIRE.
http://ads.harvard.edu/pubs/arXiv/ADSmatches.xml
http://ads.harvard.edu/pubs/arXiv/ADSmatches_updates.xml

"""

from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field
from hep_ads_xml_bibcodes import BIBCODE_DICT, TRICKY_JOURNALS
from hep_published import JOURNAL_PUBLISHED_DICT

import xml.etree.ElementTree as ET
import re

TEST = False
#TEST = True
VERBOSE = False
DEBUG = False
UPDATE = True
UPDATE = False

STARTING_COUNTER = 476727
ENDING_COUNTER = 5001


DOCUMENT = '/afs/cern.ch/project/inspire/TEST/hoc/ADSmatches.xml'

if TEST:
    VERBOSE = 1
    DEBUG = 1
    DOCUMENT = '/afs/cern.ch/project/inspire/TEST/hoc/test.xml'
    #DOCUMENT = 'test.xml'
    #DOCUMENT = 'ADS_astro2.xml'
    #DOCUMENT = 'ADS_cond.xml'
    #DOCUMENT = 'ADS_math.xml'
    #DOCUMENT = 'ADSmatches.xml'

BADRECS = [1299943, 1263270, 782224, 799038, 834458]
BADRECS = [1202336, 744283, 419659, 535573, 535574, 535581, 799568, 536276,
           650007, 631684]

BIBCODERE = re.compile(r'^(\d{4}[.&0-9A-Za-z]{15})$')

if UPDATE:
    DOCUMENT = '/afs/cern.ch/project/inspire/TEST/hoc/ADSmatches_updates.xml'
    STARTING_COUNTER = 1


def journal_fix(journal):
    """
    Puts the journal name into INSPIRE form.
    """
    if journal == 'PhDT':
        return None
    elif journal == 'IJGMM':
        return None
    if re.match(r'^[A-Z]\w*\&?\w+$', journal):
        for key in BIBCODE_DICT:
            if journal == key:
                return BIBCODE_DICT[key]
    else:
        if VERBOSE > 0:
            print 'BAD JOURNAL', journal
    return None

def create_xml(input_dict):
    """
    The function create_xml takes an article dictionary from ADS and
    checks to see if it has information that should be added to INSPIRE.
    If so, it builds up that information.
    """

    need_bibcode   = False
    need_doi       = False
    need_pubnote   = False
    recid_eprint   = 0
    recid_doi      = 0
    recid_pubnote  = 0

    if TEST:
        print "In create_xml"
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
    if DEBUG == 1:
        print element_dict
    if eprint:
        eprint  = re.sub(r'arXiv:([a-z])', r'\1', eprint)
        search  =  'find eprint ' + eprint
        result = perform_request_search(p=search, cc='HEP')
        if DEBUG == 1:
            print search, result
        if len(result) == 0:
            return None
        elif len(result) == 1:
            recid_eprint = result[0]
            for badrec in BADRECS:
                if recid_eprint == badrec:
                    return None
        else:
            print 'Multiple ', search
            return None
    else:
        return None
    if doi:
        if re.search(r'10.1103/PhysRev[CD]', doi):
            return None
        if re.search(r'10.1016/j.nuclphysb', doi):
            return None
        search  =  '0247_a:' + doi
        result = perform_request_search(p=search, cc='HEP')
        if DEBUG == 1:
            print search, result
        if len(result) == 1:
            recid_doi = result[0]
            if recid_doi != recid_eprint:
                print "Check eprint doi mismatch", recid_eprint, recid_doi
                return None
        elif len(result) == 0:
            need_doi = True
        else:
            print 'Multiple ', search
            return None
        match_obj = re.search(r'10.1051/epjconf/(\d{4})(\d\d)(\d{5})', doi)
        if match_obj:
            journal = 'EPJ Web Conf.'
            volume  = match_obj.group(2)
            page    = match_obj.group(3)
            pubyear = match_obj.group(1)
        else:
            pass
            #match_obj = re.search(r'10.1142\/S0217751X(\d{7})\w', doi)
            #if match_obj:
                #page    = match_obj.group(1)
                ##print 'DOI match', page
    if bibcode:
        if not BIBCODERE.match(bibcode):
            print "Bad bibcode", bibcode, recid_eprint
            return None
        search  = '035__a:' + bibcode
        result = perform_request_search(p=search, cc='HEP')
        if TEST:
            print search, result
        if len(result) == 1:
            recid_bibcode = result[0]
            if recid_bibcode != recid_eprint:
                print "Check eprint bibcode mismatch", recid_eprint, \
                                                       recid_bibcode
                return None
        elif len(result) == 0:
            need_bibcode = True
        #2015IJMPA..3050059N
        match_obj = re.match(r'^(\d{4})IJMP(\w)\.\.(\d{7})\w', bibcode)
        if match_obj:
            if TEST:
                print 'IJMP = ', bibcode 
            if not page:
                return None
            journal        = 'Int.J.Mod.Phys.'
            pubyear        = match_obj.group(1)
            volume_letter  = match_obj.group(2)
            if TEST:
                print 'IJMP', journal, pubyear, volume, page
        match_obj = re.match(r'^\d{4}(\w+\&?\w+)', bibcode)
        if match_obj:
            journal = match_obj.group(1)
            if DEBUG == 1:
                print journal
            journal = journal_fix(journal)
            if DEBUG == 1:
                print journal
            if journal:
                match_obj = re.match(r'(.*)\:\:(\w+)', journal)
                if match_obj:
                    journal = match_obj.group(1)
                    volume_letter = match_obj.group(2)
        if re.search(r'\.\.?\d+L\.', bibcode):
            page_letter = 'L'
        elif re.search(r'\.\.\d+A\.', bibcode):
            page_letter = 'A'
        if DEBUG == 1:
            print 'page_letter = ', page_letter
    if journal_ref and not volume:
        #Phys.Rev.A.86:013639,2012
        #J.Appl.Phys.100:084104,2006
        match_obj = re.search(r'(.*\w\.)(\d+)\:(\w+)\,(\d{4})', journal_ref)
        if match_obj:
            if not volume:
                volume  = match_obj.group(2)
            if not page:
                page    = match_obj.group(3)
            if not pubyear:
                pubyear = match_obj.group(4)
            if not journal:
                journal = match_obj.group(1)
                match_obj = re.match(r'^(.*\.)(\w)\.$', journal)
                if match_obj:
                    letter   = match_obj.group(2)
                    if letter in ['A', 'B', 'C', 'D', 'E', 'G', 'X']:
                        volume_letter = letter
                        journal  = match_obj.group(1)
                if DEBUG == 1:
                    print journal
                journal = journal_fix(journal)
                if DEBUG == 1:
                    print journal
        if DEBUG == 1:
            print journal, volume, page, pubyear
    if journal == 'JHEP' or journal == 'JCAP':
        volume = pubyear[-2:]  + volume
    elif journal == 'JINST':
        # or journal == 'Comptes Rendus Physique':
        journal = None
    if journal and volume and page and pubyear:
        volume  = volume_letter + volume
        page    = page_letter + page
        #search = 'find j "' + journal + ',' + volume + ',' + page + '"'        
        #search = '773__p:"' + journal + '" 773__v:' + volume + ' 773__c:' + page
        #search += ' or (773__p:"' + journal + '" 773__v:' + volume + \
        #           ' 773__c:"' + page + '\-*")'
        search = 'journal:"' + journal + ',' + volume + ',' + page + '"'
        result = perform_request_search(p=search, cc='HEP')
        if DEBUG:
            print search, result
        if len(result) == 1:
            recid_pubnote = result[0]
            if recid_pubnote != recid_eprint:
                print "Check eprint pubnote mismatch", recid_eprint, \
                                                       recid_pubnote
                return None
        elif len(result) == 0:
            need_pubnote = True
        else:
            print 'Multiple ', search
            return None
        #Can't always trust weird page numbers, check the pub year
        search = '001:' + str(recid_eprint) + ' 773__y:' + pubyear
        result = perform_request_search(p=search, cc='HEP')
        if TEST:
            print search, result
        if len(result) == 1:
            need_pubnote = False
        if recid_pubnote and not need_bibcode and not need_doi:
            return None   
    if need_pubnote and not need_doi and journal in TRICKY_JOURNALS:
        need_pubnote = False
    if need_doi or need_bibcode or need_pubnote:
        record = {}
        record_add_field(record, '001', controlfield_value=str(recid_eprint))
        pubnote = [('p', journal), ('v', volume), ('c', page)]
        if journal == 'ICRC':
            journal = journal + ' ' + pubyear
            pubnote = [('q', journal), ('v', volume), ('c', page)]
        else:
            pubnote.append(('y', pubyear))
        if need_pubnote:
            record_add_field(record, '773', '', '', subfields=pubnote)
        if journal in JOURNAL_PUBLISHED_DICT:
            search = "001:" + str(recid_eprint) + " -980__a:Published"
            result = perform_request_search(p=search, cc='HEP')
            if len(result) == 1:
                collection = [('a', 'Published')]
                record_add_field(record, '980', '', '', subfields=collection)
        if need_doi:
            doi  = [('a', doi), ('2', 'DOI'), ('9', 'ADS')]
            record_add_field(record, '024', '7', '', subfields=doi)
        if need_bibcode:
            bibcode  = [('a', bibcode), ('9', 'ADS')]
            record_add_field(record, '035', '', '', subfields=bibcode)
        if TEST:
            print 'doi, bibcode, pbn', need_doi, need_bibcode, need_pubnote, \
                                   recid_eprint
        return print_rec(record)
    else:
        return None

def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    tree = ET.parse(DOCUMENT)
    root = tree.getroot()
    line_counter   = 1
    output_counter = 1
    for child in root:
        line_counter += 1
        if line_counter < STARTING_COUNTER:
            pass
        else:
            if output_counter == ENDING_COUNTER:
                print 'line_counter =', line_counter
                break
            if 'doi' in child.attrib:
                record_update = create_xml(child.attrib)
                if record_update:
                    try:
                        if DEBUG == 1:
                            print record_update
                        else:
                            if not TEST:
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

