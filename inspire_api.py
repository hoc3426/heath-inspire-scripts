"""A script to use the INSPIRE API to do automated searching."""

from urllib2 import Request, urlopen, URLError
from bs4 import BeautifulSoup, Comment
import re
import sys
import time

START_YEAR = 1990
END_YEAR   = 1992

def search_inspire(url):
    """Do an API search at INSPIRE."""
    request = Request(url)
    try:
        response = urlopen(request)
        result = response.read()
        soup = BeautifulSoup(result, "lxml")
        return soup
    except URLError, error:
        print 'URL =', url
        print 'No result. Got an error code:', error
        quit()

def get_result(search, number_only=False):
    """
       Takes an INSPIRE search and returns the list of INSPIRE recids.
    """
    number = '20000'
    if number_only:
        number = '1'
    url = 'http://inspirehep.net/search?of=xm&rg=' + number + '&ot=001&p=' + \
          search.replace(' ', '+')
    soup = search_inspire(url)
    if number_only:
        try:
            comments = soup.findAll(text=lambda text:isinstance(text, Comment))
            return int(re.sub(r'\D', '', comments[0]))
        except IndexError:
            return 0
    recids = [int(recid.string) for recid in soup.findAll('controlfield')]
    return recids

def main(author):
    """Find the number of citations of an author per year."""

    search = 'find ea ' + author
    result = get_result(search)

    print """
    Citations per year of the %d papers of %s
    Time period: %d-%d
    """ % (len(result), author, START_YEAR, END_YEAR)

    print "{0:4} {1:6} {2:6}".format('Year', ' Cites', ' Total')
    sleep_time = 1
    big_total = 0
    for year in range(START_YEAR, END_YEAR):
        total = 0
        year_next = year + 2
        search = 'exactauthor:' + author + ' date:1900->' + str(year_next)
        #print search
        for recid in get_result(search):
            time.sleep(sleep_time)
            search = 'refersto:recid:' + str(recid) + ' earliestdate:' + \
                     str(year)
            total += get_result(search, number_only=True)
            #print search, total
        big_total += total
        print "{0:4} {1:6} {2:6}".format(year, total, big_total)
    print "{0:11} {2:6}".format('Total', '', big_total)

if __name__ == '__main__':
    try:
        main(str(sys.argv[1:][0]))
    except IndexError:
        print "No author selected using R.P. Feynman"
        print "To choose an author, run the command, e.g.,"
        print "python inspire_api.py j.j.schwinger.1"
        main('R.P.Feynman.1')
    except KeyboardInterrupt:
        print 'Exiting'

