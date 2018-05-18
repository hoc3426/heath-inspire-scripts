# -*- coding: utf-8 -*-

""" A script to create a table of all the Fermilab experiments,
    sorted by experiment number. Table displays various information
    about the experiments.
"""

import re

import lxml.html as LH
import lxml.etree as ET
from lxml.html.builder import ElementMaker, html_parser

import unicodedata

from invenio.search_engine import perform_request_search, \
                                  get_fieldvalues
from invenio.bibformat_engine import BibFormatObject as bfo

from hep_convert_email_to_id import get_recid_from_id

print 'cd /web/sites/ccd.fnal.gov/htdocs/techpubs'

VERBOSE = False
#VERBOSE = True

TITLE = "Fermilab Experiments, Proposals and Tests"
STATUS_EXPLANATION = "Status values: Proposed, Approved, Started,\
Completed, Cancelled (terminated after approval) and Rejected."
VERIFIED_EXPLANATION = "Verified: The date the INSPIRE records was \
last verified by the spokesperson. A verification date of 2007 means \
the information has been taken from the final Fermilab Workbook."


SEARCH = "119__a:/^FNAL/ or 119__c:/^FNAL/ or \
419__a:/^FNAL/ or 119__u:Fermilab"
SEARCH += ' -980:ACCELERATOR'

#SEARCH = "419__a:/^FNAL/"
#SEARCH = "001:1108199 or 001:1668677"

SORTER_ALREADY_SEEN = {}

INSPIRE_URL = 'http://inspirehep.net/record/'
PROPOSAL_URL = 'https://ccd.fnal.gov/techpubs/fermilab-reports-proposal.html'

ELEMENT = ElementMaker(makeelement=html_parser.makeelement)

HEADING_DICT = {'number':('119__a', '119__c', '419__a'),
                'collaboration':'710__g',
                'spokespersons':'702__',
                'title':'245__a',
                'status':'046__',
                'institutions':'700__u',
                'verified':'670__d'}
HEADING = HEADING_DICT.keys()
HEADING.append('proposal')

INDEXES = {'Institutions':'110__u', 'Experiments':'119__a',
           'HepNames':'678__a', 'HEP':'001'}

def make_url(input_value, recid):
    '''Make a url based on link and display.'''

    recid = str(recid)
    href_link = INSPIRE_URL + recid
    if re.search(r'search\?p=', recid):
        href_link = re.sub(r'record/', r'', href_link)
    try:
        return ELEMENT.a(input_value, href=href_link)
    except ValueError:
        print 'Problem with', input_value, href_link
        quit()

def populate_td(input_value, recid=None):
    '''Populate the <td> elements of the table'''

    if VERBOSE:
        print 'input_value =', input_value
    if recid and isinstance(input_value, str):
        return make_url(input_value, recid)

    ul_elem = LH.Element("ul")

    for spokesperson in input_value:
        name = spokesperson['name']
        name = re.sub(ur' \(.*', '', name)
        try:
            name = make_url(name, spokesperson['recid'])
        except KeyError:
            pass
        try:
            display = LH.Element("li")
            display.append(name)
        except TypeError:
            display = ELEMENT.li(name)
        dates = ' (' + spokesperson['start'] + ' - '
        if spokesperson['curr'].lower() == 'current':
            dates += 'present)'
            display.append(ELEMENT.b(dates))
        else:
            dates += spokesperson['end'] + ')'
            display.append(ELEMENT.a(dates))

        ul_elem.append(display)
    return ul_elem

def create_html_table(experiments):
    """HTML TABLE generation by lxml.html tree.
       Follows http://lxml.de/3.3/api/lxml.html.builder-module.html
    """

    table = LH.Element("table", attrib={"class":"sortable",
                                        "border":"1"})
    table_tr = ELEMENT.tr()
    table_tr.append(ELEMENT.th('FNAL Number'))
    new_heading = list(HEADING)
    new_heading.remove('number')
    for heading in new_heading:
        width_value = ''
        if heading == 'institutions':
            width_value = '12%'
        elif heading == 'title':
            width_value = '30%'
        table_tr.append(ELEMENT.th(heading.capitalize(), width=width_value))
    table.append(table_tr)
    for _, experiment in sorted(experiments.items(), reverse=True):
    #for _, experiment in sorted(experiments.items()):
        table_tr = ELEMENT.tr()
        table_tr.append(ELEMENT.td(populate_td(experiment['number'],
                                   recid=experiment['recid'])))
        new_heading = list(HEADING)
        new_heading.remove('number')
        for key in new_heading:
            if VERBOSE:
                print key, experiment[key]
            if key == 'proposal':
                if not re.match(r'^FNAL.*\d{4}$', experiment['number']):
                    table_tr.append(ELEMENT.td())
                    continue
                search = '037__a:fermilab-proposal-' + \
                         re.sub(r'\D', '', experiment['number']) + '*'
                result = perform_request_search(p=search, cc='HEP')
                if len(result) == 1:
                    table_tr.append(ELEMENT.td(populate_td(key,
                                    recid=result[0])))
                    continue
                elif len(result) > 1:
                    url_argument = 'search?p=' + search
                    table_tr.append(ELEMENT.td(populate_td(key,
                                    recid=url_argument)))
                    continue
                else:
                    experiment[key] = None
            if experiment[key] == None:
                table_tr.append(ELEMENT.td())
                continue
            try:
                if key == 'status' and experiment[key].startswith('Started:'):
                    experiment[key] = ELEMENT.b(experiment[key])
                table_tr.append(ELEMENT.td(experiment[key]))
            except TypeError:
                try:
                    table_tr.append(ELEMENT.td(populate_td(experiment[key])))
                except KeyError:
                    print key, experiment
            except KeyError:
                print key, experiment
                table_tr.append(ELEMENT.td())
        table.append(table_tr)
    return table


