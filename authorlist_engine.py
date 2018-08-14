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

""" Invenio Authorlist Data Conversion Engine. """

import getopt
import re
import sys
import time
try:
    import json
except ImportError:
    import simplejson as json
from xml.dom import minidom
#import invenio.authorlist_config as cfg
EMPTY                       = re.compile('^\s*$')
UNDEFINED                   = 'UNDEFINED'
  
  
class Resources:
    SCRIPTS                 = ['jquery.min.js',
                               'jquery-ui.min.js',
                               'jquery.dataTables.min.js',
                               'jquery.dataTables.ColVis.min.js',
                               'authorlist.js',
                               'authorlist.spreadSheet.js',
                               'authorlist.select.js']
  
    STYLESHEETS             = ['authorlist.css',
                               'authorlist.dataTable.css',
                               'authorlist.dataTable.jquery-ui.css',
                               'authorlist.jquery-ui.custom.css',
                               'authorlist.colVis.css',
                               'authorlist.spreadSheet.css']
  
  
class JSON:
    AFFILIATIONS_KEY        = 'affiliations'
    AUTHORS_KEY             = 'authors'
    COLLABORATION           = 'collaboration'
    EXPERIMENT_NUMBER       = 'experiment_number'
    PAPER_ID                = 'paper_id'
    LAST_MODIFIED           = 'last_modified'
    PAPER_TITLE             = 'paper_title'
    REFERENCE_IDS           = 'reference_ids'
  
    # Author table indices
    INDEX                   = 0
    EDIT                    = 1
    FAMILY_NAME             = 2
    GIVEN_NAME              = 3
    PAPER_NAME              = 4
    STATUS                  = 5
    AFFILIATIONS            = 6
    IDENTIFIERS             = 7
  
    # Affiliation indices in author table
    AFFILIATION_ACRONYM     = 0
    AFFILIATION_STATUS      = 1
  
    # Identifiers indices in author table
    IDENTIFIER_NUMBER      = 0
    IDENTIFIER_NAME        = 1
  
    # Affiliation table indices
    ACRONYM                = 2
    UMBRELLA               = 3
    NAME                   = 4
    DOMAIN                 = 5
    MEMBER                 = 6
    SPIRES_ID              = 7
  
  
class AuthorsXML:
    COLLABORATION_ID       = 'c1'
    DECEASED               = 'Deceased'
    MEMBER                 = 'member'
    NONMEMBER              = 'nonmember'
    ORGANIZATION_ID        = 'o'
    SPIRES                 = 'SPIRES'
    TIME_FORMAT            = '%Y-%m-%d_%H:%M'
  
  
class OPTIONS:
  IDENTIFIERS_LIST         = ['Inspire ID', 'ORCID']
  IDENTIFIERS_MAPPING      = {'Inspire ID': 'Inspire ID',
                              'INSPIRE': 'Inspire ID',
                              'Inspire': 'Inspire ID',
                              'ORCID': 'ORCID'}
  AUTHOR_AFFILIATION_TYPE  = ['Affiliated with', 'Now at', 'Also at',
                              'On leave from', 'Visitor']
  




# default name that will be used, when affiliation name is missing
UNKNOWN_AFFILIATION = 'Unknown Affiliation'
# Namespaces used in the xml file
NAMESPACES = {'cal': \
              'http://inspirehep.net/info/HepNames/tools/authors_xml/',
              'foaf': 'http://xmlns.com/foaf/0.1/',
              }

