#!/usr/bin/python
# -*- coding: UTF-8 -*-
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from hep_convert_email_to_id import get_hepnames_recid_from_email, \
                                    get_hepnames_anyid_from_recid
from invenio.search_engine import print_record
from hep_convert_email_to_id import *
from collections import OrderedDict

import re
import sys
import cgi


VERBOSE = True
VERBOSE = False

def xml_frontmatter(experiment, collaboration):
    output = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE collaborationauthorlist SYSTEM "http://www.slac.stanford.edu/spires/hepnames/authors_xml/author.dtd">
<collaborationauthorlist xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:cal="http://www.slac.stanford.edu/spires/hepnames/authors_xml/">
  <cal:creationDate>$Date: 2014/07/09 14:55:49 $</cal:creationDate>
  <cal:publicationReference>arXiv:yymm.nnnn</cal:publicationReference>
  <cal:collaborations>
    <cal:collaboration id="c1">
      <foaf:name>"""
    output += collaboration
    output += """</foaf:name>
      <cal:experimentNumber>"""
    output += experiment
    output += """</cal:experimentNumber>
    </cal:collaboration>
  </cal:collaborations>"""
    return output

def xml_affiliations(affiliations):
    output  = '  <cal:organizations>\n'
    for affiliation in affiliations:
        name    = ''
        domain  = ''
        street  = ''
        town    = ''
        state   = ''
        country = ''
        zip     = ''
        address = ''
        if VERBOSE:
            print affiliation
        try:
            search = '110__u:"' + affiliation + '"'
        except:
            print 'Problem affiliation', affiliation
        if VERBOSE:
            print search
        try:
            x = perform_request_search(p = search, cc = 'Institutions')
        except UnboundLocalError:
            print 'Problem with', search
        if len(x) == 1:
            y = get_fieldvalues(x[0], '110__a')
            if y: name = cgi.escape(y[0])
            y = get_fieldvalues(x[0], '8564_u')
            if y: domain = y[0]
            y = get_fieldvalues(x[0], '371__a')
            if y: street = y[0] + ', '
            y = get_fieldvalues(x[0], '371__b')
            if y: town = y[0] + ', '
            y = get_fieldvalues(x[0], '371__c')
            if y: state = y[0] + ', '
            y = get_fieldvalues(x[0], '371__d')
            if y: country = y[0]
            y = get_fieldvalues(x[0], '371__e')
            if y: zip = y[0]+ ', '
            address = name + ', ' + street + town + state + zip + country
            address = cgi.escape(address)
        output += '    <foaf:Organization id="a'
        output += str(affiliations.index(affiliation) + 1) + '">\n'
        output += '      <cal:orgDomain>' + domain + '</cal:orgDomain>\n'
        output += '      <foaf:name>' + name + '</foaf:name>\n'
        output += '      <cal:orgName source="INSPIRE">' + affiliation
        output += '</cal:orgName>\n'
        output += '      <cal:orgStatus collaborationid="c1">member</cal:orgStatus>\n'
        if address:
            output += '      <cal:orgAddress>' + address + '</cal:orgAddress>\n'
        output += '    </foaf:Organization>\n'
    output += '  </cal:organizations>'
    return output

def xml_authors(authors):
    output  = '  <cal:authors>\n'
    for key in sorted(authors.iterkeys()):
        initial = re.sub(r'^(\w).*', r'\1', authors[key]['foaf_givenName']) + '.'
        output += '    <foaf:Person>\n'
        output += '      <foaf:name>' + authors[key]['foaf_givenName']
        output += ' ' + authors[key]['foaf_familyName'] + '</foaf:name>\n'
        output += '      <foaf:givenName>' + authors[key]['foaf_givenName'] + '</foaf:givenName>\n'
        output += '      <foaf:familyName>' + authors[key]['foaf_familyName'] + '</foaf:familyName>\n'
        output += '      <cal:authorNamePaper>' + initial
        output += ' ' + authors[key]['foaf_familyName'] + '</cal:authorNamePaper>\n'
        output += '      <cal:authorAffiliations>\n'
        output += '        <cal:authorAffiliation organizationid="a'
        output += str(authors[key]['affiliation_id']) + '" connection="member"/>\n'
        output += '      </cal:authorAffiliations>\n'
        output += '      <cal:authorids>\n'
        try:
            output += '        <cal:authorid source="INSPIRE">' + authors[key]['author_id'] + '</cal:authorid>\n'
        except KeyError:
            print authors[key]
        except TypeError:
            pass
        try:
            output += '        <cal:authorid source="INSPIRE">' + authors[key]['orcid'] + '</cal:authorid>\n'
        except KeyError:
            print authors[key]
        except TypeError:
            pass
        output += '      </cal:authorids>\n'
        output += '    </foaf:Person>\n'
    output  += '  </cal:authors>\n'
    output  += '</collaborationauthorlist>'
    return output


def affiliations_process(x):
    x.sort()
    x = list(OrderedDict.fromkeys(x))
    return x

def main(experiment, collaboration):
    authors = {}
    affiliations = []
    affiliation_count = 1
    search = "693__e:" + experiment
    x = perform_request_search(p = search, cc = 'HepNames')
    for r in x:
        foaf_name = get_fieldvalues(r, '100__q')
        cal_authorNameNative = get_fieldvalues(r, '400__a')
        name = get_fieldvalues(r, '100__a')[0]
        foaf_givenName  = re.sub(r'.*\, ', '', name)
        foaf_familyName =  re.sub(r'\,.*', '', name)
        author_id = find_inspire_id_from_record(r)
        orcid      = get_hepnames_anyid_from_recid(r, 'ORCID')
        if VERBOSE:
            print r
        affiliation = get_hepnames_aff_from_recid(r, 'Current')
        if not affiliation: print 'No aff - find recid', r
        d = {}
        d['foaf_givenName']  = foaf_givenName
        d['foaf_familyName'] = foaf_familyName
        d['affiliation']     = affiliation
        d['author_id']       = author_id
        authors[name.lower()] = d
        affiliations.append(affiliation)
    affiliations = affiliations_process(affiliations)
    for key in authors:
        affiliation = authors[key]['affiliation']
        affiliation_number = affiliations.index(affiliation) + 1
        authors[key]['affiliation_id'] = affiliation_number
    print xml_frontmatter(experiment, collaboration)
    print xml_affiliations(affiliations)
    print xml_authors(authors)

if __name__ == '__main__':
    experiment    = sys.argv[1:][0]
    collaboration = sys.argv[1:][1]
    try:
        main(experiment, collaboration)
    except KeyboardInterrupt:
        print 'Exiting'

