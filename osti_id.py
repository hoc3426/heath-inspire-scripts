#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import cgi
import sys

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import print_record
from invenio.bibrecord import print_rec, record_add_field

def osti_add_url(string):
    osti_base_url = 'http://www.osti.gov/scitech/biblio/'
    matchObj = re.match(r'^(\d+)\s+(\d+)', string)
    if matchObj :
        inspire_id = matchObj.group(1)
        osti_id    = matchObj.group(2)
        #print "Check: " + inspire_id + " " + osti_id
        search_id = "001:" + inspire_id + " or 970__a:SPIRES-" + inspire_id
        search_id  = search_id + " 037__a:FERMILAB* "
        search_osti_url = " 8564_y:OSTI "
        search_osti_id  = " 8564_u:/" + osti_id + "/"      
        search = search_id + search_osti_url + search_osti_id
        x = perform_request_search(p = search, cc = 'HEP')
        if len(x) == 1:
            #print "       " + inspire_id + " " + osti_id + " match"
            return
        if len(x) == 0:
            search = search_id + search_osti_url
            y = perform_request_search(p = search, cc = 'HEP')
            if len(y) == 1:
                #print 'Duplicate OSTI ID?', osti_id, search
                recid = y[0]
                reportValues = get_fieldvalues(recid,'037__a')
                report = ''
                existing_osti_id = ''
                for y in reportValues:
                    if re.search('FERMILAB', y): report = y
                for u in get_fieldvalues(recid, '8564_u'):
                    if re.search('osti.gov', u):
                        matchObj = re.search(r'(\d+)', u)
                        if matchObj :
                            existing_osti_id = matchObj.group(1)
                print report, existing_osti_id, osti_id
            elif len(y) == 0:
                search = search_id
                z =  perform_request_search(p = search, cc = 'HEP')
                if len(z) == 1:
                    recid = z[0]
                    record = {}
                    record_add_field(record, '001', controlfield_value=str(recid))
                    osti_url = osti_base_url + osti_id
                    new_id  = [('a', osti_id), ('9', 'OSTI')]
                    new_url = [('u', osti_url), ('y', 'OSTI')]
                    record_add_field(record, '035', '', '', subfields=new_id)
                    record_add_field(record, '856', '4', '', subfields=new_url)
                    return print_rec(record)
                else:
                    print "Something wrong: " + search                    
        else:
            #print "Check this one: \n  ", search, "\n  ",string 
            #search = "001:" + inspire_id + " or 970__a:SPIRES-" + inspire_id
            #search = search + " and 037__a:FERMILAB*"
            #x = perform_request_search(p = search, cc = 'HEP')
            print len(x), search

def main(input):
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    if input:
        output_data = osti_add_url(input)
        if output_data:
            output.write(output_data)
    else:
        try:
            for i in open('osti.in','r').readlines():
                output_data = osti_add_url(i)
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
    
