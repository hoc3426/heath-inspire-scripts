"""Dictionary of experiment categories."""

import lxml.html

from lxml.html.builder import *

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


def create_table():
    """HTML TABLE generation by lxml.html tree.
       Follows http://lxml.de/3.3/api/lxml.html.builder-module.html
    """

    E = ElementMaker(makeelement = html_parser.makeelement)
    #table = E.TABLE()
    #td = E.TD('2016')
    #tr = E.TR('year')
    #tr.append(td)
    #table.append(tr)

    #for key in sorted(EXPT_DICT):
    #    tr = E.TR()
    #    print 'key =', key[0], key[1]
    #    td = E.TD(key[0])
    #    tr.append(td)
    #    td = E.TD(key[1])
    #    tr.append(td)
    #    for x in EXPT_DICT[key]:
    #        #print x[0], x[1]
    #        pass
    #    table.append(tr)

    ul = E.UL()
    for key in sorted(EXPT_DICT):
        link = E.A()
        link.href = BASE_URL + key[0]
        link.text_content = key[1]
        #link = E.a(link)
        #li_input = link + ":" + key[1]
        li = E.LI(link)
        li.append(link)
        ul.append(li)
        ul_sub = E.UL()
        for value in EXPT_DICT[key]:
            li_input = value[0] + ":" + value[1]
            li_sub = E.LI(li_input)
            ul_sub.append(li_sub)
        ul.append(ul_sub)


    out = lxml.html.tostring(ul, encoding='UTF-8', pretty_print=True,
                             method='html').rstrip('\n')

    return out


def unused():
    """Test."""

    for key in sorted(EXPT_DICT):
        print 'key =', key[0], key[1]
        for x in EXPT_DICT[key]:
            print x[0], x[1]

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