def retrieve_data_from_record(recid):
    """
    Extract data from a record id in order to import it to the Author list
    interface
    """

    from invenio.search_engine import record_exists
    if not record_exists(recid):
        print "No such record", recid
        return None

    from invenio.bibformat_engine import BibFormatObject
    from invenio.bibformat_elements.bfe_INSPIRE_inst_address import \
         format_element as get_address

    from invenio.search_engine import perform_request_search
    from invenio.search_engine_utils import get_fieldvalues
    from invenio.bibedit_utils import get_record

    output = {}

    DEFAULT_AFFILIATION_TYPE = cfg.OPTIONS.AUTHOR_AFFILIATION_TYPE[0]
    DEFAULT_IDENTIFIER = cfg.OPTIONS.IDENTIFIERS_LIST[0]
    IDENTIFIERS_MAPPING = cfg.OPTIONS.IDENTIFIERS_MAPPING

    bibrecord = get_record(recid)

    try:
        paper_title = get_fieldvalues(recid, '245__a')[0]
    except IndexError:
        paper_title = ""
    try:
        collaboration_name = get_fieldvalues(recid, '710__g')
    except IndexError:
        collaboration_name = ""
    try:
        experiment_number = get_fieldvalues(recid, '693__e')
    except IndexError:
        experiment_number = ""

    record_authors = bibrecord.get('100', [])
    record_authors.extend(bibrecord.get('700', []))

    author_list = []
    unique_affiliations = []

    for i, field_instance in enumerate(record_authors, 1):
        family_name = ""
        given_name = ""
        name_on_paper = ""
        status = ""
        affiliations = []
        identifiers = []
        field = field_instance[0]
        for subfield_code, subfield_value in field:
            if subfield_code == "a":
                try:
                    family_name = subfield_value.split(',')[0]
                    given_name = subfield_value.split(',')[1].lstrip()
                except:
                    pass
                name_on_paper = subfield_value
            elif subfield_code == "u":
                affiliations.append([subfield_value,
                                     DEFAULT_AFFILIATION_TYPE])
                unique_affiliations.append(subfield_value)
            elif subfield_code == "i":
                # FIXME This will currently work only with INSPIRE IDs
                id_prefix = subfield_value.split("-")[0]
                if id_prefix in IDENTIFIERS_MAPPING:
                    identifiers.append([subfield_value,
                                        IDENTIFIERS_MAPPING[id_prefix]])
        if not identifiers:
            identifiers.append(['', DEFAULT_IDENTIFIER])
        if not affiliations:
            affiliations.append([UNKNOWN_AFFILIATION,
                                 DEFAULT_AFFILIATION_TYPE])
            unique_affiliations.append(UNKNOWN_AFFILIATION)
        author_list.append([
            i,              # Row number
            '',             # Place holder for the web interface
            family_name,
            given_name,
            name_on_paper,
            status,
            affiliations,
            identifiers
        ])

    unique_affiliations = list(set(unique_affiliations))

    output.update({'authors': author_list})

    # Generate all the affiliation related information
    affiliation_list = []
    for i, affiliation in enumerate(unique_affiliations, 1):
        institution = perform_request_search(c="Institutions",
                          p='110__u:"' + affiliation + '"')
        full_name = affiliation
        inspire_id = ''
        domain = ''
        if len(institution) == 1:
            full_name_110_a = get_fieldvalues(institution[0], '110__a')
            if full_name_110_a:
                full_name = str(full_name_110_a[0])
            full_name_110_b = get_fieldvalues(institution[0], '110__b')
            if full_name_110_b:
                full_name += ', ' + str(full_name_110_b[0])
            domain = get_fieldvalues(institution[0], '8564_u')
            inspire_id = affiliation
            address = get_address(BibFormatObject(institution[0]))
            if address:
                full_name += ', ' + address

        affiliation = [i,
                       '',
                       affiliation,
                       '',
                       full_name,
                       domain,
                       True,
                       inspire_id]
        affiliation_list.append(affiliation)

    output.update({'affiliations': affiliation_list})
    output.update({'paper_title': paper_title,
                   'collaboration': collaboration_name,
                   'experiment_number': experiment_number,
                   'last_modified': int(time.time()),
                   'reference_ids': [],
                   'paper_id': '1'})

    return output


class Converter(object):
    CONTENT_TYPE = 'text/plain'
    FILE_NAME = 'converted.txt'

    def __init__(self):
        raise NotImplementedError

    def dump(self, data):
        raise NotImplementedError

    def dumps(self, data):
        raise NotImplementedError


