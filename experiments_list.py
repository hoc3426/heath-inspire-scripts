"""Dictionary of experiment categories."""

import lxml.html as LH
import lxml.etree as ET

from lxml.html.builder import ElementMaker, html_parser
from BeautifulSoup import BeautifulSoup as BS

import re

BASE_URL = 'http://inspirehep.net/search?cc=Experiments'
BASE_URL += '&sf=experimentname&so=a&p=372__a:'
TITLE = 'WebDoc-Page-Title:Major HEP Experiments'
PARAGRAPH = """The following list of major experiments in HEP and related
fields seeks to organize the experiments by their primary characteristic.
Where experiments could reasonably be included in more than one
category, we have attempted to select the most meaningful.
For example, although LHCb could be included in the "Hadron collider" 
category, its primary focus is the investigation of beauty sector physics
and as such it has been included in the "Heavy Flavor Factory" category.
If you have any questions or comments please feel free to contact us about it
at
"""

EMAIL = 'feedback@inspirehep.net'
MAILTO = 'mailto:' + EMAIL

EXPT_DICT = {("1", "Collider Experiments"):[
("1.1", "Hadron Collider"),
("1.2", "e+e- Collider"),
("1.3", "ep Collider"),
("1.4", "Heavy Flavor Factory")],
("2", "Fixed Target Experiments"):[
("2.1", "High-momentum transfer"),
("2.2", "Hadron Spectroscopy"),
("2.3", "Deep inelastic scattering"),
("2.4", "Drell-Yan/Dilepton production"),
("2.5", "Flavor physics"),
("2.6", "Lepton precision experiments")],
("3", "Neutrino (flavor) experiments"):[
("3.1", "Accelerator - Short baseline"),
("3.2", "Accelerator - Long baseline"),
("3.3", "Reactor"),
("3.4", "Neutrino telescopes"),
("3.5", "Neutrinoless double beta decay")],
("4", "Dark matter search experiments"):[
("4.1", "Non-accelerator"),
("4.2", "Axion search experiments"),
("4.3", "Dark Forces")],
("5", "Cosmic ray experiments"):[
("5.1", "Ground array"),
("5.2", "Cerenkov array"),
("5.3", "Satellite")],
("6", "Other Rare-process non-accelerator experiments" ):[
("6.1", "Proton decay"),
("6.2", "Modified gravity"),
("6.3", "Magnetic monopoles")],
("7", "Accelerator Test Facility Experiments" ):[
("7.1", "Electron and positron beams"),
("7.2", "Muon beams"),
("7.3", "Proton beams")],
("8", "Astronomy experiments"):[
("8.1", "CMB"),
("8.2", "Survey"),
("8.3", "Supernovae"),
("8.4", "Gravity waves")]
}

ELEMENT = ElementMaker(makeelement=html_parser.makeelement)

def populate_ul(input_ul, input_tuple):
    """Creates the ul list."""
    href_display = input_tuple[0]
    href_link = BASE_URL + input_tuple[0]
    if len(input_tuple[0]) == 1:
        href_link += '*'
    href = ELEMENT.A(href_display, href=href_link)
    li_final = ELEMENT.LI(href, input_tuple[1])
    input_ul.append(li_final)
    return li_final

def create_table():
    """HTML TABLE generation by lxml.html tree.
       Follows http://lxml.de/3.3/api/lxml.html.builder-module.html
    """

    ul_top = ELEMENT.UL()
    for key in sorted(EXPT_DICT):
        li_top = populate_ul(ul_top, key)
        ul_sub = ELEMENT.UL()
        for value in EXPT_DICT[key]:
            populate_ul(ul_sub, value)
        li_top.append(ul_sub)

    root = LH.tostring(ul_top) #convert the generated HTML to a string

    comment = ET.Comment(TITLE)
    comment = ET.tostring(comment)
  
    email = ELEMENT.A(EMAIL, href=MAILTO)
    paragraph = ELEMENT.P(PARAGRAPH, email, ".")
    paragraph = LH.tostring(paragraph)
    paragraph = re.sub(r' \.', '.', paragraph)

    root = comment + paragraph + root

    soup = BS(root)                #make BeautifulSoup
    out = soup.prettify()   #prettify the html

    return out

def create_title():
    comment = ELEMENT.Comment("some comment")

def main():
    """Creates and opens a file and writes the table to it."""

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename,'w')
    table = create_table()
    output.write(table)
    output.close()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

