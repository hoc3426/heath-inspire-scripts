#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unicodedata
import re
import os
import string
import random

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

from hepnames_fermilab_aff_from_email import aff_from_email
from hepnames_add_from_list_authors import AUTHORS, EMAILS

EXPERIMENT = 'FNAL-E-0974'
EXPERIMENT = 'AUGER'
EXPERIMENT = 'BNL-RHIC-STAR'
EXPERIMENT = 'DUNE'
EXPERIMENT = 'GERDA'
EXPERIMENT = 'EXO-200'
EXPERIMENT = 'PEN'
EXPERIMENT = 'PADME'
EXPERIMENT = 'XENON1T'
EXPERIMENT = 'Baby-MIND'
EXPERIMENT = 'HARPO'
EXPERIMENT = None

SOURCE = 'Fermilab'
#SOURCE = 'HARPO'

#INSPIRE = 72053
#INSPIRE = 72499
#INSPIRE = 72524
#INSPIRE = 73359
#INSPIRE = 73383
INSPIRE = 73787

if EMAILS:
    emails_unknown = []
    for email in EMAILS:
        recid = get_hepnames_recid_from_email(email)
        if recid:  
            search = '001:' + str(recid)  + ' 693__e:' + EXPERIMENT
            result = perform_request_search(p=search, cc='HepNames')
            if len(result) == 0:
                print 'or', recid
        else:
            emails_unknown.append(email)
    for email in emails_unknown:
        print email
    quit()

def create_xml(author,email,af,experiment,inspire_id):
    common_fields = {}
    common_tags = {}
    author2 = re.sub(r'(.*)\, (.*)',r'\2 \1', author)
    common_tags['980__'] = [('a', 'HEPNAMES')]
    common_tags['100__'] = [('a', author), ('q', author2), ('g', 'ACTIVE')]
    aff = aff_from_email(email)
    if aff:
        common_tags['371__'] = [('m', email), ('a', aff), ('z', 'current')]
    else:
        common_tags['371__'] = [('m', email), ('z', 'current')]
    if experiment:
        common_tags['693__'] = [('e', experiment), ('z', 'current')]
    common_tags['035__'] = [('9', 'INSPIRE'), ('a', inspire_id)]
    if SOURCE:
        common_tags['670__'] = [('a', SOURCE)]

    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    #return common_fields
    return print_rec(common_fields)



search = "371__u:/a/ or 371__u:/e/ or 371__u:/i/ or 371__u:/o/ or 371__u:/u/"

fileName = 'tmp_hepnames_add_from_list.out'
#input = open('tmp.bnl.in', 'r')
output = open(fileName,'w')
#for line in input.readlines():
if False:
    line = re.sub(r'\n', '', line)
    try:
        match_object = re.match(r'(.*)\t+(.*)\t+(.*)\t+(.*)\t+(.*)', line)
        fname = match_object.group(1)
        lname = match_object.group(2)
        id    = match_object.group(3)
        aff   = match_object.group(4)
        email = match_object.group(5)
        recid = get_hepnames_recid_from_email(email)
        inspire = find_inspire_id_from_record(recid)
        line = line + '\t' + inspire
        #print line
        #output.write(line)
    except TypeError:
        print line
        pass
    except AttributeError:
        print line
        pass
    line = line + '\n'
    output.write(line)
#input.close()
output.close()


x = perform_request_search(p=search,cc='HepNames')
#x = x[:5]
#print len(x)

fileName = 'tmp_hepnames_add_from_list.out'
output = open(fileName,'w')
for author in AUTHORS:
    au = author[0] 
    email = author[1]
    email = email.lower()
    #af = author[1]
    af = ''
    #au = re.sub(r'(.*[A-Z][A-Z]) ([A-Z][a-z].*)',r'\1, \2',au)
    #au = re.sub(r'(.*[a-z]) ([A-Z][A-Z].*)',r'\2, \1',au)
    #au = string.capwords(au)    
    #au = re.sub(r'\s+', r' ', au)
    if "," in au:
        pass
    else:
        au = re.sub(r'(.*) (\S+)',r'\2, \1', au)
    #search = "find a " + au
    #x = perform_request_search(p=search,cc='HepNames')
    recid = get_hepnames_recid_from_email(email)
    #print search,' : ',len(x)
    if recid and EXPERIMENT == None:
        continue
    if recid and EXPERIMENT:
        search = "001:" + str(recid) + " -693__e:" + EXPERIMENT
        x = perform_request_search(p=search,cc='HepNames')
        if len(x) == 1:
            #print search
            print 'or', x[0]
            pass
    #elif recid:
    #    print 'or', recid
    #elif len(x) < 1 and not recid:
    else:
        if af:
            bm = bestmatch(af,'ICN')
            aflist = bm[0]
            af = aflist[1]
        inspire_id = 'INSPIRE-00' + str(INSPIRE) + str(random.randint(1, 9))
        output.write(create_xml(au, email, af, EXPERIMENT, inspire_id))
        INSPIRE += 1          
        #print INSPIRE
    #output.write(print_record(r,ot=['001','371'],format='xm'))
#output.close()


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


