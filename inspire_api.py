"""A script to use the INSPIRE API to do automated searching."""

from urllib2 import Request, urlopen, URLError
from bs4 import BeautifulSoup, Comment
import re
import sys

def search_inspire(url):
    """Do an API search at INSPIRE."""
    request = Request(url)
    try:
        response = urlopen(request)
        result = response.read()
        soup = BeautifulSoup(result, "lxml")
        return soup
    except URLError, error:
        print 'Search input =', search
        print 'URL =', url
        print 'No result. Got an error code:', error
        quit()

def get_result(search, number_only=False):
    """
       Takes an INSPIRE search and returns the list of INSPIRE recids.
    """

    url = 'http://inspirehep.net/search?of=xm&rg=5000&ot=001&p=' + \
          search.replace(' ', '+')
    soup = search_inspire(url)
    print soup
    if number_only:
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        print comments
        return int(re.sub(r'\D', '', comments[0]))
    recids = [int(recid.string) for recid in soup.findAll('controlfield')]
    return recids

def main(author):
    """Find the number of citations of an author per year."""

    print 'Citations per year of', author
    print "{0:4} {1:6} {2:6}".format('Year', ' Cites', ' Total')
    search = 'find ea ' + author
    result = get_result(search)
    big_total = 0
    for year in range(1990, 1991):
        total = 0
        for recid in result:
            search = 'refersto:recid:' + str(recid) + ' earliestdate:' + \
                     str(year)
            total += get_result(search, number_only=True)
        big_total += total
        print "{0:4} {1:6} {2:6}".format(year, total, big_total)
    print "{0:11} {2:6}".format('Total', '', big_total)

if __name__ == '__main__':
    try:
        author = str(sys.argv[1:][0])
        main(author)
    except IndexError:
        main('R.P.Feynman.1')
    except KeyboardInterrupt:
        print 'Exiting'

