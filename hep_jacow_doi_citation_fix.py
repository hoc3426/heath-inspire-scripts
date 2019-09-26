"""
   Resolve implicit citation of JACoW DOIs, e.g.
   text:
     $$mpresented at the IPAC'19, Melbourne, Australia, May,
     paper TUPGW091, this conference
   becomes:
     $$mpresented at the IPAC'19, Melbourne, Australia, May,
     paper TUPGW091, this conference$$adoi:10.18429/JACoW-IPAC2019-TUPGW091
   url:
     "accelconf.web.cern.ch/AccelConf" == "jacow.org"
     $$uhttp://accelconf.web.cern.ch/AccelConf/IPAC2017/papers/tuocb3.pdf
   becomes:
     $$uhttp://accelconf.web.cern.ch/AccelConf/IPAC2017/papers/tuocb3.pdf
     $$adoi:10.18429/JACoW-IPAC2017-TUOCB3

  Fix for malformed DOIs, e.g.
  ref:
    999C5a:doi:10.18429/JACoW-IBIC18-WEPC06
    999C5a:doi:10.18429/JACoW-IPAC2017MOPVA060
    999C5a:doi:10.18429/JACoW-IPAC2018-MOZ-GBD1
    999C5a:doi:10.18429/JACoW-NAPAC2016-MOPOB69.pdf
  becomes
    999C5a:doi:10.18429/JACoW-IBIC2018-WEPC06
    999C5a:doi:10.18429/JACoW-IPAC2017-MOPVA060
    999C5a:doi:10.18429/JACoW-IPAC2018-MOZGBD1
    999C5a:doi:10.18429/JACoW-NAPAC2016-MOPOB69

"""

from datetime import datetime
import re
from invenio.search_engine import get_all_field_values, get_record, \
                                  perform_request_search
from invenio.bibrecord import print_rec, record_get_field_instances, \
                              record_add_field
#from hep_jacow_doi_citation_fix_input import SEARCH

TALK_REGEX = re.compile(r'^(MO|TU|WE|TH|FR)[A-Z]{1,8}\d{1,8}')
URL_REGEX = re.compile(
r'https?://(accelconf.web.cern.ch|jacow.org).*/(\w+\d{4})/papers/(\w+)\.pdf',
re.IGNORECASE)

JACOW_CONFERENCES = ["ABDW", "APAC", "BIW", "COOL", "CYCLOTRONS",
"DIPAC", "ECRIS", "EPAC", "ERL", "FEL", "HB", "HIAT", "IBIC",
"ICALEPCS", "ICAP", "IPAC", "LINAC", "MEDSI", "NAPAC", "PAC", "PCaPAC",
"RuPAC", "SAP", "SRF"]
JACOW_CONFERENCES = sorted(JACOW_CONFERENCES, key=len, reverse=True)

def get_jacow_dois():
    """Return all the JACoW DOIs INSPIRE has."""

    jacow_dois = set()
    for doi in get_all_field_values('0247_a'):
        if doi.startswith('10.18429/JACoW-'):
            jacow_dois.add('doi:' + doi)
    return jacow_dois

JACOW_DOIS = get_jacow_dois()
CURRENT_YEAR = datetime.now().year

def jacow_citation_statistics():
    """Show the tally of citations for JACoW papers."""

    citation_dict = {}
    for citation_count in range(0, 50):
        search = '0247_9:jacow cited:' + str(citation_count)
        result = perform_request_search(p=search, cc='HEP')
        citation_dict[citation_count] = len(result)

    print datetime.now()
    total = 0
    for key, value in citation_dict.items():
        total += key*value
        if value:
            print "{0:3d} {1:6d}".format(key, value)
    print 'Total', total

def create_jacow_doi(conf, year, talk):
    """Takes candidate for e.g. IPAC2016 and returns normalized form."""

    if conf not in JACOW_CONFERENCES:
        return None
    if int(year) in range(59, 100):
        year = '19' + year
    elif len(year) == 2:
        year = '20' + year
    if int(year) not in range(1959, CURRENT_YEAR + 1):
        return None
    doi = 'doi:10.18429/JACoW-' + conf + year + '-' + talk
    if doi in JACOW_DOIS:
        return doi
    return None

def fix_jacow_doi(doi):
    '''
    999C5a:doi:10.18429/JACoW-IBIC18-WEPC06
    999C5a:doi:10.18429/JACoW-IPAC2017MOPVA060
    999C5a:doi:10.18429/JACoW-IPAC2018-MOZ-GBD1
    999C5a:doi:10.18429/JACoW-NAPAC2016-MOPOB69.pdf
    '''

    doi = re.sub(r'doi:10.18429/JAC[oO]W-?', '', doi)
    doi = re.sub(r'^([A-z]+)(\d+)\-?(\w+)\-?(\w+).*', r'\1 \2 \3\4', doi)
    return extract_jacow_doi(doi)

def extract_jacow_doi(ref):
    """Takes a reference and looks to see if a JACoW talk is cited."""

    conf = year = talk = None

    match_obj = URL_REGEX.match(ref)
    if match_obj:
        conf = match_obj.group(2)
        year = re.sub(r'\D', '', conf)
        conf = re.sub(r'\d', '', conf)
        talk = match_obj.group(3).upper()
        return create_jacow_doi(conf, year, talk)

    for jacow_conf in JACOW_CONFERENCES:
        if jacow_conf in ref:
            conf = jacow_conf
            break
    for word in re.split(r'\W', ref):
        if re.match(TALK_REGEX, word):
            talk = word
        if re.match(r'\b[5-9,0,1]\d\b', word) or \
           re.match(r'\b(19|20)\d\d\b', word):
            year = word
    if conf and talk and year:
        return create_jacow_doi(conf, year, talk)
    return None

def create_xml(recid, tags):
    """
    Replaces an email with an INSPIRE ID and an ORCID where possible
    """

    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    #We don't want to update records that already have the DOI.
    flag_instances = []
    for (tag, field_instance) in \
            [(tag, field_instance) for tag in tags \
             for field_instance in record_get_field_instances(record, \
             tag[0:3], tag[3], tag[4])]:
        correct_subfields = []
        flag_instance = False
        for code, value in field_instance[0]:
            if code == 'a' and value.startswith('doi:10.18429/JAC'):
                if value not in JACOW_DOIS:
                    doi = fix_jacow_doi(value)
                    if doi:
                        value = doi
                        flag_instance = True
            if code in ('m', 'u', 'x'):
                doi = extract_jacow_doi(value)
                if doi:
                    if ('a', doi) in correct_subfields:
                        flag_instance = False
                    else:
                        correct_subfields.append(('a', doi))
                        flag_instance = True
            if (code, value) in correct_subfields:
                flag_instance = False
            else:
                correct_subfields.append((code, value))
                #flag_instance = True
        flag_instances.append(flag_instance)
        record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
            subfields=correct_subfields)
    if any(flag_instances):
        return print_rec(correct_record)
    return None

def main():
    """
    Run through a search to find potential JACoW citations
    and convert them to DOIs.
    """

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename, 'w')
    output.write('<collection>\n')
    counter = 0
    search = '999C5a:doi:10.18429/JAC* or 65017a:accelerators'
    result = perform_request_search(p=search, cc='HEP')
    for recid in result:
        xml = create_xml(recid, ['999C5'])
        if xml:
            output.write(xml)
            counter += 1
    output.write('</collection>')
    output.close()
    print 'Number of records examined:', len(result)
    print 'Number of records updated:', counter
    print filename
    jacow_citation_statistics()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

