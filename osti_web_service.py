"""
Script to push information on Fermilab publications
to OSTI using the webservice AN241.1.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

import re
import cgi
import sys
import datetime
import pytz
import os

from urllib2 import Request, urlopen
import PyPDF2
from PyPDF2 import PdfFileReader
from StringIO import StringIO


from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.intbitset import intbitset
from invenio.bibformat_engine import BibFormatObject
from check_url import checkURL

from osti_web_service_constants import ACCEPTED_SEARCH, \
                                       DIRECTORY, \
                                       DOE_AFF_DICT, \
                                       DOE_FERMILAB_DICT, \
                                       DOE_SUBJECT_CATEGORIES_DICT, \
                                       INSPIRE_AFF_DICT, \
                                       SEARCH, \
                                       TYPE_DICT

CHICAGO_TIMEZONE = pytz.timezone('America/Chicago')

LOGFILE = 'osti_web_service.log'
VERBOSE = True
VERBOSE = False
TEST = False
#TEST = True
RECIDS = False
ENDING_COUNTER = 20

CMS = intbitset(perform_request_search(p="find r fermilab and cn cms", \
                                       cc='HEP'))

def create_osti_id_pdf(recid, osti_id):
    """
    Places a PDF named after the OSTI id in a location that
    can be pushed to OSTI.
    If the pdf is not of an excepted paper it skips this.
    """
    final_pdf = None
    final_txt = None
    if VERBOSE:
        print recid, osti_id
    if not recid or not osti_id:
        return None
    try:
        [url, accepted] = get_url(recid)
        if accepted == False:
            return None
    except IndexError:
        print "No url on", recid
        return None
    except TypeError:
        print "No url on", recid
        return None
    remote_file = urlopen(Request(url)).read()
    memory_file = StringIO(remote_file)
    try:
        PdfFileReader(memory_file)
    except PyPDF2.utils.PdfReadError:
        print "PDF invalid for", recid
        return None
    except TypeError:
        print "Problem with", url
        return None
    final_pdf = DIRECTORY + str(osti_id) + ".pdf"
    final_txt = DIRECTORY + str(osti_id) + ".txt"
    if os.path.exists(final_pdf) or os.path.exists(final_txt):
        print "Already have PDF for recid=", recid, "osti_id=", osti_id
        print final_pdf
        print final_txt
        return None
    output = open(final_pdf, 'wb')
    output.write(remote_file)
    output.close()


def get_language(recid):
    """ Find the langauge of the work. """
    try:
        return get_fieldvalues(recid, '041__a')[0]
    except IndexError:
        return 'English'

def get_osti_id(recid):
    """ Find the osti_id from an INSPIRE record """
    osti_id = None
    for item in BibFormatObject(int(recid)).fields('035__'):
        if item.has_key('9') and item.has_key('a'):
            if item['9'].lower() == 'osti':
                osti_id = item['a']
    return osti_id

def check_already_sent(recid):
    """Looks to see if we've already sent the AM to OSTI."""

    osti_id = get_osti_id(recid)
    if osti_id:
        final_pdf = DIRECTORY + str(osti_id) + ".pdf"
        final_txt = DIRECTORY + str(osti_id) + ".txt"
        if os.path.exists(final_pdf) or os.path.exists(final_txt):
            if VERBOSE:
                print final_pdf
                print final_txt
            return True
    return False


