'''
Script to process large batch files sent from AMS.
'''

import getopt
import cPickle as pickle
import re
import sys

from invenio.intbitset import intbitset
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from hep_msnet import RECIDS_NOMATCH_FILE, create_xml

MSNET_FILE = 'inspireMathscinetOutput.txt'
MSNET_FILE = 'inspire2MathscinetOutput.txt'
MSNET_FILE = 'inspire3MathscinetOutput.txt'
MSNET_FILE = 'tmp_hep_msnet_large_send.out'

def find_recids_nomatch():
    '''Find the records that have already been checked.'''

    try:
        recids_nomatch = pickle.load(open(RECIDS_NOMATCH_FILE, "rb"))
        print 'Number of non-matching recids 1:', len(recids_nomatch)
        return recids_nomatch
    except pickle.UnpicklingError:
        print 'Exiting'
        return None


def generate_list_to_append():
    '''
    Parse results from MSNET.
    Create a file to upload.
    '''

    recids_nomatch = find_recids_nomatch()

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    for line in open(MSNET_FILE, 'r').readlines():
        if '1' not in line:
            continue
        try:
            match_obj = re.match(r'(\d+) (10\.\S+) (\d+)', line)
            recid =  match_obj.group(1)
            msnet = match_obj.group(3)
            output.write(create_xml(recid, msnet))
        except AttributeError:
            try:
                match_obj = re.match(r'^(\d+) (10\.\S+)\s*$', line)
                recid =  match_obj.group(1)
                recids_nomatch.add(int(recid))
            except AttributeError:
                print "Unknown error with:", line
    output.write('</collection>')
    output.close()
    with open(RECIDS_NOMATCH_FILE, "wb") as fname:
        try:
            pickle.dump(recids_nomatch, fname)
        except pickle.PicklingError:
            print "Problem adding:"
    print 'Number of non-matching recids 2:', len(recids_nomatch)
    print filename


def generate_list_to_send(search):
    '''
    Generate a list to send to MSNET.
    '''

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_send.txt', filename)
    output = open(filename,'w')

    recids_nomatch = find_recids_nomatch()

    print search
    result_m = perform_request_search(p=search, cc='HEP')
    print search, len(result_m)
    search = "035__9:msnet"
    result_i = perform_request_search(p=search, cc='HEP')
    search = "0247_2:doi"
    result_d = perform_request_search(p=search, cc='HEP')
    result = intbitset(result_m) & intbitset(result_d) - intbitset(result_i)
    result = result - intbitset(recids_nomatch)
    for recid in result:
        try:
            doi = get_fieldvalues(recid, '0247_a')[0]
        except IndexError:
            print 'Problem with:', recid, doi
            break
        output.write(str(recid) + ',' + doi + '\n')
    output.close()
    print filename

def main(input1, input2=None):
    '''
    Either generate a list to send to MSNET or append the results
    from MSNET.
    '''

    if input1 == '-s':
        generate_list_to_send(input2)
    elif input1 == '-a':
        generate_list_to_append()

if __name__ == '__main__':

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 's:a')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    try:
        for option, argument in OPTIONS:
            print option, argument
            main(option, argument)
    except KeyboardInterrupt:
        print 'Exiting'

