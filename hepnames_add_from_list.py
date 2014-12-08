#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unicodedata
import re
import os
import string

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import get_record
from invenio.search_engine import get_all_field_values
from invenio.search_engine import print_record
from invenio.bibformat_engine import BibFormatObject
from hep_convert_email_to_id import get_hepnames_recid_from_email
from hep_convert_email_to_id import find_inspire_id_from_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field
#from afftranslator2 import bestmatch

from hepnames_add_from_list_authors import AUTHORS
EXPERIMENT = 'FNAL-E-0974'

def create_xml(author,email,af,experiment):
    common_fields = {}
    common_tags = {}
    author2 = re.sub(r'(.*)\, (.*)',r'\2 \1', author)
    common_tags['980__'] = [('a', 'HEPNAMES')]
    common_tags['100__'] = [('a', author), ('q', author2), ('g', 'ACTIVE')]
    common_tags['371__'] = [('m', email),('a', af),('z', 'current')]
    common_tags['693__'] = [('e', experiment),('z', 'current')]
    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    #return common_fields
    print print_rec(common_fields)



search = "371__u:/a/ or 371__u:/e/ or 371__u:/i/ or 371__u:/o/ or 371__u:/u/"



x = perform_request_search(p=search,cc='HepNames')
#x = x[:5]
print len(x)

fileName = 'tmp_junk.out'
output = open(fileName,'w')
for author in AUTHORS:
    au = author[1] 
    email = author[0]
    email = email.lower()
    #af = author[2]
    af = ''
    #au = re.sub(r'(.*[A-Z][A-Z]) ([A-Z][a-z].*)',r'\1, \2',au)
    #au = re.sub(r'(.*[a-z]) ([A-Z][A-Z].*)',r'\2, \1',au)
    #au = string.capwords(au)    
    au = re.sub(r'(.*) (\S+)',r'\2, \1', au)
    search = "find a " + au
    x = perform_request_search(p=search,cc='HepNames')
    hepnames_record = get_hepnames_recid_from_email(email)
    #print search,' : ',len(x)
    if hepnames_record:
        search = "001:" + str(hepnames_record) + " -693__e:" + EXPERIMENT
        x = perform_request_search(p=search,cc='HepNames')
        if len(x) == 1:
            print x[0]
    elif len(x) < 1 and not hepnames_record:
        if af:
            bm = bestmatch(af,'ICN')
            aflist = bm[0]
            af = aflist[1]
        create_xml(au, email, af, EXPERIMENT)

    #output.write(print_record(r,ot=['001','371'],format='xm'))
output.close()


if False:
  authorId = None
  authorName = None
  email = None
  authorId = find_inspire_id_from_record(r)
  authorName = get_fieldvalues(r,'100__a')[0]
  email = get_fieldvalues(r,'371__m')
  if authorName : printLine = authorName
  if email : 
    email = email[0]
    printLine = printLine  + ' | ' + email
  else :
    email = None
  if authorId : printLine = printLine  + ' | ' + authorId
  #print authorName, '|', r, '|', email, '|', authorId
  #printLine = authorName  + ' | ' + email  + ' | ' + authorId
  #print printLine
  search = 'find ea ' + authorName
  y = perform_request_search(p=search,cc='HepNames')
  if len(y) > 1:
    for rr in y:
      print rr,authorName


