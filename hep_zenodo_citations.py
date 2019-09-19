'''Script to find the citations to Zenodo DOIs.'''

import re
from urllib2 import urlopen, URLError

from invenio.search_engine import perform_request_search, \
                                  get_all_field_values

class Repository(object):
    """
    For a particular repository find all citations to its DOIs and
    print an output of the most highly cited records.
    """

    def __init__(self, regex):
        self.regex = re.compile(regex)
        self.citations = self.get_citations()

    @classmethod
    def get_ref_metadata(cls, ref):
        """Get the metadata for a particular record."""
        return 'No metadata for ' + ref

    def get_citations(self):
        """Find all the citations of records in this repository."""

        citations_list = []
        citations = ''
        #for ref in get_all_field_values('999C5a'):
        for ref in ['doi:10.5281/zenodo.11020',
                    'doi:10.5281/zenodo.45906']:
            if self.regex.match(ref):
                search = '999C5a:' + ref
                cites = perform_request_search(p=search, cc='HEP')
                if len(cites):
                    #if not self.regex.match(ref):
                    #    print 'Problem with DOI extraction:', search, cites
                    #    continue
                    try:
                        metadata = self.get_ref_metadata(ref)
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


class Zenodo(Repository):
    """Set up the Zenodo subclass."""

    def __init__(self):
        super(Zenodo, self).__init__(r'^doi:10\.5281/zenodo\.\d+$')

    def get_ref_metadata(self, ref):
        '''Find the author and title of a Zenodo work.'''

        url = 'https://zenodo.org/record/' + \
                   ref.replace('doi:10.5281/zenodo.', '')
        print url
        try:
            webpage = urlopen(url).read()
        except URLError:
            return ValueError('Error opening: ' + url)
        title = str(webpage).split('<title>')[1].split('</title>')[0]
        try:
            author = \
            re.search(r'<meta name="citation_author" content="(.*)" />',
                      str(webpage)).group(1) + ' : '
        except AttributeError:
            author = ''
        return author + title

def main():
    '''Run the program.'''

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '.out', filename)
    output = open(filename, 'w')
    zenodo_output = Zenodo()
    output.write(zenodo_output.citations)
    output.close()
    print filename

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