class AuthorsXML(Converter):
    CONTENT_TYPE = 'text/xml'
    FILE_NAME = 'authors.xml'

    def __init__(self):
        pass

    def create_affiliation(self, document, parsed, organization_ids):
        affiliation = document.createElement('cal:authorAffiliation')

        affiliation_acronym = parsed[cfg.JSON.AFFILIATION_ACRONYM]
        affiliation_status = parsed[cfg.JSON.AFFILIATION_STATUS]

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

        identifier_number = parsed[cfg.JSON.IDENTIFIER_NUMBER]
        identifier_name = parsed[cfg.JSON.IDENTIFIER_NAME]

        identifier.setAttribute('source', identifier_name)
        identifier_text = document.createTextNode(identifier_number)
        identifier.appendChild(identifier_text)

        return identifier

    def create_authors(self, document, root, parsed, organization_ids):
        parsed_authors = parsed[cfg.JSON.AUTHORS_KEY]

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
        paper_name_info = parsed[cfg.JSON.PAPER_NAME]
        paper_name_text = document.createTextNode(paper_name_info)
        paper_name.appendChild(paper_name_text)
        author.appendChild(paper_name)

        # given name
        given_name_info = parsed[cfg.JSON.GIVEN_NAME]
        if (cfg.EMPTY.match(given_name_info) is None):
            given_name = document.createElement('foaf:givenName')
            given_name_text = document.createTextNode(given_name_info)
            given_name.appendChild(given_name_text)
            author.appendChild(given_name)

        # family name
        family_name_info = parsed[cfg.JSON.FAMILY_NAME]
        if (cfg.EMPTY.match(family_name_info) is None):
            family_name = document.createElement('foaf:familyName')
            family_name_text = document.createTextNode(family_name_info)
            family_name.appendChild(family_name_text)
            author.appendChild(family_name)

        # status
        author_status_info = parsed[cfg.JSON.STATUS]
        if (author_status_info):
            author_status = document.createElement('cal:authorStatus')
            author_status_text = document.createTextNode(author_status_info)
            author_status.appendChild(author_status_text)
            author.appendChild(author_status)

        # collaboration
        collaboration = document.createElement('cal:authorCollaboration')
        collaboration.setAttribute('collaborationid',
                                   cfg.AuthorsXML.COLLABORATION_ID)
        author.appendChild(collaboration)

        # affiliations
        affiliations = document.createElement('cal:authorAffiliations')
        author.appendChild(affiliations)
        for parsed_affiliation in parsed[cfg.JSON.AFFILIATIONS]:
            affiliation = self.create_affiliation(document,
                                                  parsed_affiliation,
                                                  organization_ids)
            affiliations.appendChild(affiliation)

        # identifiers
        identifiers = document.createElement('cal:authorids')
        author.appendChild(identifiers)
        for parsed_identifier in parsed[cfg.JSON.IDENTIFIERS]:
            identifier = self.create_identifier(document, parsed_identifier)
            identifiers.appendChild(identifier)

        return author

    def create_collaboration(self, document, root, parsed):
        # collaborations
        collaborations = document.createElement('cal:collaborations')
        collaboration = document.createElement('cal:collaboration')
        collaboration.setAttribute('id', cfg.AuthorsXML.COLLABORATION_ID)
        collaborations.appendChild(collaboration)

        # name
        name = document.createElement('foaf:name')
        try:
            name_info = parsed[cfg.JSON.COLLABORATION]
            name_text = document.createTextNode(name_info)
        except TypeError:
            name_info = parsed[cfg.JSON.COLLABORATION][0]
            name_text = document.createTextNode(name_info)
        name.appendChild(name_text)
        collaboration.appendChild(name)

        # experiment number
        experiment_number_info = parsed[cfg.JSON.EXPERIMENT_NUMBER]
        if not isinstance(experiment_number_info, basestring):
            experiment_number_info = experiment_number_info[0]
        if (cfg.EMPTY.match(experiment_number_info) is None):
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
        creation_date_info = time.strftime(cfg.AuthorsXML.TIME_FORMAT)
        creation_date_text = document.createTextNode(creation_date_info)
        creation_date.appendChild(creation_date_text)
        root.appendChild(creation_date)

        # publication reference
        for reference_info in parsed[cfg.JSON.REFERENCE_IDS]:
            reference = document.createElement('cal:publicationReference')
            reference_text = document.createTextNode(reference_info)
            reference.appendChild(reference_text)
            root.appendChild(reference)

    def create_organizations(self, document, root, parsed, ids):
        parsed_organizations = parsed[cfg.JSON.AFFILIATIONS_KEY]

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
        acronym = parsed[cfg.JSON.ACRONYM]
        organization = document.createElement('foaf:Organization')
        organization.setAttribute('id', ids[acronym])

        # create the domain node if field is set
        domain_info = parsed[cfg.JSON.DOMAIN]
        if not isinstance(domain_info, basestring):
            try:
                domain_info = domain_info[0]
            except IndexError:
                domain_info = None
        if (cfg.EMPTY.match(domain_info) is None):
            domain = document.createElement('cal:orgDomain')
            domain_text = document.createTextNode(domain_info)
            domain.appendChild(domain_text)
            organization.appendChild(domain)

        # organization name, no presence check,
        # already done on the client side
        name = document.createElement('foaf:name')
        name_info = parsed[cfg.JSON.NAME]
        name_text = document.createTextNode(name_info)
        name.appendChild(name_text)
        organization.appendChild(name)

        # organization acronym
        org_acronym = document.createElement('cal:orgName')
        org_acronym_text = document.createTextNode(acronym)
        org_acronym.appendChild(org_acronym_text)
        organization.appendChild(org_acronym)

        # organization identifier
        org_name_info = parsed[cfg.JSON.INSPIRE_ID]
        if (cfg.EMPTY.match(org_name_info) is None):
            org_name = document.createElement('cal:orgName')
            org_name.setAttribute('source', cfg.AuthorsXML.INSPIRE)
            org_name_text = document.createTextNode(org_name_info)
            org_name.appendChild(org_name_text)
            organization.appendChild(org_name)
        else:
            org_name_info = parsed[cfg.JSON.NAME]
            org_address = document.createElement('cal:orgAddress')
            org_address_text = document.createTextNode(org_name_info)
            org_address.appendChild(org_address_text)
            organization.appendChild(org_address)

        # membership
        org_status_info = parsed[cfg.JSON.MEMBER]
        if (not org_status_info):
            org_status_info = cfg.AuthorsXML.NONMEMBER
        else:
            org_status_info = cfg.AuthorsXML.MEMBER
        org_status = document.createElement('cal:orgStatus')
        org_status_text = document.createTextNode(org_status_info)
        org_status.appendChild(org_status_text)
        organization.appendChild(org_status)

        # umbrella organization/group
        group_info = parsed[cfg.JSON.UMBRELLA]
        if (cfg.EMPTY.match(group_info) is None):
            if group_info in ids.keys():
                group = document.createElement('cal:group')
                group.setAttribute('with', ids[group_info])
                organization.appendChild(group)

        return organization

    def dump(self, data):
        parsed = json.loads(data)
        document, root = self.create_document()
        affiliations = parsed[cfg.JSON.AFFILIATIONS_KEY]

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
            acronym = organization[cfg.JSON.ACRONYM]
            ids[acronym] = cfg.AuthorsXML.ORGANIZATION_ID + str(index)

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


if __name__ == '__main__':

    recid_dict = None

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 'r:')
        print OPTIONS
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    for option, argument in OPTIONS:
        print option, argument
        if option == '-r':
            recid_dict = retrieve_data_from_record(argument)
    if OPTIONS == []:
        from authorlist_engine_input import RECID_DICT as recid_dict

    if recid_dict:
        data = json.dumps(recid_dict)
        #output = dump(data, AuthorsXML)
        import pprint
        pprint.pprint(recid_dict)
