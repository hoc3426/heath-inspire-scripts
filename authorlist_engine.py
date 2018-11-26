## This file is part of Invenio.
## Copyright (C) 2011, 2012, 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Convert a spreadsheet-based author list into an author.xml file. """

import cPickle as pickle
import csv
import getopt
import gzip
import re
import sys
import time
try:
    import json
except ImportError:
    import simplejson as json
from xml.dom import minidom

AFFILIATIONS_DICT_FILE = 'authorlist_engine_affiliations.p.gz'
AFFILIATIONS_DICT_FILE = AFFILIATIONS_DICT_FILE
AFFILIATIONS_DICT = {}

try:
    AFFILIATIONS_DICT = pickle.load(gzip.open(AFFILIATIONS_DICT_FILE, "rb"))
except EOFError:
    print "Error opening affiliations file:", AFFILIATIONS_DICT_FILE    
except IOError:
    try:
        AFFILIATIONS_DICT_FILE = AFFILIATIONS_DICT_FILE.replace('.gz', '')
        AFFILIATIONS_DICT = pickle.load(open(AFFILIATIONS_DICT_FILE, "rb"))
    except EOFError:
        print "Error opening:", AFFILIATIONS_DICT_FILE
    except IOError:
        print '''REMOVE THIS WARNING:
No affiliation file found, no institution name conversions performed.
**********
'''
        

def get_aff(affiliation):
    '''Convert affiliation information into INSPIRE format.'''

    affiliation_key = re.sub(r'\W+', ' ', affiliation).upper()
    affiliation_key = re.sub(r'^[ ]+', '', affiliation_key)
    affiliation_key = re.sub(r'[ ]+$', '', affiliation_key)
    affiliation_key = re.sub(r'[ ]+$', ' ', affiliation_key)

    try:
        return AFFILIATIONS_DICT[affiliation_key][0]
    except KeyError:
        return 'UNDEF: ' + affiliation



EMPTY = re.compile(r'^\s*$')
UNDEFINED = 'UNDEFINED'


class JSON(object):
    '''Defines the parameters to be used in the xml file.'''

    def __init__(self):
        pass

    AFFILIATIONS_KEY = 'affiliations'
    AUTHORS_KEY = 'authors'
    COLLABORATION = 'collaboration'
    EXPERIMENT_NUMBER = 'experiment_number'
    PAPER_ID = 'paper_id'
    LAST_MODIFIED = 'last_modified'
    PAPER_TITLE = 'paper_title'
    REFERENCE_IDS = 'reference_ids'

    # Author table indices
    INDEX = 0
    EDIT = 1
    FAMILY_NAME = 2
    GIVEN_NAME = 3
    PAPER_NAME = 4
    STATUS = 5
    AFFILIATIONS = 6
    IDENTIFIERS = 7

    # Affiliation indices in author table
    AFFILIATION_ACRONYM = 0
    AFFILIATION_STATUS = 1

    # Identifiers indices in author table
    IDENTIFIER_NUMBER = 0
    IDENTIFIER_NAME = 1

    # Affiliation table indices
    ACRONYM = 2
    UMBRELLA = 3
    NAME = 4
    DOMAIN = 5
    MEMBER = 6
    INSPIRE_ID = 7

class OPTIONS(object):
    '''Standardizes various parameters.'''

    def __init__(self):
        pass

    IDENTIFIERS_LIST = ['INSPIRE', 'ORCID']
    IDENTIFIERS_MAPPING = {'Inspire ID': 'INSPIRE',
                           'INSPIRE': 'INSPIRE',
                           'Inspire': 'INSPIRE',
                           'ORCID': 'ORCID'}
    AUTHOR_AFFILIATION_TYPE = ['Affiliated with', 'Now at', 'Also at',
                              'On leave from', 'Visitor']





# default name that will be used, when affiliation name is missing
UNKNOWN_AFFILIATION = 'Unknown Affiliation'
# Namespaces used in the xml file
NAMESPACES = {'cal': \
              'http://inspirehep.net/info/HepNames/tools/authors_xml/',
              'foaf': 'http://xmlns.com/foaf/0.1/',
              }

