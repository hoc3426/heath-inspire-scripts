"""Fix incorrectly cited Fermilab report numbers."""

from invenio.search_engine import perform_request_search, \
                                  get_all_field_values, \
                                  get_record
from invenio.bibrecord import print_rec, record_add_field, \
                              record_get_field_instances

import numpy
import re

COUNTER_MAX = 50
FERMILAB = re.compile('^FERMILAB.*', re.I)
FNAL = re.compile('^FNAL.*', re.I)
ARCHAIC = re.compile('^FERMILAB.*(THY|EXP)$', re.I)

YY_FORM = re.compile(r'^[A-Z]+-[A-Z]+-\d\d-\d\d\d.*')
YYYY_FORM = re.compile(r'^[A-Z]+-[A-Z]+-\d\d\d\d-\d\d.*')
DDDD_FORM = re.compile(r'^[A-Z]+-(TM|FN|PROPOSAL)-\d\d\d\d.*')
EXCEPTION = re.compile(r'^FERMILAB-THESIS-200[5-8]-\d\d\d.*')

REF = '999C5r'
REP = '037__a'

REPORT_CITATIONS = get_all_field_values(REF)
FERMILAB_CITATIONS = set([report.upper() for report in REPORT_CITATIONS if
                      FERMILAB.match(report) or FNAL.match(report)])

REPORT_NUMBERS = get_all_field_values(REP)
FERMILAB_REPORTS = set([report.upper() for report in REPORT_NUMBERS if
                    (FERMILAB.match(report) or FNAL.match(report)) and not
                    ARCHAIC.match(report)])

def build_correction_dict():
    """Create a set of records that need to be fixed along with
       a dictionary of bad report numbers and what they should be."""

    bad_recids = set()
    correction_dict = {}
    for bad_report in numpy.setdiff1d(FERMILAB_CITATIONS, FERMILAB_REPORTS):
        if not any((YY_FORM.match(bad_report),
                    YYYY_FORM.match(bad_report),
                    DDDD_FORM.match(bad_report))):
            continue
        for fermilab_report in FERMILAB_REPORTS:
 
            #if bad_report.startswith(fermilab_report):
            #    print bad_report, '\t', fermilab_report
            #continue

            #if not fermilab_report.startswith(bad_report):
            #    continue
            if not any((fermilab_report.startswith(bad_report),
                        bad_report.startswith(fermilab_report))):
                continue   

            if EXCEPTION.match(bad_report):
                if not EXCEPTION.match(fermilab_report):
                    continue


            search = REF + ':' + bad_report
            bad_report_recids = perform_request_search(p=search, cc='HEP')
            if len(bad_report_recids) == 0:
                continue
            search = REP + ':' + fermilab_report
            try:
                report_recid = perform_request_search(p=search, cc='HEP')[0]
            except IndexError:
                continue
            search = 'refersto:recid:' + str(report_recid)
            report_citations = perform_request_search(p=search, cc='HEP')
            missing_citations = set(bad_report_recids) - set(report_citations)
            if len(missing_citations) == 0:
                continue
            bad_recids = bad_recids | missing_citations
            correction_dict[bad_report] = fermilab_report

    return bad_recids, correction_dict


def create_xml(recid, correction_dict):
    """Fix the citations of Fermilab reports."""

    tags = [REF]
    record = get_record(recid)
    correct_record = {}
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    flag = False
    for (tag, field_instance) in \
            [(tag, field_instance) for tag in tags \
             for field_instance in record_get_field_instances(record, \
             tag[0:3], tag[3], tag[4])]:
        correct_subfields = []
        for code, value in field_instance[0]:
            if code == 'r' and value.upper() in correction_dict:
                print 'Was:', value
                value = correction_dict[value.upper()]
                print 'Now:', value
                flag = True
            correct_subfields.append((code, value))
        record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
                         subfields=correct_subfields)
    if flag:
        return print_rec(correct_record)
    else:
        return None

def fix_references(counter_max):
    """Find bad reference citations and fix them."""

    counter = 0
    bad_recids, correction_dict = build_correction_dict()
    print 'Records needing to be fixed:', len(bad_recids)
    print 'Bad report numbers:', len(correction_dict)
    #for key, value in correction_dict.items():
    #    print "{0}\t{1}".format(key, value)

    output = ''
    for recid in bad_recids:
        if counter > counter_max:
            break
        output += create_xml(recid, correction_dict)
        counter += 1
    return output

def main():
    """Prepare a list of fixed references."""

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename, 'w')
    output.write('<collection>')
    output.write(fix_references(COUNTER_MAX))
    output.write('</collection>')
    output.close()
    print filename

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

