import xml.etree.ElementTree as ET
from xml.dom import minidom

import re
import cgi
import sys
from datetime import datetime
import time

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import print_record
from invenio.intbitset import intbitset
from invenio.bibformat_engine import BibFormatObject
from check_url import checkURL

from osti_web_service_constants import *

LOGFILE = 'osti_web_service.log'
VERBOSE = True
RECIDS = False


CMS = intbitset(perform_request_search(p="find r fermilab and cn cms", \
                                       cc='HEP'))

def get_url(recid):
    url = None
    url_fermilab = None
    url_arxiv = None
    url_openaccess = None
    url_postprint = None
    accepted = False

    for item in BibFormatObject(recid).fields('8564_'):
        if item.has_key('y'):
            if item['y'] == 'Article from SCOAP3':
                url_openaccess = item['u']
                accepted = True
        if item.has_key('3') and not url_openaccess:
            if item['3'] == 'openaccess':
                url_openaccess = item['u']
                accepted = True    
            elif item['3'] == 'postprint':
                url_postprint = item['u']
                accepted = True
 
    if not accepted:
        urls = get_fieldvalues(recid, '8564_u')
        for url_i in urls:
            if re.search(r'fermilab\-.*pdf', url_i):
                url_fermilab = url_i
            elif re.search(r'record/\d+/files/arXiv', url_i):
                url_arxiv = url_i
            
    if url_openaccess:
        url = url_openaccess
    elif url_postprint:
        url = url_postprint
    elif url_fermilab:
        url = url_fermilab
    elif url_arxiv and recid in CMS:
        url = url_arxiv
    if url:
        return [url, accepted]
    else:
        return None

def get_title(recid):
    title = get_fieldvalues(recid, '245__a')[0]
    title = cgi.escape(title)
    return title

def get_authors(recid):
    authors = get_fieldvalues(recid, "100__a") \
            + get_fieldvalues(recid, "700__a")
    if len(authors) <= 10 and len(authors) > 0:
       return '; '.join([unicode(a, "utf-8") for a in authors])
    elif len(authors) > 10:
       return authors[0] + "; et al."

def get_reports(recid):
    reports = get_fieldvalues(recid, "037__z") \
            + get_fieldvalues(recid, "037__a")
    return '; '.join(r for r in reports)

def get_product_type(recid):
    type_dict = {'TM':'TR', 'CONF':'CO', 'PUB':'JA', 'THESIS':'TD',
                 'MASTERS':'TD', 'BACHELORS':'TD', 'HABILITATION':'TD',
                 'DESIGN':'PD'}
    product_type = '??'
    report_string = get_reports(recid)
    for key in type_dict:
        pattern = 'FERMILAB-' + key
        if re.search(pattern, report_string):
            product_type = type_dict[key]
    return product_type
    

def get_affiliations(recid, long):
    affiliations = get_fieldvalues(recid, "100__u") \
                 + get_fieldvalues(recid, "700__u")
    aff_dict= {'Argonne':'ANL', 
               'Brookhaven':'BNL', 
               'Fermilab':'FNAL',
               'LBL, Berkeley':'LBNL', 
               'LLNL, Livermore':'LLNL',
               'Los Alamos':'LANL', 
               'Oak Ridge':'ORNL',
               'PNL, Richland':'PNNL', 
               'Princeton U., Plasma Physics Lab.':'PPPL',
               'SLAC':'SLAC',
               'Sandia':'SNL-CA',
               'Sandia, Livermore':'SNL-NM',
               'Jefferson Lab':'TJNAF'}
    doe_affs = []
    doe_affs_long = []
    for aff in affiliations:
        if aff in aff_dict and not aff_dict[aff] in doe_affs:
            doe_affs.append(aff_dict[aff])
            doe_affs_long.append(DOE_AFF_DICT[aff_dict[aff]])
    if long:
        return '; '.join([a for a in doe_affs_long])        
    else:
        return '; '.join([a for a in doe_affs])

def get_date(recid):
    try:
        date = get_fieldvalues(recid, '269__c')[0]
    except:
        try:
            date = get_fieldvalues(recid, '260__c')[0]
        except:
           try:
               date = get_fieldvalues(recid, '502__d')[0]
           except:
               date = 1900
    try:
        date_object = datetime.strptime(date, '%Y-%m-%d')
        date = date_object.strftime('%m/%d/%Y')
    except:
        try:
            date_object = datetime.strptime(date, '%Y-%m')
            date = date_object.strftime('%Y %B')
        except:
            pass
    return date

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_xml(recid, records):
    #records = ET.Element('records')
    record = ET.SubElement(records, 'record')
    #osti_id = ET.SubElement(record, 'osti_id')
    site_input_code = ET.SubElement(record, 'site_input_code')
    product_type = ET.SubElement(record, 'product_type')
    journal_type = ET.SubElement(record, 'journal_type')
    title = ET.SubElement(record, 'title')
    author = ET.SubElement(record, 'author')
    report_nos = ET.SubElement(record, 'report_nos')
    doe_contract_nos = ET.SubElement(record, 'doe_contract_nos')
    originating_research_org = \
               ET.SubElement(record, 'originating_research_org')
    publicaton_date = ET.SubElement(record, 'publicaton_date')
    language = ET.SubElement(record, 'language')
    country_publication_code = ET.SubElement(record, 'country_publication_code')
    sponsor_org = ET.SubElement(record, 'sponsor_org')
    access = ET.SubElement(record, 'access.limitation')
    medium_code = ET.SubElement(record, 'medium_code')
    site_url = ET.SubElement(record, 'site_url')
    file_format = ET.SubElement(record, 'file_format')

    site_input_code.text = SITE    
    product_type.text = get_product_type(recid)
    title.text = get_title(recid)
    author.text = get_authors(recid)
    report_nos.text = get_reports(recid)
    doe_contract_nos.text = DOE_NUMBER
    originating_research_org.text = get_affiliations(recid, True)
    publicaton_date.text = get_date(recid)
    language.text = LANGUAGE
    country_publication_code.text = COUNTRY
    sponsor_org.text = SPONSOR
    access.text = 'UNL'
    medium_code.text = 'ED'
    [url, accepted] = get_url(recid)
    site_url.text = url
    if accepted:
        journal_type.text = 'AM'
    else:
        journal_type.text = 'FT'
    file_format.text = 'PDF/A'
    #print prettify(records)


def main(recids):
    #recids = [1400805, 1373745, 1342808, 1400935]
    records = ET.Element('records')
    for recid in recids:
        if get_url(recid):
            create_xml(recid, records)
    print prettify(records)
    


def find_records():
    """
    Finds records to send email to.
    """

    print """
    Let's do a HEP search in INSPIRE format
    """
    search_input = raw_input("Your search? ")
    if len(search_input) > 3:
    # and re.search(r':', search_input):
        search = search_input
    else:
        print "That's not a search. Game over."
        return None
    print search
    result = perform_request_search(p=search, cc='HEP')
    if len(result) > 0:
        log = open(LOGFILE, 'a')
        date_time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        date_time_stamp = date_time_stamp + ' ' + search + ' : '\
                    + str(len(result)) + '\n'
        log.write(date_time_stamp)
        log.close()
        return result
    else:
        print "No results found."
        return None

if __name__ == '__main__':
    if not RECIDS:
        RECIDS = []
        try:
            RECID = int(sys.argv[1:][0])
            RECIDS.append(RECID)
        except:
            RECIDS = find_records()
    try:
        main(RECIDS)
    except KeyboardInterrupt:
        print 'Exiting'

