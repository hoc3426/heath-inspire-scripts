#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Script for adding OSTI IDs to INSPIRE records after using OSTI Web Service.
"""

import re
import cgi
import sys
import xml.etree.ElementTree as ET

from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field

TEST = False
TEST = True
DOCUMENT = 'tmp_osti.out'

if TEST:
    #DOCUMENT = 'test.xml'
    pass

def find_recid(id):
    if not id.isdigit():
       print "Invalid ID: " , id
       return False
    search = "001:" + id + " or 970__a:SPIRES-" + id + " 037:FERMILAB*"        
    x = perform_request_search(p = search, cc = 'HEP')
    if len(x) == 1:
        recid = x[0]
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
    except:
        print "Something wrong: " + search                    
        return False


def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    tree = ET.parse(DOCUMENT)
    root = tree.getroot()
    #for child in root:
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
                print 'CANNOT print record', child.attrib
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

