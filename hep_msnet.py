'''
Script to get MathSciNet IDs
https://mathscinet.ams.org/mathscinet/help/mr_lookup_help.html

https://mathscinet.ams.org/batchmrlookup?&amp;api=xref&amp;qdata=
ISSN | JOUR | AUTH | VID | IID | PID | YNO | TYP | KEY | MRID | TTL

where:
ISSN = ISSN
JOUR = Journal title or abbreviation
AUTH = Author name(s)
VID = Volume number
IID = Issue ID number
PID = Initial Page number
YNO = Year
TYP = Resource type (for compatibility with Crossref; in Batch MR Lookup this value is ignored)
KEY = User supplied key
MRID = Identifier (Mathematical Reviews Number)
TTL = Item title

e.g.
curl "https://mathscinet.ams.org/batchmrlookup?&amp;api=xref&amp;qdata=
  |J.Geom.Phys.|Gerasimov|44||41|2002||539482||"
0393-0440|J. Geom. Phys.|Gerasimov;Kotov|44|1|41|2002||539482|1936305|
  Harmonic twistor formalism and transgression on hyperk\"ahler manifolds.

'''

from urllib2 import Request, urlopen

from invenio.search_engine import perform_request_search
from invenio.intbitset import intbitset
from invenio.search_engine import get_fieldvalues

def find_records():
    search = "find fc m and tc p and jy 2010"
    result_m = perform_request_search(p=search, cc='HEP')
    search = "035__9:msnet"
    result_i = perform_request_search(p=search, cc='HEP')
    result = intbitset(result_m) - intbitset(result_i)
    return result[:5]
    
def create_request(recid):
    journal = get_fieldvalues(recid, '773__p')[0]
    author = get_fieldvalues(recid, '100__a')[0]
    volume = get_fieldvalues(recid, '773__v')[0]
    page = get_fieldvalues(recid, '773__c')[0]
    year = get_fieldvalues(recid, '773__y')[0]
    return "|{0}|{1}|{2}||{3}|{4}||{5}||".format(journal, author,
                                                 volume, page, year, recid)

def get_msnet_id(request):
    url = "https://mathscinet.ams.org/batchmrlookup?&amp;api=xref&amp;qdata="
    #url += "|J.Geom.Phys.|Gerasimov|44||41|2002||539482||"
    url += request
    return urlopen(Request(url)).read().split('|')[9]

def main():
    for recid in find_records():
        request = create_request(recid)
        print request
        print get_msnet_id(request)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
