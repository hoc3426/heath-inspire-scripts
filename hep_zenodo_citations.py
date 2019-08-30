'''Script to find the citations to Zenodo DOIs.'''

import re
from urllib2 import urlopen, URLError

from invenio.search_engine import perform_request_search, \
                                  get_all_field_values

ZENODO_REGEX = re.compile(r'^doi:10\.5281/zenodo\.\d+$')

def get_metadata(url):
    '''Find the title of a Zenodo work.'''

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

def zenodo_citations():
    '''Search for Zenodo DOI citations and tally them.'''

    zenodos = []
    citation_report = ''
    for ref in get_all_field_values('999C5a'):
        if ref.startswith('doi:10.5281/zenodo.'):
            search = '999C5a:' + ref
            cites = perform_request_search(p=search, cc='HEP')
            if len(cites):
                if not re.match(ZENODO_REGEX, ref):
                    print 'Problem with DOI extraction:', search, cites
                    continue
                #url = 'https://doi.org/api/handles/' + ref.replace('doi:', '')
                #try:
                #    checkURL(url)
                url = 'https://zenodo.org/record/' + \
                      ref.replace('doi:10.5281/zenodo.', '')
                try:
                    title = get_metadata(url)
                except ValueError:
                    print 'Problem with DOI:', search, cites, '\n'
                    continue
                zenodos.append((len(cites), ref, cites, title))
    for doi in sorted(zenodos, reverse=True):
        #for recid in doi[2]:
        #    url = 'https://inspirehep.net/record/' + str(recid) + \
        #          '/references'
        #    print '   ', url
        #print ' '
        doi_url = 'https://doi.org/' + doi[1].replace('doi:', '')
        citation_report += \
'''{0} citations to {3}
  {2}
  https://inspirehep.net/search?p=999C5a:{1}

'''.format(doi[0], doi[1], doi[3], doi_url)
    return citation_report

def main():
    '''Run the program.'''

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '.out', filename)
    output = open(filename, 'w')
    output.write(zenodo_citations())
    output.close()
    print filename

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

