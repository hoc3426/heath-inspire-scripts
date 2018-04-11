""" A script to create a table of all the Fermilab experiments,
    sorted by experiment number. Table displays various information
    about the experiments.
"""

import re

import lxml.html as LH
import lxml.etree as ET

from lxml.html.builder import ElementMaker, html_parser
from BeautifulSoup import BeautifulSoup as BS

from invenio.search_engine import perform_request_search, \
                                  get_fieldvalues
from invenio.bibformat_engine import BibFormatObject as bfo

print 'cd /web/sites/ccd.fnal.gov/htdocs/techpubs'

VERBOSE = False
#VERBOSE = True

SEARCH = "119__a:/^FNAL-[EPT]-1/ or 419__a:/^FNAL-[EPT]-1/"
SEARCH = "119__a:/^FNAL/ or 119__c:/^FNAL/ or \
          419__a:/^FNAL/ or 119__u:Fermilab"
#SEARCH = "119__a:/^FNAL-E-0830/"
#SEARCH = "001:1667178"
SEARCH += ' -980:ACCELERATOR'

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

    if recid:
        href_link = INSPIRE_URL + recid
        try:
            return ELEMENT.A(input_value, href=href_link)
        except ValueError:
            print 'Problem with', input_value, href_link
            quit()

    ul_elem = LH.Element("ul")
    for spokesperson in input_value:
        name = spokesperson['name']
        name = re.sub(r' \(.*', '', name)
        display = name + ' (' + \
                  spokesperson['start'] + ' - '
        if spokesperson['curr'].lower() == 'current':
            display += 'present)'
            display = ELEMENT.B(display)
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
        if heading == 'institutions':
            table_tr.append(ELEMENT.TH(heading.capitalize(), width="12%"))
        else:
            table_tr.append(ELEMENT.TH(heading.capitalize()))
    table.append(table_tr)
    for _, experiment in sorted(experiments.items(), reverse=True):
        table_tr = ELEMENT.TR()
        table_tr.append(ELEMENT.TD(populate_td(experiment['number'],
                                   recid=experiment['recid'])))
        new_heading = list(HEADING)
        new_heading.remove('number')
        for key in new_heading:
            #print key, experiment[key]
            try:
                table_tr.append(ELEMENT.TD(experiment[key]))
            except KeyError:
                try:
                    table_tr.append(ELEMENT.TD(populate_td(experiment[key])))
                except KeyError:
                    table_tr.append(ELEMENT.TD())
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
    comment = ET.Comment("Fermilab Experiments")

    head.append(ELEMENT.TITLE("Fermilab Experiments"))
    body.append(ELEMENT.H1("Fermilab Experiments"))
    body.append(ELEMENT.P(time_stamp()))
    body.append(ELEMENT.P(ELEMENT.A("List of Fermilab Proposals",
                                     href=PROPOSAL_URL)))
    body.append(comment)
    body.append(table)

    html.append(head)
    html.append(body)

    root = LH.tostring(html)

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
                        spoke[field] = item[element]
                    else:
                        spoke[field] = '???'
                spokes.append(spoke)
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


        else:
            try:
                experiment[key] = get_fieldvalues(recid, value)[0]
            except IndexError:
                experiment[key] = get_fieldvalues(recid, value)


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
