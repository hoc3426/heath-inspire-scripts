# -*- coding: utf-8 -*-
"""Dictionary of experiment categories."""

import lxml.html as LH
import lxml.etree as ET

from lxml.html.builder import ElementMaker, html_parser
from BeautifulSoup import BeautifulSoup as BS
from operator import itemgetter

import re
import time

from invenio.search_engine import perform_request_search
from particle_discoveries_input import DISCOVERY_LIST

FILE = "/afs/cern.ch/project/inspire/info/Experiments/discoveries.webdoc"

INSPIRE_URL = 'http://inspirehep.net/record/'
INSPIRE_URL_SEARCH = 'http://inspirehep.net/search?p='

TITLE = 'WebDoc-Page-Title:Particle Physics Discoveries'
TITLE = 'WebDoc-Page-Title:Nobel Prizes in Particle Physics'
TITLE = 'WebDoc-Page-Title:Prize Winning Discoveries in Particle Physics'
PARAGRAPH = """The following list of Nobel and Wolf Prizes in particle physics.
We have attempted to match the prizes to papers in INSPIRE. Sometimes one
or two representative papers have been chosen when the prize-winning work 
spans decades.
Column headings are sortable.
This is very much a work in progress and we value your feedback. 
If you have any questions or comments please feel free to contact us about it
at
"""

EMAIL = 'feedback@inspirehep.net'
MAILTO = 'mailto:' + EMAIL

SCRIPT = '''MathJax.Hub.Config({
  tex2jax: {inlineMath: [['$','$']],
            processEscapes: true},
  showProcessingMessages: false,
  messageStyle: "none"
});
'''

SCRIPT_URL =  '//cdn.mathjax.org/mathjax/latest/MathJax.js?'
SCRIPT_URL += 'config=TeX-AMS-MML_HTMLorMML'

SORT_SCRIPT = 'sorttable.js'

NOBEL_URL = 'http://www.nobelprize.org/nobel_prizes/physics/laureates/'
WOLF_URL = 'http://www.wolffund.org.il/index.php?dir=site'
WOLF_URL += '&page=winners&language=eng&prize=3016&field=3008&year='

ELEMENT = ElementMaker(makeelement=html_parser.makeelement)

HEADING = ['Discovery', 'Year', 'Citations', 'Experiment',
           'Affiliation', 'Nobel Prize', 'Nobel Laureates',
           'Wolf Prize', 'Wolf Laureates']

INDEXES = {'Institutions':'110__u', 'Experiments':'119__a',
           'HepNames':'678__a', 'HEP':'001'}

def populate_td(href_display, href_link=None, collection=None, \
                nobel=False, citations=False, wolf=False):
    """Creates the ul list."""
    if citations:
        if isinstance(href_display, str):
            search = 'refersto:recid:' + href_display
            cites = len(perform_request_search(p=search, cc='HEP'))
        elif isinstance(href_display, tuple):
            cites = []
            for recid in href_display:
                search = 'refersto:recid:' + recid
                cites += perform_request_search(p=search, cc='HEP')
            cites = set(cites)
            cites = len(cites)
        cites = str(cites)
        if len(cites) > 3:
            cites = cites[:-3] + ',' + cites[-3:]
        return ELEMENT.TD(str(cites), align="right")
    if nobel:
        href_link = NOBEL_URL + href_display
    if wolf:
        href_link = WOLF_URL + href_display
    if isinstance(href_link, str):
        if href_link.isdigit():
            href_link = INSPIRE_URL + href_link
        elif collection in INDEXES:
            href_link = INDEXES[collection] + ':"' + href_link + '"'
            href_link = INSPIRE_URL_SEARCH + \
                    href_link
    elif isinstance(href_link, tuple):
        url = ''
        for value in href_link[1:]:
            url += '+or+' + INDEXES[collection] + ':"' + value + '"'
        href_link = INSPIRE_URL_SEARCH + \
                    INDEXES[collection] + ':"' + href_link[0] + '"' + url
    if INSPIRE_URL_SEARCH in href_link:
        href_link += '&cc=' + collection


    #elif isinstance(href_link, tuple):
    #    url = ''
    #    for recid in href_link[1:]:
    #        url += '+or+001:' + recid
    #    href_link = INSPIRE_URL_SEARCH + \
    #                '001:' + href_link[0] + \
    #                url
    #elif href_link.isdigit():
    #    href_link = INSPIRE_URL + href_link
    #else:
    #    if db in INDEXES:
    #        href_link = INDEXES[db] + ':"' + href_link + '"'
    #
    #    href_link = INSPIRE_URL_SEARCH + \
    #                href_link
    #    if db:
    #        href_link += '&cc=' + db
    try:
        href = ELEMENT.A(href_display.replace('"', ''), href=href_link)
    except ValueError:
        print 'Problem with', href_display, href_link
        quit()
    return ELEMENT.TD(href)