def get_url(recid):
    """Is there a valid url? Is it to an accepted PDF?"""
    url = None
    url_fermilab = None
    url_arxiv = None
    url_openaccess = None
    url_postprint = None
    url_inspire = None
    accepted = False

    for item in BibFormatObject(int(recid)).fields('8564_'):
        if item.has_key('y'):
            if item['y'] == 'Article from SCOAP3':
                url_openaccess = item['u']
                accepted = True
        if item.has_key('z') and not url_openaccess:
            if item['z'] == 'openaccess':
                url_openaccess = item['u']
                accepted = True
            elif item['z'] == 'postprint':
                url_postprint = item['u']
                accepted = True

    if not accepted:
        urls = get_fieldvalues(recid, '8564_u')
        for url_i in urls:
            if re.search(r'lss.*fermilab\-.*pdf', url_i):
                url_fermilab = url_i
            elif re.search(r'record/\d+/files/arXiv', url_i):
                url_arxiv = url_i
            if re.search(r'inspirehep.*fermilab\-.*pdf', url_i):
                url_inspire = url_i
            elif re.search(r'inspirehep.*MUCOOL\-.*pdf', url_i):
                url_inspire = url_i

    if url_openaccess:
        url = url_openaccess
    elif url_postprint:
        url = url_postprint
    elif url_fermilab:
        url = url_fermilab
    elif url_arxiv and int(recid) in CMS:
        url = url_arxiv
    elif url_inspire:
        url = url_inspire

    if VERBOSE:
        print url

    if url:
        try:
            if checkURL(url):
                return [url, accepted]
            else:
                print "Check recid", recid
                print "Problem (if) with", url
                return [None, accepted]
        except:
            print "Check recid", recid
            print "Problem with (try) ", url
            return [None, accepted]
        #if checkURL(url):
        #    return [url, accepted]
        #else:
        #    print "Problem with", url
        #    return [None, accepted]
    else:
        return [None, False]

def get_title(recid):
    """Get title with in xml compliant form."""
    try:
        title = get_fieldvalues(recid, '245__a')[0]
        title = cgi.escape(title)
        return title
    except IndexError:
        print 'Problem with title on', recid
        return None

def get_pubnote(recid):
    """Gets publication information"""
    try:
        journal = get_fieldvalues(recid, "773__p")[0]
    except IndexError:
        journal = None
    try:
        volume = get_fieldvalues(recid, "773__v")[0]
    except IndexError:
        volume = None
    try:
        issue = get_fieldvalues(recid, "773__n")[0]
    except IndexError:
        issue = None
    try:
        pages  = get_fieldvalues(recid, "773__c")[0]
    except IndexError:
        pages = None
    try:
        doi = get_fieldvalues(recid, "0247_a")[0]
    except IndexError:
        doi = None
    return [journal, volume, issue, pages, doi]

def get_conference(recid_hep):
    """ Get conference information """
    try:
        cnum  = get_fieldvalues(recid_hep, "773__w")[0]
    except IndexError:
        return None
    search = '111__g:' + cnum
    result = perform_request_search(p=search, cc='Conferences')
    if len(result) != 1:
        return None
    recid = result[0]
    try:
        conference_note = get_fieldvalues(recid, "111__a")[0]
    except IndexError:
        conference_note = ''
    try:
        conference_note += ', ' + get_fieldvalues(recid, "111__c")[0]
    except IndexError:
        pass
    try:
        date = get_fieldvalues(recid, "111__x")[0]
        date_object = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date_object.strftime('%m/%d')
        conference_note += ', ' + date
    except IndexError:
        pass
    try:
        date = get_fieldvalues(recid, "111__y")[0]
        date_object = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date_object.strftime('%m/%d/%Y')
        conference_note += '-' + date
    except IndexError:
        pass
    if conference_note:
        return conference_note
    else:
        return None