def time_stamp():
    '''Create a time stamp for the html page.'''

    from datetime import datetime
    import pytz

    time_st = pytz.timezone('America/Chicago')
    time_st = datetime.now(time_st).strftime('%Y-%m-%d %H:%M:%S')
    time_st = 'Updated:' + time_st
    return time_st

def create_html(experiments):
    """Creates the html for the page."""



    html = LH.Element("html")
    body = LH.Element("body")
    head = LH.Element("head")
    table = create_html_table(experiments)

    head.append(ELEMENT.title(TITLE))
    body.append(ELEMENT.h1(TITLE))
    body.append(ELEMENT.p(time_stamp()))
    body.append(ELEMENT.p(ELEMENT.a("List of Fermilab Proposals",
                                     href=PROPOSAL_URL)))
    body.append(ELEMENT.p(STATUS_EXPLANATION))
    body.append(ELEMENT.p(VERIFIED_EXPLANATION))
    body.append(table)

    html.append(head)
    html.append(body)
    return ET.tostring(html.getroottree(),
                       encoding='utf-8', pretty_print=True,
                       xml_declaration=True)

def populate_experiments_dict(recid):
    '''Get all the information on each experiment.'''

    experiment = {}
    experiment['recid'] = str(recid)
    for key, value in HEADING_DICT.items():
        if key == 'number':
            sorter = None
            numbers =  get_fieldvalues(recid, value[0])
            numbers += get_fieldvalues(recid, value[1])
            numbers += get_fieldvalues(recid, value[2])
            for number in numbers:
                if number.startswith('FNAL'):
                    experiment[key] = number
                    sorter = re.sub(r'\D', '', number)
            if not sorter:
                number = numbers[0]
                sorter = number
                experiment[key] = number
            if sorter:
                if sorter in SORTER_ALREADY_SEEN:
                    print "Duplicate sorter:", sorter, recid
                    print sorter, SORTER_ALREADY_SEEN[sorter]
                    quit()
                else:
                    SORTER_ALREADY_SEEN[sorter] = recid
        elif key == 'institutions':
            experiment[key] = ' / '.join(sorted(set(get_fieldvalues(recid,
                                                                value))))
        elif key == 'spokespersons':
            spokes = []
            fields = [('name', 'a'), ('idnum', 'i'), ('start', 'd'),
                      ('end', 'e'), ('curr', 'z')]
            for item in bfo(int(recid)).fields(value):
                spoke = {}
                for (field, element) in fields:
                    if item.has_key(element):
                        spoke[field] = re.sub(r'^(\d{4}).*', r'\1',
                                              item[element])
                    elif field != 'idnum':
                        spoke[field] = '???'
                    if VERBOSE:
                        print 'spoke', field, spoke[field]
                if 'idnum' in spoke:
                    spoke_recid = get_recid_from_id(spoke['idnum'])
                    if spoke_recid:
                        spoke['recid'] = str(spoke_recid)
                spoke['name'] = unicodedata.normalize('NFKD', \
                                unicode(spoke['name'])).\
                                encode('ascii','ignore')
                spokes.append(spoke)
            if spokes == []:
                spokes = '???'
            experiment[key] = spokes
        elif key == 'status':
            fields = [('Proposed', 'q'), ('Approved', 'r'),
                      ('Started', 's'),
                      ('Completed', 't'), ('Cancelled', 'c')]
            for item in bfo(int(recid)).fields(value):
                for (field, element) in fields:
                    if item.has_key(element):
                        if not item[element] == '9999':
                            experiment[key] = field + ': ' + item[element]
                #Rejected experiments have Cancelled but not Approved
                if item.has_key('q') and item.has_key('c') and not \
                   item.has_key('r'):
                    experiment[key] = 'Rejected' + ': ' + item['c']

            if key not in experiment:
                experiment[key] = '???'
        else:
            try:
                experiment[key] = get_fieldvalues(recid, value)[0]
            except IndexError:
                experiment[key] = get_fieldvalues(recid, value)
        if experiment[key] == [] or experiment[key] == '':
            experiment[key] = None

    try:
        return {sorter:experiment}
    except UnboundLocalError:
        print 'Problem with:', recid, number


def generate_experiments_dict(search):
    """Finds all the experiments and builds a dictionary."""

    experiments = {}
    result = perform_request_search(p=search, cc='Experiments')
    for recid in result:
        experiments.update(populate_experiments_dict(recid))
    return experiments

def main():
    """Creates the html page with a table of experiments."""

    html_file = 'www/fermilab-experiments.html'
    output = open(html_file, 'w')
    experiments = generate_experiments_dict(SEARCH)
    html = create_html(experiments)
    output.write(html)
    output.close()
    print '\\rm fermilab-experiments.html'
    print 'wget http://hoc.web.cern.ch/hoc/fermilab-experiments.html'
    print ''
    print 'http://ccd.fnal.gov/techpubs/fermilab-experiments.html'

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