class Converter(object):
    '''Used to output final file.'''

    CONTENT_TYPE = 'text/plain'
    FILE_NAME = 'converted.txt'

    def __init__(self):
        raise NotImplementedError

    def dump(self, data):
        raise NotImplementedError

    def dumps(self, data):
        raise NotImplementedError


class AuthorsXML(Converter):

    def __init__(self):
        pass

    CONTENT_TYPE = 'text/xml'
    FILE_NAME = 'authors.xml'
    COLLABORATION_ID = 'c1'
    DECEASED = 'Deceased'
    MEMBER = 'member'
    NONMEMBER = 'nonmember'
    ORGANIZATION_ID = 'o'
    SPIRES = 'SPIRES'
    INSPIRE = 'INSPIRE'
    TIME_FORMAT = '%Y-%m-%d_%H:%M'

    def create_affiliation(self, document, parsed, organization_ids):
        affiliation = document.createElement('cal:authorAffiliation')

        affiliation_acronym = parsed[JSON.AFFILIATION_ACRONYM]
        affiliation_status = parsed[JSON.AFFILIATION_STATUS]

        if affiliation_acronym not in organization_ids:
            affiliation.setAttribute('organizationid',
                                     'Error - there is no organization \
                                     called ' +
                                     affiliation_acronym)
        else:
            affiliation.setAttribute('organizationid',
                                     organization_ids[affiliation_acronym])
        affiliation.setAttribute('connection', affiliation_status)

        return affiliation

    def create_identifier(self, document, parsed):
        identifier = document.createElement('cal:authorid')

        identifier_number = parsed[JSON.IDENTIFIER_NUMBER]
        identifier_name = parsed[JSON.IDENTIFIER_NAME]

        identifier.setAttribute('source', identifier_name)
        identifier_text = document.createTextNode(identifier_number)
        identifier.appendChild(identifier_text)

        return identifier

    def create_authors(self, document, root, parsed, organization_ids):
        parsed_authors = parsed[JSON.AUTHORS_KEY]

        authors = document.createElement('cal:authors')
        root.appendChild(authors)

        for parsed_author in parsed_authors:
            author = self.create_author(document, parsed_author,
                                        organization_ids)
            authors.appendChild(author)

    def create_author(self, document, parsed, organization_ids):
        author = document.createElement('foaf:Person')

        # paper name
        paper_name = document.createElement('cal:authorNamePaper')
        paper_name_info = parsed[JSON.PAPER_NAME]
        paper_name_text = document.createTextNode(paper_name_info)
        paper_name.appendChild(paper_name_text)
        author.appendChild(paper_name)

        # given name
        given_name_info = parsed[JSON.GIVEN_NAME]
        if EMPTY.match(given_name_info) is None:
            given_name = document.createElement('foaf:givenName')
            given_name_text = document.createTextNode(given_name_info)
            given_name.appendChild(given_name_text)
            author.appendChild(given_name)

        # family name
        family_name_info = parsed[JSON.FAMILY_NAME]
        if EMPTY.match(family_name_info) is None:
            family_name = document.createElement('foaf:familyName')
            family_name_text = document.createTextNode(family_name_info)
            family_name.appendChild(family_name_text)
            author.appendChild(family_name)

        # status
        author_status_info = parsed[JSON.STATUS]
        if author_status_info:
            author_status = document.createElement('cal:authorStatus')
            author_status_text = document.createTextNode(author_status_info)
            author_status.appendChild(author_status_text)
            author.appendChild(author_status)

        # collaboration
        collaboration = document.createElement('cal:authorCollaboration')
        collaboration.setAttribute('collaborationid',
                                   AuthorsXML.COLLABORATION_ID)
        author.appendChild(collaboration)

        # affiliations
        affiliations = document.createElement('cal:authorAffiliations')
        author.appendChild(affiliations)
        for parsed_affiliation in parsed[JSON.AFFILIATIONS]:
            affiliation = self.create_affiliation(document,
                                                  parsed_affiliation,
                                                  organization_ids)
            affiliations.appendChild(affiliation)

        # identifiers
        identifiers = document.createElement('cal:authorids')
        author.appendChild(identifiers)
        for parsed_identifier in parsed[JSON.IDENTIFIERS]:
            identifier = self.create_identifier(document, parsed_identifier)
            identifiers.appendChild(identifier)

        return author

    def create_collaboration(self, document, root, parsed):
        # collaborations
        collaborations = document.createElement('cal:collaborations')
        collaboration = document.createElement('cal:collaboration')
        collaboration.setAttribute('id', AuthorsXML.COLLABORATION_ID)
        collaborations.appendChild(collaboration)

        # name
        name = document.createElement('foaf:name')
        try:
            name_info = parsed[JSON.COLLABORATION]
            name_text = document.createTextNode(name_info)
        except TypeError:
            name_info = parsed[JSON.COLLABORATION][0]
            name_text = document.createTextNode(name_info)
        name.appendChild(name_text)
        collaboration.appendChild(name)

        # experiment number
        experiment_number_info = parsed[JSON.EXPERIMENT_NUMBER]
        if not isinstance(experiment_number_info, basestring):
            experiment_number_info = experiment_number_info[0]
        if EMPTY.match(experiment_number_info) is None:
            experiment_number = document.createElement('cal:experimentNumber')
            experiment_number_text = document.createTextNode(
                                         experiment_number_info)
            experiment_number.appendChild(experiment_number_text)
            collaboration.appendChild(experiment_number)
        root.appendChild(collaborations)

    def create_document(self):
        dom = minidom.getDOMImplementation()
        document = dom.createDocument(None, 'collaborationauthorlist', None)
        root = document.documentElement

        root.setAttribute('xmlns:foaf', 'http://xmlns.com/foaf/0.1/')
        root.setAttribute('xmlns:cal',
            'http://inspirehep.net/info/HepNames/tools/authors_xml/')

        return document, root

    def create_header(self, document, root, parsed):
        # creation date
        creation_date = document.createElement('cal:creationDate')
        creation_date_info = time.strftime(AuthorsXML.TIME_FORMAT)
        creation_date_text = document.createTextNode(creation_date_info)
        creation_date.appendChild(creation_date_text)
        root.appendChild(creation_date)

        # publication reference
        for reference_info in parsed[JSON.REFERENCE_IDS]:
            reference = document.createElement('cal:publicationReference')
            reference_text = document.createTextNode(reference_info)
            reference.appendChild(reference_text)
            root.appendChild(reference)

    def create_organizations(self, document, root, parsed, ids):
        parsed_organizations = parsed[JSON.AFFILIATIONS_KEY]

        # organizations container
        organizations = document.createElement('cal:organizations')
        root.appendChild(organizations)

        # create individual organizations and append them
        for parsed_organization in parsed_organizations:
            organization = self.create_organization(document,
                                                    parsed_organization,
                                                    ids)
            organizations.appendChild(organization)

    def create_organization(self, document, parsed, ids):
        acronym = parsed[JSON.ACRONYM]
        organization = document.createElement('foaf:Organization')
        organization.setAttribute('id', ids[acronym])

        # create the domain node if field is set
        domain_info = parsed[JSON.DOMAIN]
        if not isinstance(domain_info, basestring):
            try:
                domain_info = domain_info[0]
            except IndexError:
                domain_info = None
        if EMPTY.match(domain_info) is None:
            domain = document.createElement('cal:orgDomain')
            domain_text = document.createTextNode(domain_info)
            domain.appendChild(domain_text)
            organization.appendChild(domain)

        # organization name, no presence check,
        # already done on the client side
        name = document.createElement('foaf:name')
        name_info = parsed[JSON.NAME]
        name_text = document.createTextNode(name_info)
        name.appendChild(name_text)
        organization.appendChild(name)

        ## organization acronym
        #org_acronym = document.createElement('cal:orgName')
        #org_acronym_text = document.createTextNode(acronym)
        #org_acronym.appendChild(org_acronym_text)
        #organization.appendChild(org_acronym)

        # organization identifier
        org_name_info = parsed[JSON.INSPIRE_ID]
        if EMPTY.match(org_name_info) is None:
            org_name = document.createElement('cal:orgName')
            org_name.setAttribute('source', AuthorsXML.INSPIRE)
            org_name_text = document.createTextNode(org_name_info)
            org_name.appendChild(org_name_text)
            organization.appendChild(org_name)
        else:
            org_name_info = parsed[JSON.NAME]
            org_address = document.createElement('cal:orgAddress')
            org_address_text = document.createTextNode(org_name_info)
            org_address.appendChild(org_address_text)
            organization.appendChild(org_address)

        # membership
        org_status_info = parsed[JSON.MEMBER]
        if not org_status_info:
            org_status_info = AuthorsXML.NONMEMBER
        else:
            org_status_info = AuthorsXML.MEMBER
        org_status = document.createElement('cal:orgStatus')
        org_status_text = document.createTextNode(org_status_info)
        org_status.appendChild(org_status_text)
        organization.appendChild(org_status)

        # umbrella organization/group
        group_info = parsed[JSON.UMBRELLA]
        if EMPTY.match(group_info) is None:
            if group_info in ids.keys():
                group = document.createElement('cal:group')
                group.setAttribute('with', ids[group_info])
                organization.appendChild(group)

        return organization

    def dump(self, data):
        parsed = json.loads(data)
        document, root = self.create_document()
        #affiliations = parsed[JSON.AFFILIATIONS_KEY]
        affiliations = parsed[JSON.AFFILIATIONS_KEY]

        organization_ids = self.generate_organization_ids(affiliations)

        self.create_header(document, root, parsed)
        self.create_collaboration(document, root, parsed)
        self.create_organizations(document, root, parsed, organization_ids)
        self.create_authors(document, root, parsed, organization_ids)

        return document

    def dumps(self, data):
        # FIX for toprettyxml function from website:
        # http://ronrothman.com/public/leftbraned/
        #     xml-dom-minidom-toprettyxml-and-silly-whitespace/
        def fixed_writexml(self, writer, indent="", addindent="", newl=""):
            # indent = current indentation
            # addindent = indentation to add to higher levels
            # newl = newline string
            writer.write(indent+"<" + self.tagName)

            attrs = self._get_attributes()
            a_names = attrs.keys()
            a_names.sort()

            for a_name in a_names:
                writer.write(" %s=\"" % a_name)
                minidom._write_data(writer, attrs[a_name].value)
                writer.write("\"")
            if self.childNodes:
                if len(self.childNodes) == 1 and \
                self.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
                    writer.write(">")
                    self.childNodes[0].writexml(writer, "", "", "")
                    writer.write("</%s>%s" % (self.tagName, newl))
                    return
                writer.write(">%s" % (newl))
                for node in self.childNodes:
                    node.writexml(writer, indent + addindent, addindent, newl)
                writer.write("%s</%s>%s" % (indent, self.tagName, newl))
            else:
                writer.write("/>%s" % (newl))
        # replace minidom's function with ours
        minidom.Element.writexml = fixed_writexml
        # End of FIX
        return self.dump(data).toprettyxml(indent='    ',
                                           newl='\r\n',
                                           encoding='utf-8')

    def generate_organization_ids(self, organizations):
        ids = {}
        # Map each organization acronym to an id of the kind 'o[index]'
        for index, organization in enumerate(organizations):
            #acronym = organization[JSON.ACRONYM]
            acronym = organization[JSON.ACRONYM]
            ids[acronym] = AuthorsXML.ORGANIZATION_ID + str(index)

        return ids