def create_html_table(discovery_list):
    """HTML TABLE generation by lxml.html tree.
       Follows http://lxml.de/3.3/api/lxml.html.builder-module.html
    """

    #table = ELEMENT.TABLE(attrib={"class":"sortable", "border":"1"})
    table = LH.Element("table", attrib={"class":"sortable", 
                                        "border":"1"})
    table_tr = ELEMENT.TR()
    for heading in HEADING:
        table_tr.append(ELEMENT.TH(heading))
    table.append(table_tr)
    #for discovery in discovery_list:
    #discovery_list_nobel = [x for x in discovery_list if 'nobel' in x]
    #discovery_list = discovery_list_nobel
    for discovery in sorted(discovery_list, key=itemgetter('year'),
                            reverse=True):
        if ('nobel' not in discovery or discovery['nobel'] == '') and \
           'wolf' not in discovery:
            continue
        table_tr = ELEMENT.TR()
        try:
            table_tr.append(ELEMENT.TD(discovery['discovery']))
        except ValueError:
            print 'Problem with', discovery['discovery']
        table_tr.append(populate_td(discovery['year'], discovery['papers'],
                        collection='HEP'))
        table_tr.append(populate_td(discovery['papers'], citations=True, \
                        collection='HEP'))
        try:
            if isinstance(discovery['exp'], tuple):
                table_tr.append(populate_td(discovery['exp'][0], \
                    discovery['exp'][1], collection='Experiments'))
            else:
                table_tr.append(populate_td(discovery['exp'], \
                    discovery['exp'], collection='Experiments'))
        except KeyError:
            table_tr.append(ELEMENT.TD())
        try:
            if isinstance(discovery['lab'], tuple):
                table_tr.append(populate_td(discovery['lab'][0], \
                                discovery['lab'][1], \
                                collection='Institutions'))
            else:
                table_tr.append(populate_td(discovery['lab'], \
                                discovery['lab'], \
                                collection='Institutions'))
        except KeyError:
            table_tr.append(ELEMENT.TD())


        try:
            table_tr.append(populate_td(discovery['nobel'], nobel=True))
            table_tr.append(populate_td(discovery['laureates'], \
                            'Nobel Prize Physics ' + discovery['nobel'], \
                            collection='HepNames'))
        except KeyError:
            table_tr.append(ELEMENT.TD())
            table_tr.append(ELEMENT.TD())

        try:
            table_tr.append(populate_td(discovery['wolf'], wolf=True))
            table_tr.append(populate_td(discovery['laureates_wolf'], \
                            'Wolf Prize Physics ' + discovery['wolf'], \
                            collection='HepNames'))
        except KeyError:
            table_tr.append(ELEMENT.TD())
            table_tr.append(ELEMENT.TD())



        #for info in discovery:
        #    if isinstance(info, tuple):
        #        table_tr_td = populate_td(info)
        #    else:
        #        table_tr_td = ELEMENT.TD(info)
        #    table_tr.append(table_tr_td)
        table.append(table_tr)
    return table

def create_html():
    """Creates the html for the page."""

    table = create_html_table(DISCOVERY_LIST)

    root = LH.tostring(table) #convert the generated HTML to a string

    comment = ET.Comment(TITLE)
    comment = ET.tostring(comment)

    script = ELEMENT.Script(SCRIPT, type="text/x-mathjax-config")
    script = LH.tostring(script)

    script2 = ELEMENT.Script(src=SCRIPT_URL, type="text/javascript")
    script2 = LH.tostring(script2)

    script3 = ELEMENT.Script(src=SORT_SCRIPT, type="text/javascript")
    script3 = LH.tostring(script3)


    email = ELEMENT.A(EMAIL, href=MAILTO)
    paragraph = ELEMENT.P(PARAGRAPH, email, ".")
    date_time = 'Updated ' + time.strftime('%Y-%m-%d %H:%M:%S')
    date_time = ELEMENT.I(date_time)
    paragraph.append(date_time)
    paragraph = LH.tostring(paragraph)
    paragraph = re.sub(r' \.', '.', paragraph)

    root = comment + script + script2 + script3 + paragraph + root

    soup = BS(root)         #make BeautifulSoup
    out = soup.prettify()   #prettify the html

    return out

def main():
    """Creates and opens a file and writes the table to it."""

    #filename = 'tmp_' + __file__
    #filename = re.sub('.py', '_correct.out', filename)
    filename = FILE
    output = open(filename,'w')
    html = create_html()
    output.write(html)
    output.close()
    print FILE
    print 'http://inspirehep.net/info/Experiments/discoveries'

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

