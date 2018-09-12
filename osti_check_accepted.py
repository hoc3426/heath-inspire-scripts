#!/usr/bin/python
"""Check that we have an accepted manuscript."""

import getopt
import re
import sys

from invenio.search_engine import perform_request_search, \
                                  get_fieldvalues

from osti_web_service import get_url, get_osti_id, \
     check_already_sent
from osti_check_accepted_dois import DOIS, TOTAL, YEARS

def check_record_status(recid):
    """Checks to see if a PDF has already been sent
       or if we have an accepted manuscript.
    """

    if check_already_sent(recid):
        return True
    if not PDF_CHECK:
        return False
    print "Checking accepted status", recid
    accepted_status = get_url(recid)
    if True in accepted_status:
        return True
    elif None in accepted_status:
        if not QUIET:
            print 'No url on:\nhttp://inspirehep.net/record/' + str(recid)
        return False
    else:
        if not QUIET:
            print recid, accepted_status
        return False

def check_doi(doi):
    """Checks to see if we have the DOI in INSPIRE."""

    search = "0247_a:" + doi + " 037:fermilab*"
    result = perform_request_search(p=search, cc='Fermilab')
    if len(result) == 1:
        return result[0]
    else:
        search = "0247_a:" + doi
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1:
            recid = result[0]
            affiliations = get_fieldvalues(recid, "100__u") \
                         + get_fieldvalues(recid, "700__u")
            if "Fermilab" not in affiliations:
                print '** Fermilab affiliation needed on:'
                print 'http://inspirehep.net/record/' + str(recid) + '\n'
                return False

            eprint = None
            report_numbers = get_fieldvalues(recid, "037__a")
            for report_number in report_numbers:
                if report_number.startswith('arXiv'):
                    eprint = report_number
                    break
            if eprint or QUIET == False:
                print '* Fermilab report number needed on:'
                if eprint:
                    print eprint
                print 'http://inspirehep.net/record/' + str(recid) + '\n'
            return False
        else:
            print "** Don't have DOI " + doi
            return False

def calc_output(counter, total):
    """Calculates a percentage."""

    percentage = 100*float(counter)/float(total)
    output = str(counter) + '/' + str(total) + \
             ' (' + "%.2f" % percentage + '%)'
    return output

def check_accepted(input_list, input_total):
    """Checks a list of DOIs or recids to see our accepted rate."""

    counter = 0
    counter_osti = 0
    total = len(input_list)
    open_access = input_total - total
    #print total
    for element in input_list:
        if re.match(r'^10\..*', element):
            element = check_doi(element)
        if str(element).isdigit():
            result = check_record_status(element)
            if result:
                counter += 1
                if get_osti_id(element):
                    counter_osti += 1
    counter += open_access
    counter_osti += open_access
    return [counter, counter_osti, input_total]
    #print 'Number of records: ', calc_output(counter, input_total)
    #print 'Number -> OSTI:    ', calc_output(counter_osti, input_total)

def main():
    """Examines compliance by fiscal year."""

    result = {}
    for year in YEARS:
        result[year] = check_accepted(DOIS[year], TOTAL[year])
    for year in YEARS:
        print 'Fiscal Year:', year
        print 'Number of records: ', calc_output(result[year][0],
                                                 result[year][2])
        print 'Number -> OSTI:    ', calc_output(result[year][1],
                                                 result[year][2])

if __name__ == '__main__':

    PDF_CHECK = False
    QUIET = False
    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 'pq')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    for option, argument in OPTIONS:
        if option == '-p':
            PDF_CHECK = True
        elif option == '-q':
            QUIET = True
    try:
        RECID = ARGUMENTS[0]
        check_accepted([RECID], 1)
    except IndexError:
        try:
            main()
        except KeyboardInterrupt:
            print 'Exiting'

