#!/usr/bin/python
"""Check that we have an accepted manuscript."""

import logging
import re
from Counter import Counter

from invenio.search_engine import get_fieldvalues, perform_request_search, \
                                  search_unit
from osti_web_service import check_already_sent
from osti_check_accepted_dois import DOIS, YEARS

DIVISIONS = ['A', '(AD|APC)', 'AE', 'CD', 'CMS', 'DI', 'E', 'LBNF', 'ND',
             'PPD', 'T', 'TD']
DIVISIONS = ['(AD|APC)', 'CD', 'CCD', 'DI', 'ESH', 'FESS', 'LBNF', 'ND',
             '(A|AE|CMS|E|PPD|T)', 'PIP2', 'QIS', 'SCD', 'TD', 'WDRS', 'V']

JOURNALS = []
LOGFILE = 'tmp_' + __file__
LOGFILE = re.sub('.py', '.log', LOGFILE)
logging.basicConfig(filename=LOGFILE, filemode='w',
                    format='%(message)s',
                    level=logging.INFO)

def get_journal(recid):
    """Get the journal."""

    try:
        JOURNALS.append(get_fieldvalues(recid, '773__p')[0])
    except IndexError:
        logging.info('No journal on:')
        logging.info('  https://old.inspirehep.net/record/' + str(recid))

def get_fermilab_report(recid):
    """Get the Fermilab report number."""

    report = None
    accepted = False
    report_numbers = get_fieldvalues(recid, "037__a") + \
                     get_fieldvalues(recid, "037__z")
    for report_number in report_numbers:
        if  report_number.startswith('FERMILAB'):
            report = report_number
        if report_number.lower() == 'osti_accepted':
            accepted = True
    return (report, accepted)


def recid_from_doi(doi):
    """Find if we have a DOI."""

    try:
        #return search_unit(p=doi, f='0247*', m='a')[0]
        search = '0247_a:' + doi
        result = perform_request_search(p=search, cc='Fermilab')
        result2 = perform_request_search(p=search, cc='HEP')
        result = result or result2
        return result[0]
    except IndexError:
        return None

def calculate_output(numerator, denominator):
    """Calculates a percentage."""

    fraction = str(numerator) + '/' + str(denominator)
    if denominator:
        percentage = 100*float(numerator)/float(denominator)
        flag = ' '
        if percentage < 85:
            flag = '*'
        output = '{0:>8s} ({1:>6.2f}%){2}'.format(fraction, percentage, flag)
    else:
        output = '{0:>8s} ({1:>7}) '.format(fraction, 'N/A')
    return output

def examine(doi):
    """
    Checks the status of a record to see if it has a DOI
    and if it does, if it has a Fermilab report number.
    """

    recid = recid_from_doi(doi)
    if not recid:
        logging.info('Need DOI')
        logging.info('  https://doi.org/{0}'.format(doi))
        return (False, None)
    get_journal(recid)
    report, accepted = get_fermilab_report(recid)
    if not report:
        logging.info('* Need report')
        logging.info('  https://old.inspirehep.net/record/{0}'.format(recid))
        return (False, None)
    if re.match(r'.*\d$', report):
        logging.info('* No division or section {0}'.format(report))
        logging.info('  https://old.inspirehep.net/record/{0}'.format(recid))
    if accepted:
        return (True, report)
    if check_already_sent(recid):
        return (True, report)
    else:
        logging.info('Need accepted version {0}'.format(report))
        logging.info('  https://old.inspirehep.net/record/{0}'.format(recid))
        return (False, report)

def process_dois(dois):
    """Go through a list of DOIs and check our holdings."""

    report_numbers_good = set()
    report_numbers_bad = set()
    for doi in dois:
        (sent_to_osti, report) = examine(doi)
        if not report:
            continue
        if sent_to_osti:
            report_numbers_good.add(report)
        else:
            report_numbers_bad.add(report)
    return (report_numbers_good, report_numbers_bad)


def main():
    """Examines compliance by fiscal year."""

    for year in YEARS:
        logging.info(year)
        (report_numbers_good, report_numbers_bad) = process_dois(DOIS[year])
        print 'Fiscal Year:', year
        print 'Sent to OSTI:', calculate_output(len(report_numbers_good),
                                                len(DOIS[year]))
        for division in DIVISIONS:
            division_good = division_bad = 0
            for report in report_numbers_good:
                if re.match(r'.*-' +  division + r'\b.*', report):
                    division_good += 1
            for report in report_numbers_bad:
                if re.match(r'.*-' +  division + r'\b.*', report):
                    division_bad += 1
            print "  {0:25s} {1:>20s}".format(division,
                  calculate_output(division_good,
                                   division_good + division_bad))
            #print "  {0:25s} {1:>20s}".format(division,
            #      calculate_output(len(report_numbers_good)-division_good,
            #                       len(DOIS[year])-(division_good +
            #                           division_bad)))

        labwide_good = labwide_bad = 0
        labwide_good_reports = []
        for report in report_numbers_good:
            if re.match(r'.*-\d+$', report):
                labwide_good += 1
                labwide_good_reports.append(report)
        for report in report_numbers_bad:
            if re.match(r'.*-\d+$', report):
                labwide_bad += 1
        print "  {0:25s} {1:>20s}".format('No div.',
              calculate_output(labwide_good,
                               labwide_good + labwide_bad))
        #print labwide_good_reports

    JOURNALS.sort()
    for key in Counter(JOURNALS).most_common():
        logging.info('{0:30s} {1:>4d}'.format(key[0], key[1]))
#Counter(JOURNALS)[key]))

    print LOGFILE


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

