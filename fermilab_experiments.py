# -*- coding: utf-8 -*-

""" A script to create a table of all the Fermilab experiments,
    sorted by experiment number. Table displays various information
    about the experiments.
"""

import re

import lxml.html as LH
import lxml.etree as ET

from lxml.html.builder import ElementMaker, html_parser
from BeautifulSoup import BeautifulSoup as BS
from bs4 import Doctype

from invenio.search_engine import perform_request_search, \
                                  get_fieldvalues
from invenio.bibformat_engine import BibFormatObject as bfo

print 'cd /web/sites/ccd.fnal.gov/htdocs/techpubs'

VERBOSE = False
#VERBOSE = True

SEARCH = "119__a:/^FNAL-[EPT]-1/ or 419__a:/^FNAL-[EPT]-1/"
SEARCH = "119__a:/^FNAL/ or 119__c:/^FNAL/ or \
          419__a:/^FNAL/ or 119__u:Fermilab"
#SEARCH = "119__a:/^FNAL-E-0823/"
SEARCH = "001:1108188"
SEARCH += ' -980:ACCELERATOR'
#SEARCH = "119__a:DUNE"

INSPIRE_URL = 'http://inspirehep.net/record/'
PROPOSAL_URL = 'https://ccd.fnal.gov/techpubs/fermilab-reports-proposal.html'

ELEMENT = ElementMaker(makeelement=html_parser.makeelement)

HEADING_DICT = {'number':('119__a', '119__c', '419__a'),
                'collaboration':'710__g',
                'spokespersons':'702__',
                'title':'245__a',
                'status':'046__',
                'institutions':'700__u'}
HEADING = HEADING_DICT.keys()

INDEXES = {'Institutions':'110__u', 'Experiments':'119__a',
           'HepNames':'678__a', 'HEP':'001'}

def populate_td(input_value, recid=None):
    '''Populate the <td> elements of the table'''

    if VERBOSE:
        print 'input_value =', input_value
    if recid:
        href_link = INSPIRE_URL + recid
        try:
            return ELEMENT.A(input_value, href=href_link)
        except ValueError:
            print 'Problem with', input_value, href_link
            quit()

    ul_elem = LH.Element("ul")

    #Spokesperson name can have Unicode, so special care must be taken.
    for spokesperson in input_value:
        name = spokesperson['name'].encode('utf-8')
        name = re.sub(ur' \(.*', '', name)
        display = name + u' (' + \
                  spokesperson['start'].encode("utf-8") + u' - '
        if spokesperson['curr'].lower() == 'current':
            display += u'present)'
            try:
                display = ELEMENT.B(display)
            except ValueError:
                print 'Problem with:', display
                quit()

        else:
            display += spokesperson['end'] + ')'
        ul_elem.append(ELEMENT.LI(display))
    return ul_elem

