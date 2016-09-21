#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import cgi
import sys

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import print_record
from invenio.bibrecord import print_rec, record_add_field

VERBOSE = True
VERBOSE = False
RECIDS = []

INPUT_FILE = 'FNALData.txt'
INPUT_FILE = 'FNALData_thesis.txt'
#INPUT_FILE = 'tmp_o.txt'
INPUT_FILE = 'tmp_osti_elem.txt'
#INPUT_FILE = 'tmp_osti_accel.txt'

def find_recid(id):
    id = re.sub(r';', '', id)
    if id.isdigit():
        search = "001:" + id + " or 970__a:SPIRES-" + id + \
                 " 037:FERMILAB*"        
        search = "035__a:" + id + " 035__9:osti"
        #print search
    elif re.search(r'FERMILAB', id):
        id = re.sub(r'\/', '-', id)
        id = re.sub(r'[\-]+', '-', id)
        id = re.sub(r'\-DO$', '-DI', id)
        search = "037:" + id
    elif re.search(r'10\.\d+\/', id):
        search = "0247_a:" + id
    x = perform_request_search(p = search, cc = 'HEP')
    if len(x) == 1:
        recid = x[0]
        if recid in RECIDS:
            print 'Duplicate', id, recid
            return None
        else:
            RECIDS.append(recid)
            return recid
    else:
        return None

def add_osti_id(string):
    if re.search(r'\s*Video\s*NA\s*NA', string):
        return False
    elif re.search(r'duplicat[eion]+ of OSTI ID', string):    
        return False
    elif re.search(r'\tSoftware\t', string):
        return False
    elif re.match(r'^\s*(\d+).*\"FNAL\",\"\d+\"$', string):
        return False

    recid = None
    report_num = None
    osti_id = None
    doi = None
    match_obj_1 = False
    match_obj_2 = False
    match_obj_3 = False

    string = re.sub(r'[\-]+', '-', string)
    string = re.sub(r'FERMILAB[ \-]+', 'FERMILAB-', string)
    string = re.sub(r'FNAL\/C\-\-(\d+)\/([\d\-A-Z]+)', \
                    r'FERMILAB-CONF-\1-\2', string)
    string = re.sub(r'FNAL[ ]\-', 'FERMILAB-', string)
    try:
        report_num = re.search(r'(FERMILAB\-\S+\d{2,}[\w\-]+)', string).group(1)
        report_num = re.sub(r'\/', '-', report_num)
        recid = find_recid(report_num) 
    except:
        pass
    try:
        osti_id = re.search(r'^FNAL[\t\s]*(\d+)', string).group(1)
        #print '****', osti_id
        if not recid:
            recid = find_recid(osti_id)
    except:
        pass
    try:
        doi = re.search(r'(10\.\d+\/\S+)', string).group(1)
        if not recid:
            recid = find_recid(doi)
    except:
        pass
    if not osti_id:
        return False
    if not any([osti_id, doi, recid]):
        print 'Boo', osti_id, report_num, doi, recid, '\n', string
    elif not recid:
        print 'Hoo', osti_id, report_num, doi, recid, '\n', string
        #for x in [report_num, osti_id, doi]:
        #    if x:
        #        print x, find_recid(x)
        return False


    #if not recid:
    #    print "Cannot find valid recid:", report_num, doi, osti_id, string
    #    return False    
    search = "001:" + str(recid) + " -035__9:OSTI"
    if VERBOSE:
        print search
    result = perform_request_search(p = search, cc = 'HEP')
    if not len(result) == 1:
        search_other = "035__a:" + osti_id + " 035__9:OSTI"
        result_other = perform_request_search(p = search, cc = 'HEP')
        try:
           recid_other = result_other[0]
           if recid != recid_other:
               print "OSTI ID", osti_id, "on record", result[0], "not", recid
        except IndexError:
           pass 
        return False   
    if VERBOSE:
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

def main(input):
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    if input:
        output_data = add_osti_id(input)
        if output_data:
            output.write(output_data)
    else:
        try:
            for i in open(INPUT_FILE, 'r').readlines():
                output_data = add_osti_id(i)
                if output_data:
                    output.write(output_data)
        except IOError as e:
            print "An error\n"
            print("({})".format(e))
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    search = sys.argv
    try:
        if len(search) == 1 :
            main(0)
        elif len(search) == 2:
            search = search[1:][0]
            main(search)
    except KeyboardInterrupt:
        print 'Exiting'
    
