'''Script to find the citations to Zenodo DOIs.'''

import re
from urllib2 import urlopen, URLError

from invenio.search_engine import perform_request_search, \
                                  get_all_field_values

def get_title(url):
    '''Find the title of a Zenodo work.'''

    try:
        webpage = urlopen(url).read()
    except URLError:
        print 'Error opening: ' + url
        return None
    title = str(webpage).split('<title>')[1].split('</title>')[0]
    return title

def zenodo_citations():
    '''Search for Zenodo DOI citations and tally them.'''

    zenodo_regex = re.compile(r'^doi:10\.5281/zenodo\.\d+$')
    zenodos = []
    for ref in get_all_field_values('999C5a'):
        if ref.startswith('doi:10.5281/zenodo.'):
            search = '999C5a:' + ref
            cites = perform_request_search(p=search, cc='HEP')
            if len(cites):
                if not re.match(zenodo_regex, ref):
                    print 'Problem with DOI extraction:', search, cites
                    continue
                #url = 'https://doi.org/api/handles/' + ref.replace('doi:', '')
                #try:
                #    checkURL(url)
                url = 'https://zenodo.org/record/' + \
                      ref.replace('doi:10.5281/zenodo.', '')
                try:
                    title = get_title(url)
                except ValueError:
                    print 'Problem with DOI:', search, cites
                    continue
                zenodos.append((len(cites), ref, cites, title))
    for doi in sorted(zenodos, reverse=True):
        print doi[0], citation(s) to, doi[1]
        print '  ', doi[3]
        #for recid in doi[2]:
        #    url = 'https://inspirehep.net/record/' + str(recid) + \
        #          '/references'
        #    print '   ', url
        print ' '

def main():
    '''Run the program.'''

    zenodo_citations()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