def create_html_table(experiments):
    """HTML TABLE generation by lxml.html tree.
       Follows http://lxml.de/3.3/api/lxml.html.builder-module.html
    """

    table = LH.Element("table", attrib={"class":"sortable",
                                        "border":"1"})
    table_tr = ELEMENT.TR()
    table_tr.append(ELEMENT.TH('FNAL Number'))
    new_heading = list(HEADING)
    new_heading.remove('number')
    for heading in new_heading:
        width_value = ''
        if heading == 'institutions':
            width_value = '12%'
        elif heading == 'title':
            width_value = '30%'
        table_tr.append(ELEMENT.TH(heading.capitalize(), width=width_value))
    table.append(table_tr)
    for _, experiment in sorted(experiments.items(), reverse=True):
    #for _, experiment in sorted(experiments.items()):
        table_tr = ELEMENT.TR()
        table_tr.append(ELEMENT.TD(populate_td(experiment['number'],
                                   recid=experiment['recid'])))
        new_heading = list(HEADING)
        new_heading.remove('number')
        for key in new_heading:
            if VERBOSE:
                print key, experiment[key]
            if experiment[key] == None:
                table_tr.append(ELEMENT.TD())
                #table_tr.append(LH.Element('TD'))
                continue
            try:
                if key == 'status' and experiment[key].startswith('Started:'):
                    experiment[key] = ELEMENT.B(experiment[key])
                table_tr.append(ELEMENT.TD(experiment[key]))
            except TypeError:
                try:
                    table_tr.append(ELEMENT.TD(populate_td(experiment[key])))
                except KeyError:
                    print key, experiment
            except KeyError:
                 table_tr.append(ELEMENT.TD())
                #if key == 'spokespersons':
                #    table_tr.append(ELEMENT.TD(populate_td(experiment[key])))
                #else:
                #    table_tr.append(ELEMENT.TD())
                #try:
                #    table_tr.append(ELEMENT.TD(populate_td(experiment[key])))
                #except (KeyError, TypeError):
                #    table_tr.append(ELEMENT.TD())
                #except ValueError:
                #    print 'Problem with metadata', _, experiment[key]
                #    quit()
                #except Exception as ex:
                #    print 'Problem with metadata', _, experiment[key]
                #    template = "An exception of type {0} occurred. \
                #                Arguments:\n{1!r}"
                #    message = template.format(type(ex).__name__, ex.args)
                #    print message

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

    #doctype = LH.Element("doctype") creates open and close element
    #print BS(LH.tostring(doctype))
    #doctype.append("html")
    #doctype = ET.Doctype("html") doesn't work
    html = LH.Element("html")
    body = LH.Element("body")
    head = LH.Element("head")
    table = create_html_table(experiments)
    title = "Fermilab Experiments, Proposals and Tests"
    status_explanation = "Status values: Proposed, Approved, Started,\
                          Completed and Cancelled"
    comment = ET.Comment(title)

    head.append(ELEMENT.TITLE(title))
    body.append(ELEMENT.H1(title))
    body.append(ELEMENT.P(time_stamp()))
    body.append(ELEMENT.P(ELEMENT.A("List of Fermilab Proposals",
                                     href=PROPOSAL_URL)))
    body.append(ELEMENT.P(status_explanation))
    body.append(comment)
    body.append(table)

    html.append(head)
    html.append(body)
    #root = doctype.append(html)
    root = html
    #Look at using html5
    return ET.tostring(root.getroottree(), pretty_print=True, 
                       xml_declaration=True, encoding='utf-8')
    root = LH.tostring(root)

    declaration = "<!doctype html>"
    declaration = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'''

    root = declaration + root

    soup = BS(root)         #make BeautifulSoup
    out = soup.prettify()   #prettify the html

    return out



def populate_experiments_dict(recid):
    '''Get all the information on each experiment.'''

    experiment = {}
    experiment['recid'] = str(recid)
    for key, value in HEADING_DICT.items():
        if key == 'number':
            sorter = None
            numbers =  get_fieldvalues(recid, value[0])
            numbers += get_fieldvalues(recid, value[1])
            for number in numbers:
                if number.startswith('FNAL'):
                    experiment[key] = number
                    sorter = re.sub(r'\D', '', number)
            if not sorter:
                number = numbers[0]
                sorter = number
                experiment[key] = number
        elif key == 'institutions':
            experiment[key] = ' / '.join(sorted(set(get_fieldvalues(recid,
                                                                value))))
        elif key == 'spokespersons':
            spokes = []
            fields = [('name', 'a'), ('id', 'i'), ('start', 'd'),
                      ('end', 'e'), ('curr', 'z')]
            for item in bfo(int(recid)).fields(value):
                spoke = {}
                for (field, element) in fields:
                    if item.has_key(element):
                        spoke[field] = re.sub(r'^(\d{4}).*', r'\1',
                                              item[element])
                    else:
                        spoke[field] = '???'
                    if VERBOSE:
                        print 'spoke', field, spoke[field]
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
