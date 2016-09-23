"""Dictionary of experiment categories."""

import lxml.html as LH

from lxml.html.builder import ElementMaker, html_parser
from BeautifulSoup import BeautifulSoup as BS

import re

BASE_URL = 'http://inspirehep.net/search?cc=Experiments&p='

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
("3.5", "0nubb")],
("4", "Dark matter search experiments"):[
("4.1", "Non-accelerator"),
("4.2", "Axion search experiments"),
("4.3", "Dark Forces")],
("5", "Cosmic ray experiments"):[
("5.1", "Ground array"),
("5.2", "Cerenkov array"),
("5.3", "Satellite")],
("6", "Other Rare-process non-accelerator experiments" ):[
("6.1", "proton decay"),
("6.2", "modified gravity"),
("6.3", "magnetic monopoles")],
("7", "Astronomy experiments"):[
("7.1", "CMB"),
("7.2", "Survey"),
("7.3", "Supernovae"),
("7.4", "Gravity waves")]
}

ELEMENT = ElementMaker(makeelement=html_parser.makeelement)

def populate_ul(input_ul, input_tuple):
    """Creates the ul list."""
    li_display = input_tuple[0] + ":" + input_tuple[1]
    li_href = input_tuple[0]
    li_final = ELEMENT.A(li_display, href=li_href)
    li_final = ELEMENT.LI(li_final)
    input_ul.append(li_final)
    return li_final

def create_table():
    """HTML TABLE generation by lxml.html tree.
       Follows http://lxml.de/3.3/api/lxml.html.builder-module.html
    """

    #element = ElementMaker(makeelement=html_parser.makeelement)

    ul_top = ELEMENT.UL()
    for key in sorted(EXPT_DICT):
        li_top = populate_ul(ul_top, key)
        ul_sub = ELEMENT.UL()
        for value in EXPT_DICT[key]:
            populate_ul(ul_sub, value)
        li_top.append(ul_sub)


    #out = lxml.html.tostring(ul, encoding='UTF-8', pretty_print=True,
    #                         method='html').rstrip('\n')

    root = LH.tostring(ul_top) #convert the generated HTML to a string
    soup = BS(root)                #make BeautifulSoup
    out = soup.prettify()   #prettify the html

    return out


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