class Converters:
    __converters__ = {'authorsxml': AuthorsXML}
    @classmethod
    def get(cls, format):
        return cls.__converters__.get(format)


def dump(data, converter):
    return converter().dump(data)


def dumps(data, converter):
    return converter().dumps(data)

def generate_check_digit(base_digits):
    '''
    Taken from https://github.com/tjwds/generate-orcid-checksum
    '''
    total = 0
    for digit in str(base_digits):
        total = (total + int(digit)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    if result == 10:
        result = "X"
    return result

ORCID_REGEX = re.compile(r'^0000-\d{4}-\d{4}-\d{3}[\dX]$')
INSPIRE_REGEX = re.compile(r'^INSPIRE-\d{8}$')

def bad_orcid(id_num):
    if not re.match(ORCID_REGEX, id_num):
        return True
    base_digits = id_num.replace('-', '')[0:15]
    check_digit = id_num.replace('-', '')[15]
    if check_digit != str(generate_check_digit(base_digits)):
        return True

def bad_inspire_id(id_num):
    if not re.match(INSPIRE_REGEX, id_num):
        return True


def read_spreadsheet(file_name):

    elements = ['given', 'family', 'inspire', 'orcid']
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|',
                                fieldnames=elements,
                                restkey='affiliations')
        author_lines = list(reader)
    #print author_lines
    return author_lines

