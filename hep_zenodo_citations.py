'''Script to find the citations to Zenodo DOIs.'''

import cPickle as pickle
import os
from os.path import exists
import re
from urllib2 import urlopen, URLError

from invenio.search_engine import perform_request_search, \
                                  get_all_field_values, get_fieldvalues


DIRECTORY = '/afs/cern.ch/project/inspire/TEST/hoc/'
ZENODO_METADATA_FILE = 'hep_author_collaboration_zenodo_metadata.p'
ZENODO_METADATA_FILE = DIRECTORY + ZENODO_METADATA_FILE
try:
    ZENODO_METADATA = pickle.load(open(ZENODO_METADATA_FILE, "rb"))
except EOFError:
    print "Error opening:", ZENODO_METADATA_FILE
except IOError:
    ZENODO_METADATA = {}


class Repository(object):
    """
    For a particular repository find all citations to its DOIs and
    print an output of the most highly cited records.
    """

    def __init__(self, regex_string):
        self.regex = self.get_regex(regex_string)
        self.regex_base = self.get_regex_base(regex_string)
        self.dois = self.get_inspire_dois(self.regex)
        self.citations = self.get_citations()

    @classmethod
    def get_regex(cls, regex_string):
        """Get the regex for the class."""
        return re.compile(r'^' + regex_string + r'$')

    @classmethod
    def get_regex_base(cls, regex_string):
        """Get the DOI base regex for the class."""
        doi_base = r'doi:10\\.\d{4,5}\/\w+'
        try:
            base = re.search(doi_base, regex_string).group()
        except AttributeError:
            doi_base = r'doi:10\\.\d{4,5}'
            base = re.search(doi_base, regex_string).group()
        return re.compile(r'^' + base + '.*')

    @classmethod
    def get_inspire_dois(cls, regex):
        """Get all the DOIs in INSPIRE."""
        dois = set()
        for doi in get_all_field_values('0247_a'):
            doi = 'doi:' + doi
            if regex.match(doi):
                dois.add(doi)
        return dois

    @classmethod
    def get_ref_metadata_inspire(cls, ref, dois):
        """Get the metadata for a particular reference from INSPIRE."""
        if ref not in dois:
            return None
        ref = ref.replace('doi:', '')
        recid = perform_request_search(p='0247_a:' + ref, cc='HEP') + \
                perform_request_search(p='0247_a:' + ref, cc='Fermilab')
        try:
            recid = recid[0]
            title = get_fieldvalues(recid, '245__a')[0]
            author = get_fieldvalues(recid, '100__a')[0]
            return """This DOI is in INSPIRE
    {0} : {1}""".format(author, title)
        except IndexError:
            return 'DOI should be in HEP but is not: ' + ref

    @classmethod
    def get_ref_metadata_repository(cls, ref):
        """Get the metadata for a particular reference from the repository."""

        return 'Metadata unknown: ' + ref

    def get_citations(self):
        """Find all the citations of records in this repository."""

        citations_list = []
        citations = ''
        for ref in get_all_field_values('999C5a'):
            if self.regex_base.match(ref):
                search = '999C5a:' + ref
                cites = perform_request_search(p=search, cc='HEP')
                if len(cites):
                    if not self.regex.match(ref):
                        print 'Problem with DOI extraction:', search, cites
                        continue
                    try:
                        metadata = self.get_ref_metadata_inspire(ref, self.dois)
                        if not metadata:
                            metadata = self.get_ref_metadata_repository(ref)
                    except ValueError:
                        print 'Problem with DOI:', search, cites, '\n'
                        continue
                    citations_list.append((len(cites), ref, cites, metadata))
        for doi in sorted(citations_list, reverse=True):
            doi_url = 'https://doi.org/' + doi[1].replace('doi:', '')
            citations += \
'''{0} citations to {3}
    {2}
    https://inspirehep.net/search?p=999C5a:{1}

'''.format(doi[0], doi[1], doi[3], doi_url)
        return citations

class OSTI(Repository):
    """Set up the OSTI subclass."""

    def __init__(self):
        super(OSTI, self).__init__(r'doi:10\.2172/\d+')



class Zenodo(Repository):
    """Set up the Zenodo subclass."""

    def __init__(self):
        super(Zenodo, self).__init__(r'doi:10\.5281/zenodo\.\d+')

    def get_ref_metadata_repository(self, ref):
        '''Find the author and title of a Zenodo work.'''

        if ref in ZENODO_METADATA:
            author = ZENODO_METADATA[ref]['author']
            title = ZENODO_METADATA[ref]['title']
            return author + ' : ' + title
        url = 'https://zenodo.org/record/' + \
                   ref.replace('doi:10.5281/zenodo.', '')
        try:
            webpage = urlopen(url).read()
        except URLError:
            return ValueError('Error opening: ' + url)
        title = str(webpage).split('<title>')[1].split('</title>')[0]
        try:
            author = \
            re.search(r'<meta name="citation_author" content="(.*)" />',
                      str(webpage)).group(1)
        except AttributeError:
            author = ''
        if author and title:
            ZENODO_METADATA[ref] = {}
            ZENODO_METADATA[ref]['author'] = author
            ZENODO_METADATA[ref]['title'] = title
        return author + ' : ' + title

def main():
    '''Run the program.'''

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '.out', filename)
    output = open(filename, 'w')
    jacow_output = Repository(r'doi:10\.18429/JACoW\-\w+\d{4}-[A-Z\d]+\d+')
    output.write(jacow_output.citations)
    output.write('\n--------------\n\n')
    osti_output = OSTI()
    output.write(osti_output.citations)
    output.write('\n--------------\n\n')
    zenodo_output = Zenodo()
    output.write(zenodo_output.citations)
    output.close()
    if exists(ZENODO_METADATA_FILE):
        backup = ZENODO_METADATA_FILE + '.bak'
        if exists(backup):
            os.remove(backup)
        os.rename(ZENODO_METADATA_FILE, backup)
    with open(ZENODO_METADATA_FILE, "wb") as fname:
        pickle.dump(ZENODO_METADATA, fname)
    print 'Number of Zenodo records:', len(ZENODO_METADATA)
    print filename

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

