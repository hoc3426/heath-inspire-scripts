#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import cgi
import sys

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import print_record
from invenio.bibrecord import print_rec, record_add_field

def osti_add_id():
    search = "037__a:FERMILAB* 8564_y:OSTI -035__9:OSTI"
    x = perform_request_search(p = search, cc = 'HEP')
    x = x[:1000]
    string = ''
    for r in x:
        record = {}
        record_add_field(record, '001', controlfield_value=str(r))
        for u in get_fieldvalues(r, '8564_u'):
            if re.search('osti.gov', u): 
                matchObj = re.search(r'(\d+)', u)
                if matchObj : 
                    osti_id = matchObj.group(1)
                    new_id  = [('a', osti_id), ('9', 'OSTI')]
                    record_add_field(record, '035', '', '', subfields=new_id)
                    string = string + print_rec(record)
    return string
  
def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    update = osti_add_id()
    if update: output.write(update)
    output.write('</collection>')
    output.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
    