def create_author_institution_dict(author_lines):

    affiliations = []
    affiliation_counter = 1
    affiliation_seen = set()
    authors = []
    author_counter = 1
    id_numbers = set()
    for author in author_lines:
        for id_number in ['orcid', 'inspire']:
            if author[id_number] and author[id_number] in id_numbers:
                print 'The ID', author[id_number], 'appears twice'
                return None
            id_numbers.add(author[id_number])
        if author['orcid'] and bad_orcid(author['orcid']):
            print 'Invalid ORCID:', author['orcid'], 'for author', author['family']
            return None
        if author['inspire'] and bad_inspire_id(author['inspire']):
            print 'Invalid INSPIRE ID:', author['inspire'], 'for author', author['family']
            return None
        author_element = [author_counter,
                        '',
                        author['family'],
                        author['given'],
                        author['family'] + ', ' + author['given'],
                        '']
        author_affiliations = []
        for affiliation in author['affiliations']:
            affiliation_inspire = get_aff(affiliation)
            author_affiliations.append([affiliation_inspire, 'Affiliated with'])

            if affiliation not in affiliation_seen:
                affiliation_seen.add(affiliation)
                affiliations.append([affiliation_counter,
                                     '',
                                     affiliation_inspire,
                                     '',
                                     affiliation,
                                     [''], #Where URL goes
                                     True,
                                     affiliation_inspire])
                affiliation_counter += 1
        author_element.append(author_affiliations)
        author_element.append([[author['inspire'], 'INSPIRE'],
                               [author['orcid'], 'ORCID']])

        authors.append(author_element)
        author_counter += 1
    recid_dict = {'affiliations':affiliations, 'authors':authors}
    recid_dict['collaboration'] = \
        ['*** WRITE YOUR COLLABORATION NAME HERE OR LEAVE BLANK ***']
    recid_dict['experiment_number'] = \
        ['*** WRITE YOUR EXPERIMENT NUMBER HERE OR LEAVE BLANK ***']
    recid_dict['last_modified'] = int(time.time())
    recid_dict['paper_title'] = ''
    recid_dict['reference_ids'] = []
    return recid_dict

if __name__ == '__main__':

    RECID_DICT = None

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 'f:')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    for option, argument in OPTIONS:
        if option == '-f':
            AUTHORS = read_spreadsheet(argument)
            RECID_DICT = create_author_institution_dict(AUTHORS)
    if OPTIONS == []:
        #from authorlist_engine_input import RECID_DICT as recid_dict
        print "Please provide name of input file."

    if RECID_DICT:
        DATA_JSON = json.dumps(RECID_DICT)
        OUTPUT = dump(DATA_JSON, AuthorsXML)
        AUTHOR_XML = OUTPUT.toprettyxml(indent='    ',
                                           newl='\r\n',
                                           encoding='utf-8')
        print AUTHOR_XML