def get_author_details(recid, authors, tag):
    """Get authors broken out as individuals"""
    for item in BibFormatObject(int(recid)).fields(tag):
        authors_detail = ET.SubElement(authors, 'authors_detail')
        author = None
        last_name = None
        first_name = None
        middle_name = None
        affiliation = None
        email = None
        orcid = None
        if item.has_key('a'):
            author = item['a']
            try:
                matchobj = re.match(r'(.*)\, (.*)\, (.*)', author)
                last_name = matchobj.group(1)
                fore_name = matchobj.group(2)
                title     = matchobj.group(3)
                fore_name = fore_name + ', ' + title
            except AttributeError:
                last_name = re.sub(r'\,.*', '', author)
                fore_name = re.sub(r'.*\, ', '', author)
            if re.search(r' ', fore_name):
                first_name = re.sub(r' .*', '', fore_name)
                middle_name = re.sub(r'.* ', '', fore_name)
            elif re.search(r'^\w\.\w\.', fore_name):
                first_name = re.sub(r'^(\w\.).*', r'\1', fore_name)
                middle_name = re.sub(r'^\w\.', '', fore_name)
            else:
                first_name = fore_name
        if item.has_key('u'):
            affiliation = item['u']
        if item.has_key('m'):
            email = item['m']
        if item.has_key('j'):
            orcid = item['j']
            if not re.search(r'ORCID:', orcid):
                orcid = None
            else:
                orcid = re.sub(r'ORCID:', '', orcid)
        ET.SubElement(authors_detail, 'first_name').text = first_name
        ET.SubElement(authors_detail, 'middle_name').text = middle_name
        ET.SubElement(authors_detail, 'last_name').text = last_name
        ET.SubElement(authors_detail, 'affiliation').text = affiliation
        ET.SubElement(authors_detail, 'private_email').text = email
        ET.SubElement(authors_detail, 'orcid_id').text = orcid

def get_corporate_author(recid):
    """Check to see if there is a corporte author and return it."""
    try:
        return get_fieldvalues(recid, "110__a")[0]
    except IndexError:
        return None

def get_author_first(recid):
    """Get authors as a long string, truncate at 10."""
    try:
        return get_fieldvalues(recid, "100__a")[0] + "; et al."
    except IndexError:
        return None
    #author_list = get_fieldvalues(recid, "100__a") \
    #        + get_fieldvalues(recid, "700__a")
    #if len(author_list) <= 10 and len(author_list) > 0 and False:
    #    return '; '.join([unicode(a, "utf-8") for a in author_list])
    #if len(author_list) > 500:
    #    return author_list[0] + "; et al."

def get_author_number(recid):
    """Gets number of authors."""
    author_list = get_fieldvalues(recid, "700__a")
    try:
        return len(author_list)
    except IndexError:
        return 0

def get_authors(recid, authors):
    """Get authors as individuals."""
    tags = ['100__', '700__']
    for tag in tags:
        get_author_details(recid, authors, tag)

def get_collaborations(recid):
    """Get the collaboration information"""
    try:
        collaborations = get_fieldvalues(recid, "710__g")
        return '; '.join([unicode(a, "utf-8") for a in collaborations])
    except StandardError:
        return None

def get_abstract(recid):
    """Get abstract if it exists."""
    try:
        abstract = get_fieldvalues(recid, "520__a")[0]
        if len(abstract) > 4990:
            abstract = abstract[:4990] + '...'
        return abstract
    except IndexError:
        return None

def get_reports(recid):
    """Get reports as a long string."""
    reports = get_fieldvalues(recid, "037__z") \
            + get_fieldvalues(recid, "037__a")
    return '; '.join(r for r in reports)

def get_product_type(recid):
    """Get product type in OSTI format."""
    type_dict = TYPE_DICT
    product_type = '??'
    report_string = get_reports(recid)
    for key in type_dict:
        pattern = 'FERMILAB-' + key
        if re.search(pattern, report_string):
            product_type = type_dict[key]
    if VERBOSE:
        print product_type
    return product_type

def get_subject_categories(recid):
    """Convert INSPIRE subject codes to OSTI codes."""
    categories = get_fieldvalues(recid, '65017a')
    try:
        osti_categories = []
        for category in categories:
            for key in DOE_SUBJECT_CATEGORIES_DICT:
                if re.search(key, category.lower()):
                    osti_categories.append(DOE_SUBJECT_CATEGORIES_DICT[key])
        return '; '.join(c for c in set(osti_categories))
    except IndexError:
        return None

