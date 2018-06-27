'''
Script to process large batch files sent from AMS.
'''


import cPickle as pickle
import re

from hep_msnet import RECIDS_NOMATCH_FILE, create_xml

MSNET_FILE = 'inspireMathscinetOutput.txt'
MSNET_FILE = 'inspire2MathscinetOutput.txt'
MSNET_FILE = 'inspire3MathscinetOutput.txt'

def main():
    '''
    Parse results from MSNET.
    Create a file to upload.
    '''

    try:
        recids_nomatch = pickle.load(open(RECIDS_NOMATCH_FILE, "rb"))
        print 'Number of non-matching recids 1:', len(recids_nomatch)
    except pickle.UnpicklingError:
        print 'Exiting'
        return None

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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

