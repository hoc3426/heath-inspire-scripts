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

import cPickle as pickle
import itertools
import re
from urllib2 import Request, urlopen, HTTPError

from invenio.search_engine import perform_request_search
from invenio.intbitset import intbitset
from invenio.search_engine import get_fieldvalues
from invenio.bibrecord import print_rec, record_add_field

DIRECTORY = '/afs/cern.ch/project/inspire/TEST/hoc/'
RECIDS_NOMATCH_FILE = 'hep_msnet_recids_nomatch.p'
RECIDS_NOMATCH_FILE = DIRECTORY + RECIDS_NOMATCH_FILE

YEAR = 2010
YEAR = 2009
YEAR = 2008
YEAR = 2007

def find_records():
    '''Looks for candidate records.'''
    search = "find fc g not fc m not fc t and tc p and jy " + str(YEAR)
    result_m = perform_request_search(p=search, cc='HEP')
    search = "035__9:msnet"
    result_i = perform_request_search(p=search, cc='HEP')
    result = intbitset(result_m) - intbitset(result_i)
    return result

def create_request(recid):
    '''Creates a line request for an article.'''

    p_dict = {}
    metadata = [('journal', '773__p'),
                ('author', '100__a'),
                ('volume', '773__v'),
                ('page', '773__c'),
                ('year', '773__y')]
    for (attribute, code) in metadata:
        try:
            p_dict[attribute] = get_fieldvalues(recid, code)[0]
        except IndexError:
            print "Problem with", attribute, recid
            quit()
    p_dict['author'] = re.sub(r'\,.*', '', p_dict['author'])
    p_dict['page'] = re.sub(r'\-.*', '', p_dict['page'])
    return "%0A|{0}|{1}|{2}||{3}|{4}||{5}||".\
    format(p_dict['journal'], p_dict['author'],
           p_dict['volume'], p_dict['page'], p_dict['year'], recid)

def msnet_submit(request):
    '''Submits a request to MSNET.'''

    url = "https://mathscinet.ams.org/batchmrlookup?&amp;api=xref&amp;qdata="
    url += request
    url = re.sub(' ', '%20', url)
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

    try:
        recids_nomatch = pickle.load(open(RECIDS_NOMATCH_FILE, "rb"))
        print 'Number of non-matching recids 1:', len(recids_nomatch)
    except pickle.UnpicklingError:
        print 'Exiting'
        return None


    recids = set(find_records()) - recids_nomatch
    print 'Initial set of candidates:', len(recids)
    request = ''
    for _, recid in enumerate(itertools.islice(recids, 100)):
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
                recids_nomatch.add(int(recid))
                continue
            try:
                output.write(create_xml(recid, msnet))
            except TypeError:
                pass
        except IndexError:
            pass
    output.write('</collection>')
    output.close()

    with open(RECIDS_NOMATCH_FILE, "wb") as fname:
        try:
            pickle.dump(recids_nomatch, fname)
        except pickle.PicklingError:
            print "Problem adding:"

    print 'Number of non-matching recids 2:', len(recids_nomatch)
    print filename

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
