"""Dictionary of Collaboration categories."""

import lxml.html as LH
import lxml.etree as ET

from lxml.html.builder import ElementMaker, html_parser
from BeautifulSoup import BeautifulSoup as BS

import re

FILE = "/afs/cern.ch/project/inspire/info/Experiments/list.webdoc"

BASE_URL = 'http://inspirehep.net/search?cc=Experiments'
BASE_URL += '&sf=experimentname&so=a&p=372__a:'
TITLE = 'WebDoc-Page-Title:Collaboration categories'
PARAGRAPH = """The following list of major collaborations in HEP and related
fields seeks to organize the collaborations by their primary focus.
Where the focus could reasonably be included in more than one
category, we have attempted to select the most meaningful.
For example, although LHCb could be included in the "Hadron collider"
category, its primary focus is the investigation of beauty sector physics
and as such it has been included in the "Heavy Flavor Factory" category.
However, this is not always possible and some collaborations have more than
one category.
This is very much a work in progress and we value your feedback.
If you have any questions or comments please feel free to contact us about it
at
"""

EMAIL = 'experiments@inspirehep.net'
MAILTO = 'mailto:' + EMAIL

STYLE = '''li:last-of-type{
    margin-bottom: 10px;
}'''


EXPT_DICT = {
("1", "Collider Experiments"):[
    {("1.1", "Hadrons"):[
        ("1.1.1", "p anti-p"),
        ("1.1.2", "p p")
        ]
    },
    ("1.2", "e+ e-"),
    ("1.3", "e p"),
    ("1.4", "Heavy Flavor Factory"),
    ("1.5", "Heavy ion"),
    ("1.6", "Detector development")
    ],
("2", "Fixed Target Experiments"):[
    ("2.1", "High-momentum transfer"),
    ("2.2", "Hadron Spectroscopy"),
    ("2.3", "Deep inelastic scattering"),
    ("2.4", "Drell-Yan/Dilepton production"),
    ("2.5", "Flavor physics"),
    ("2.6", "Lepton precision experiments"),
    ("2.7", "Neutron/proton precision experiments")
    ],
("3", "Neutrino (flavor) experiments"):[
    {("3.1", "Accelerator"):[
        ("3.1.1", "short-baseline"),
        ("3.1.2", "long-baseline")
        ]
    },
    {("3.2", "Reactor"):[
        ("3.2.1", "ultra-short-baseline"),
        ("3.2.2", "longer baselines")
        ]
    },
    {("3.3", "Non terrestrial"):[
        ("3.3.1", "Atmospheric"),
        ("3.3.2", "Solar"),
        ("3.3.3", "Cosmic"),
        ]
    },
    ("3.4", "Neutrinoless double beta decay"),
    ("3.5", "Neutrino mass"),
    ],
("4", "Dark matter search experiments"):[
    ("4.1", "Non-accelerator"),
    ("4.2", "Axion search experiments"),
    ("4.3", "Dark Forces")
    ],
("5", "Cosmic ray/Gamma ray experiments"):[
    ("5.1", "Ground array"),
    ("5.2", "Cerenkov array"),
    ("5.3", "Satellite"),
    ("5.4", "Balloon")
    ],
("6", "Other Rare-process/exotic experiments" ):[
    ("6.1", "Proton decay"),
    ("6.2", "Modified gravity and space-time"),
    ("6.3", "Magnetic monopoles"),
    ("6.4", "Fractionally charged particles")
    ],
("7", "Accelerator Test Facility Experiments" ):[
    ("7.1", "Electron and positron beams"),
    ("7.2", "Muon beams"),
    ("7.3", "Proton beams"),
    ("7.4", "Neutrino beams")
    ],
("8", "Astronomy experiments"):[
    ("8.1", "CMB"),
    ("8.2", "Survey"),
    ("8.3", "Supernovae"),
    ("8.4", "Gravitational waves"),
    ("8.5", "Gravitational lensing/Dark matter")
    ],
("9", "Non-experimental"):[
    ("9.1", "Data Analysis"),
    {("9.2", "Simulation tools"):[
        ("9.2.1", "Detector Simulation"),
        ("9.2.2", "Event Simulation")
        ]
    },
    ("9.3", "Parton Distribution Fits"),
    ("9.4", "Lattice Gauge Theory"),
    ("9.5", "Neutrino Physics"),
    ("9.6", "Particle Properties")
   ]
}



ELEMENT = ElementMaker(makeelement=html_parser.makeelement)

def populate_ul(input_ul, input_tuple):
    """Creates the ul list."""
    href_display = input_tuple[0]
    href_link = BASE_URL + input_tuple[0]
    href_link += '*'
    href = ELEMENT.A(href_display, href=href_link)
    li_final = ELEMENT.LI(href, input_tuple[1])
    input_ul.append(li_final)
    return li_final

def create_html_list(experiment_dictionary, ul_top = ELEMENT.UL()):
    """HTML UL LIST generation by lxml.html tree.
       Follows http://lxml.de/3.3/api/lxml.html.builder-module.html
    """

    #ul_top = ELEMENT.UL()
    for key in sorted(experiment_dictionary):
        print 'key =', key
        li_top = populate_ul(ul_top, key)
        ul_sub = ELEMENT.UL()
        for value in experiment_dictionary[key]:
            print '  1  value =', value
            if isinstance(value, tuple):
                print '  2  value =', value
                populate_ul(ul_sub, value)
            elif isinstance(value, dict):
                ul_sub = create_html_list(value, ul_sub)
                li_top.append(ul_sub)
            #print 'ul_sub =', LH.tostring(ul_sub)
            #print ' '
            #print 'ul_top =', LH.tostring(ul_top)
            #print ' '
        li_top.append(ul_sub)
    return ul_top

def create_html(experiment_dictionary):
    """Creates the html for the page."""

    ul_top = create_html_list(experiment_dictionary)

    root = LH.tostring(ul_top) #convert the generated HTML to a string

    comment = ET.Comment(TITLE)
    comment = ET.tostring(comment)

    style = ELEMENT.Style(STYLE, type="text/css")
    style = LH.tostring(style)

    email = ELEMENT.A(EMAIL, href=MAILTO)
    paragraph = ELEMENT.P(PARAGRAPH, email, ".")
    paragraph = LH.tostring(paragraph)
    paragraph = re.sub(r' \.', '.', paragraph)

    root = comment + style + paragraph + root

    soup = BS(root)         #make BeautifulSoup
    out = soup.prettify()   #prettify the html

    return out

def main():
    """Creates and opens a file and writes the table to it."""

    #filename = 'tmp_' + __file__
    #filename = re.sub('.py', '_correct.out', filename)
    filename = FILE
    output = open(filename,'w')
    table = create_html(EXPT_DICT)
    output.write(table)
    output.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

