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
TYP = Resource type (for compatibility with Crossref;
      in Batch MR Lookup this value is ignored)
KEY = User supplied key
MRID = Identifier (Mathematical Reviews Number)
TTL = Item title

e.g.
curl "https://mathscinet.ams.org/batchmrlookup?&amp;api=xref&amp;qdata=
  |J.Geom.Phys.|Gerasimov|44||41|2002||539482||"
0393-0440|J. Geom. Phys.|Gerasimov;Kotov|44|1|41|2002||539482|1936305|
  Harmonic twistor formalism and transgression on hyperk\"ahler manifolds.

'''

import re

from urllib2 import Request, urlopen, HTTPError

from invenio.search_engine import perform_request_search
from invenio.intbitset import intbitset
from invenio.search_engine import get_fieldvalues
from invenio.bibrecord import print_rec, record_add_field

def find_records():
    '''Looks for candidate records.'''
    search = "find fc m and tc p and jy 2010"
    result_m = perform_request_search(p=search, cc='HEP')
    search = "035__9:msnet"
    result_i = perform_request_search(p=search, cc='HEP')
    result = intbitset(result_m) - intbitset(result_i)
    return result[:5]

def create_request(recid):
    '''Creates a line request for an article.'''

    journal = get_fieldvalues(recid, '773__p')[0]
    author = get_fieldvalues(recid, '100__a')[0]
    author = re.sub(r'\,.*', '', author)
    volume = get_fieldvalues(recid, '773__v')[0]
    page = get_fieldvalues(recid, '773__c')[0]
    page = re.sub(r'\-.*', '', page)
    year = get_fieldvalues(recid, '773__y')[0]
    return "%0A|{0}|{1}|{2}||{3}|{4}||{5}||".format(journal, author,
                                                 volume, page, year, recid)

def msnet_submit(request):
    '''Submits a request to MSNET.'''

    url = "https://mathscinet.ams.org/batchmrlookup?&amp;api=xref&amp;qdata="
    #url += "|J.Geom.Phys.|Gerasimov|44||41|2002||539482||"
    url += request
    try:
        return urlopen(Request(url)).read()
    except HTTPError:
        print "Problem with:", url
        quit()
    except IndexError:
        return None

def create_xml(recid, msnet):
    '''Creates xml record to append MSNET ID'''

    common_fields = {}
    common_tags = {}
    record_add_field(common_fields, '001', controlfield_value=str(recid))
    common_tags['035__'] = [('9', 'MSNET'), ('a', msnet)]
    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    return print_rec(common_fields)

def main():
    '''
    Look for records that need an MSNET ID.
    Prepare a submission to send.
    Parse results from MSNET.
    Create a file to upload.
    '''

    request = ''
    for recid in find_records():
        request += create_request(recid)
    msnet_result = msnet_submit(request)

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    for msnet_record in msnet_result.split('\n'):
        try:
            recid = msnet_record.split('|')[8]
            msnet = msnet_record.split('|')[9]
            if msnet == '':
                continue
            try:
                output.write(create_xml(recid, msnet))
            except TypeError:
                pass
        except IndexError:
            pass
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
