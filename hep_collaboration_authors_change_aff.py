"""
A system to fix the dictionary of affilations conversions.
"""

import cPickle as pickle
import re
import os
from os.path import exists

from invenio.search_engine import perform_request_search
from hep_collaboration_authors import AFFILIATIONS_DONE_FILE

def main():
    """Get the new key value pair."""

    aff_input = raw_input("Affiliation string? ")
    try:
        affiliations_done = pickle.load(open(AFFILIATIONS_DONE_FILE, "rb"))
        print 'Number of affiliations 1:', len(affiliations_done)
    except pickle.UnpicklingError:
        print 'Exiting'
    aff_input = re.sub(r'\W+', ' ', aff_input).upper()
    try:
        print "Currently gives", affiliations_done[aff_input]
    except KeyError:
        print "No current value for", aff_input

    aff_output = raw_input("INSPIRE ICN? ")
    if len(aff_input) < 3 or len(aff_output) < 3:
        print "That's too short. Game over."
        return None
    search = '110__u:"' + aff_output + '"'
    if len(perform_request_search(p=search, cc='Institutions')) != 1:
        print "Invalid ICN", aff_output
        return None

#    try:
#        affiliations_done = pickle.load(open(AFFILIATIONS_DONE_FILE, "rb"))
#        print 'Number of affiliations 1:', len(affiliations_done)
#    except pickle.UnpicklingError:
#        print 'Exiting'
#    aff_input = re.sub(r'\W+', ' ', aff_input).upper()
#    try:
#        print "Currently gives", affiliations_done[aff_input]
#    except KeyError:
#        print "No current value for", aff_input

    if isinstance(aff_output, str):
        affiliations_done[aff_input] = [aff_output]
    elif isinstance(aff_output, list):
        affiliations_done[aff_input] = aff_output
    if exists(AFFILIATIONS_DONE_FILE):
        backup = AFFILIATIONS_DONE_FILE + '.bak'
        if exists(backup):
            os.remove(backup)
        os.rename(AFFILIATIONS_DONE_FILE, backup)

    with open(AFFILIATIONS_DONE_FILE, "wb") as fname:
        try:
            pickle.dump(affiliations_done, fname)
        except pickle.PicklingError:
            print "Problem adding:"
            print aff_input
            print aff_output
    try:
        print "Now gives", affiliations_done[aff_input]
    except KeyError:
        print "No current value for", aff_input
    print 'Number of affiliations 2:', len(affiliations_done)



if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