def get_affiliations(recid, long_flag):
    """Get affiliations using OSTI institution names."""
    affiliations = get_fieldvalues(recid, "100__u") \
                 + get_fieldvalues(recid, "700__u")
    affiliations.append("Fermilab")
    doe_affs = []
    doe_affs_long = []
    for aff in set(affiliations):
        #if aff in INSPIRE_AFF_DICT and not INSPIRE_AFF_DICT[aff] in doe_affs:
        if aff in INSPIRE_AFF_DICT:
            doe_affs.append(INSPIRE_AFF_DICT[aff])
            doe_affs_long.append(DOE_AFF_DICT[INSPIRE_AFF_DICT[aff]])
    if long_flag:
        return '; '.join([a for a in doe_affs_long])
    else:
        return '; '.join([a for a in doe_affs])

def get_date(recid, product_type):
    """Get date in format mm/dd/yyyy, yyyy or yyyy Month."""
    try:
        date = get_fieldvalues(recid, '260__c')[0]
    except IndexError:
        try:
            date = get_fieldvalues(recid, '269__c')[0]
        except IndexError:
            try:
                date = get_fieldvalues(recid, '502__d')[0]
            except IndexError:
                date = '1900'
    try:
        date_object = datetime.datetime.strptime(date, '%Y-%m-%d')
        date = date_object.strftime('%m/%d/%Y')
    except ValueError:
        try:
            date_object = datetime.datetime.strptime(date, '%Y-%m')
            date = date_object.strftime('%Y %B')
            if product_type in ['TR', 'TD', 'JA']:
                date = date_object.strftime('%m/01/%Y')
        except ValueError:
            if product_type in ['TR', 'TD', 'JA']:
                date = '01/01/' + str(date)
    return date

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def create_xml(recid, records):
    """
    Creates xml entry for a recid and feeds it to list of records.
    Tests to see if all the necessary information is present.
    If an accepted version has already been submitted, returns None.
    """

    [url, accepted] = get_url(recid)
    if url is None:
        return None
    osti_id = get_osti_id(recid)
    if osti_id:
        file_txt = DIRECTORY + '/' + str(osti_id) + '.txt'
        file_pdf = DIRECTORY + '/' + str(osti_id) + '.pdf'
        if os.path.isfile(file_txt) or os.path.isfile(file_pdf):
            #print "Already sent AM for", osti_id
            return None
    product_type = get_product_type(recid)
    if accepted:
        product_type = 'JA'
    journal_info = get_pubnote(recid)
    if product_type == 'JA' and journal_info[0] == None:
        return None
    #Begin building record
    record = ET.SubElement(records, 'record')
    if osti_id:
        ET.SubElement(record, 'osti_id').text = osti_id
        dict_osti_id = {'osti_id':osti_id}
        ET.SubElement(record, 'revdata', dict_osti_id)
        ET.SubElement(record, 'revprod', dict_osti_id)
    else:
        ET.SubElement(record, 'new')
    ET.SubElement(record, 'site_input_code').text = \
        DOE_FERMILAB_DICT['site_input_code']
    if product_type == 'JA':
        if accepted:
            ET.SubElement(record, 'journal_type').text = 'AM'
            #print 'Accepted Manuscript', recid, osti_id
            create_osti_id_pdf(recid, osti_id)
        else:
            ET.SubElement(record, 'journal_type').text = 'FT'
    ET.SubElement(record, 'product_type').text = product_type
    access_limitation = ET.SubElement(record, 'access_limitation')
    ET.SubElement(access_limitation, 'unl')
    if not accepted:
        ET.SubElement(record, 'site_url').text = url
    ET.SubElement(record, 'title').text = get_title(recid)
    collaborations = get_collaborations(recid)
    author_number = get_author_number(recid)

    corporate_author = get_corporate_author(recid)
    if corporate_author:
        author = ET.SubElement(record, 'author')
        author.text = corporate_author

    elif author_number > 20:
        author = ET.SubElement(record, 'author')
        author_first = get_author_first(recid)
        if author_first:
            author.text = get_author_first(recid)
    else:
        authors = ET.SubElement(record, 'authors')
        get_authors(recid, authors)
    ET.SubElement(record, 'contributor_organizations').text = \
        collaborations
    ET.SubElement(record, 'report_nos').text = get_reports(recid)
    for key in DOE_FERMILAB_DICT:
        ET.SubElement(record, key).text = DOE_FERMILAB_DICT[key]
    ET.SubElement(record, 'description').text = get_abstract(recid)
    ET.SubElement(record, 'originating_research_org').text = \
        get_affiliations(recid, True)
    #journal_info = get_pubnote(recid)
    #if product_type == 'JA' and journal_info[0] == None:
    #    return None
    journal_elements = ['journal_name', 'journal_volume', 'journal_issue',
                        'product_size', 'doi']
    i_count = 0
    for journal_element in journal_elements:
        ET.SubElement(record, journal_element).text = journal_info[i_count]
        i_count += 1
    if product_type == 'CO':
        ET.SubElement(record, 'conference_information').text = \
        get_conference(recid)
    ET.SubElement(record, 'other_identifying_nos').text = str(recid)
    ET.SubElement(record, 'publication_date').text = \
        get_date(recid, product_type)
    ET.SubElement(record, 'language').text = \
        get_language(recid)
    ET.SubElement(record, 'subject_category_code').text = \
        get_subject_categories(recid)
    ET.SubElement(record, 'released_date').text = \
          CHICAGO_TIMEZONE.fromutc(datetime.datetime.utcnow()).\
          strftime('%m/%d/%Y')
    return 1

