#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Script for adding OSTI IDs to INSPIRE records after using OSTI Web Service.
"""

import os
import re
import xml.etree.ElementTree as ET
import urllib2
import PyPDF2
from PyPDF2 import PdfFileReader

from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field
from osti_web_service import get_url


TEST = False
TEST = True
DOCUMENT = 'tmp_osti.out'
DIRECTORY = '/afs/cern.ch/project/inspire/TEST/hoc/osti/'

if TEST:
    #DOCUMENT = 'test.xml'
    pass

RECIDS = []

def create_osti_id_pdf(recid, osti_id):
    try:
        url = get_url(recid)[0]
    except IndexError:
        print "No url on", recid
        return None
    response = urllib2.urlopen(url)
    pdf = response.read()
    try:
        PyPDF2.PdfFileReader(open(pdf, "rb"))
    except PyPDF2.utils.PdfReadError:
        print "PDF invalid for", recid
        return None
    final_pdf = DIRECTORY + str(recid) + ".pdf"
    if os.path.exists(final_pdf):
        print "Already have PDF for", recid
        return None
    output = open(final_pdf, 'w')
    output.write(pdf)
    output.close()

def find_recid(mystery_id):
    """
    Takes an ID, could be a recid or an irn, and returns a recid
    """

    if not mystery_id.isdigit():
        print "Invalid ID: " , mystery_id
        return False
    search = "001:" + mystery_id + \
             " or 970__a:SPIRES-" + mystery_id + " 037:FERMILAB*"
    result = perform_request_search(p = search, cc = 'HEP')
    if len(result) == 1:
        recid = result[0]
        if recid in RECIDS:
            return False
        else:
            RECIDS.append(recid)
            return recid
    else:
        return False

def create_xml(osti_id, inspire_id):
    """
    The function checks if the OSTI ID should be added to INSPIRE.
    If so, it builds up that information.
    """

    osti_id = str(osti_id)
    recid = str(inspire_id)
    search = "001:" + recid
    result = perform_request_search(p = search, cc = 'HEP')
    if len(result) != 1:
        print 'No such INSPIRE record', recid
        return None
    search = "001:" + recid + " 035__a:" + osti_id
    result = perform_request_search(p = search, cc = 'HEP')
    if len(result) == 1:
        return None
    search = "035__a:" + str(osti_id)
    result = perform_request_search(p = search, cc = 'HEP')
    if len(result) == 1:
        print 'OSTI ID', osti_id, 'already on', result[0]
        return None
    search = "001:" + recid + " -035__9:OSTI"
    if TEST:
        print search
    result = perform_request_search(p = search, cc = 'HEP')
    if not len(result) == 1:
        print 'Problem with', recid, osti_id
        return False
    if TEST:
        print result
    record = {}
    record_add_field(record, '001', controlfield_value=str(recid))
    new_id  = [('a', osti_id), ('9', 'OSTI')]
    record_add_field(record, '035', '', '', subfields=new_id)
    try:
        return print_rec(record)
        create_osti_id_pdf(recid, osti_id)
    except:
        print "Something wrong: " + search
        return False


def main():
    """
    Takes the output from an OSTI web push and appends the
    OSTI IDs to the INSPIRE records.
    """

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    tree = ET.parse(DOCUMENT)
    root = tree.getroot()
    for record in root.findall('record'):
        print record.tag
        osti_id = record.find('osti_id').text
        inspire_id = record.find('other_identifying_nos').text
        record_update = create_xml(osti_id, inspire_id)
        if record_update:
            try:
                if TEST:
                    print record_update
                else:
                    output.write(record_update)
            except:
                print 'CANNOT print record', record.attrib
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

