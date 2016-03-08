#!/usr/bin/python
# -*- coding: UTF-8 -*-
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from hep_convert_email_to_id import get_hepnames_recid_from_email
from invenio.search_engine import print_record
from hep_convert_email_to_id import find_inspire_id_from_record
import re

fileName = "directory.html"
search = '110:/carleton/'
EXPERIMENT = 'DES'
search = '693__e:' + EXPERIMENT
x = perform_request_search(p=search, cc='HepNames')


fileName = 'tmp_hepnames_collaboration_check.out'
output = open(fileName,'w')

for r in x:
    email = get_fieldvalues(r,'371__m')
    if email: email = email[0]
    else: email = ' '
    aff = get_fieldvalues(r,'371__a')
    if aff: aff = aff[0]
    else: aff = ' '
    name = get_fieldvalues(r,'100__a')[0]
    id = find_inspire_id_from_record(r)
    print name
    print email
    print id
    person = name + '|' + aff + '|' + email + '|' + id + '\n'
    output.write(person)
    #output.write(print_record(r,ot=['100','371','035'],format='hm'))
output.close()