def main(recids):
    """Generate OSTI posting from a recid or an INSPIRE search."""

    counter = 0
    if not recids:
        print "No, that search did not work"
        return None
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '.out', filename)
    output = open(filename,'w')

    #recids = [1400805, 1373745, 1342808, 1400935]
    records = ET.Element('records')
    for recid in recids:
        if counter > ENDING_COUNTER:
            break
        if check_already_sent(recid):
            if VERBOSE:
                print "Already have", recid
            continue
        record_test = create_xml(recid, records)
        if record_test:
            counter += 1
        #if get_url(recid)[0]:
        #    if get_product_type(recid) == 'JA' and \
        #    get_pubnote(recid)[0] == None:
        #        pass
        #    else:
        #        create_xml(recid, records)
        #        counter += 1
    if TEST:
        print prettify(records)
    else:
        #output.write(XML_PREAMBLE)
        output.write(prettify(records))
    output.close()
    print "Number of records:", counter

def find_records(search_input=None):
    """
    Finds records to send email to.
    """

    print """
    Let's do a HEP search in INSPIRE format
    """
    if SEARCH:
        search_input = SEARCH
    elif not search_input:
        search_input = raw_input("Your search? ").lower()
    if len(search_input) > 3:
        if re.search(r'ignore', search_input):
            search = re.sub(r'ignore', '', search_input)
            search = search + ' 037:fermilab*'
        else:
            search = search_input + ' 037:fermilab* -035__9:osti'
    else:
        print "That's not a search. Game over."
        return None
    print search
    result = perform_request_search(p=search, cc='HEP')
    if len(result) > 0:
        log = open(LOGFILE, 'a')
        date_time_stamp = \
            CHICAGO_TIMEZONE.fromutc(datetime.datetime.utcnow()).\
            strftime('%Y-%m-%d %H:%M:%S')
        date_time_stamp = date_time_stamp + ' ' + search + ' : '\
                    + str(len(result)) + '\n'
        log.write(date_time_stamp)
        log.close()
        result.reverse()
        return result
    else:
        print "No results found."
        return None

if __name__ == '__main__':
    try:
        if sys.argv[1:][0] == 'i':
            RECIDS = find_records(ACCEPTED_SEARCH)
        elif sys.argv[1:][0] == 'a':
            RECIDS = find_records('     ')
    except IndexError:
        pass
    if not RECIDS:
        RECIDS = []
        try:
            RECID = int(sys.argv[1:][0])
            RECIDS.append(RECID)
        except StandardError:
            RECIDS = find_records()
    try:
        main(RECIDS)
    except KeyboardInterrupt:
        print 'Exiting'

