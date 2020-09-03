#!/usr/bin/python

'''Stadardizes references to books and other items.'''

import re
import os
import sys
#import unicodedata

from contextlib import contextmanager

from invenio.intbitset import intbitset
from invenio.search_engine import print_record
from invenio.search_engine import perform_request_search
from invenio.textmarc2xmlmarc import transform_file

COUNTER_MAX = 500

BOOKS = [
['Itzykson', 'quantum field theory', '0486445682', '159194'],
['Baxter', 'exactly solved models in statistical mechanics', '0486462714', '1120339'],
['Carroll', 'spacetime and geometry', '0805387323', '650093'],
['Birrell', 'quantum fields in curved space', '0521278589', '181166'],
['Peskin', 'introduction to quantum field theory', '0201503972', '407703'],
['Halzen', 'quarks and leptons', '0471887412', '205394'],
['Zee', 'quantum field theory in a nutshell', '0691140340', '633051'],
['Zee', 'einstein gravity in a nutshell', '069114558X', '1230427'],
['Quigg', 'gauge theories of the strong', '0805360204', '195708', '1983'],
['Quigg', 'gauge theories of the strong', '0805360204', '195708'],
['Zinn-Justin', 'quantum field theory and critical phenomena', '0198509235', '290037'],
['Deligne', 'quantum fields and strings', '0821820125', '508870'],
['Collins', 'foundations of perturbative qcd', '9781107645257', '922696'],
['Chandrasekhar', 'mathematical theory of black holes', '9780198503705', '224457'],
[r'H\S+bsch', 'bestiary for physicists', '9789810219277', '338506'],
['Streater', 'pct.*spin and statistics.*and all that', '0691070628', '290343'],
['Galperin', 'harmonic superspace*camb', '9780511535109', '570842'],
['Feynman', r'photon[\s\-]+hadron interactions', '9780201360745', '85512'],
['W5013', 'w5013', 'CERN-W5013', '863473'],
['Campbell', 'Black Book of Quantum Chromodynamics', '9780199652747', '1635686'],
['Carey', 'The Optics Of Charged Particle Beams', '9783718605453', '257245'],
['Szekeres', 'A Course in Modern Mathematical Physics', '9780521829601', '669271'],
['Thomas', 'The Structure of the Nucleon', '9783527402977', '559956', '2001'],
['Thomas', 'New Starting Point for Nuclear Physics', 'CERN-TH-3368', '179234', '1982'],
['Esposito','Advanced concepts in quantum mechanics', '9781316121689', '1333796', '2014'],
['Kovchegov', 'Quantum chromodynamics at high energy', '9780521112574', '1217905', '2012'],
['Eides', 'Theory of Light Hydrogenic Bound States', '9783540452690', '1757483', '2007']
]

BOOKS = [BOOKS[18]]

def process_references(book):
    '''
    Look through reference list to find the cited reference and clean it up.
    '''

    print book
    reference_flag = False
    date = None
    counter = 1
    author = book[0]
    title = book[1].lower()
    isbn = book[2]
    isbn_tag = "i"
    recid_book = book[3]
    if len(book) == 5:
        date = book[4]
    if re.search(r"\-", isbn):
        isbn_tag = "r"

    search_author = '999C5:/' + author + '/'
    search_title  = '999C5:/' + title + '/ -refersto:recid:' + recid_book + \
                    ' -999C50:' + recid_book
    x_author = perform_request_search(p=search_author, cc='HEP')
    x_title = perform_request_search(p=search_title, cc='HEP')
    result = list(intbitset(x_author) & intbitset(x_title))
    print len(result), result
    records = []
    if len(result) == 1:
        return None
    new_records = []
    for recid in result:
        records.append(print_record(recid, ot=['999C5'], format='hm'))
    #lines = [record.split('\n') for record in records]]
    for record in records:
        if counter > COUNTER_MAX:
            continue
        new_record = []
        reference_flag = False
        for i in record.split('\n'):
            i = re.sub(r'\n', r'', i)
            i = re.sub(r'</?pre>', '', i)
            i = re.sub(r'<pre style="margin: 1em 0px;">', '', i)
            if re.search(author, i):
                j = i.lower()
                #j = re.sub(r', ', r' ', j)
                #j = re.sub('[ ]+', r' ', j)
                if re.search(title, j) and not re.search(r'$$0', j):
                    if date:
                        if re.search(date, j):
                            i = i + "$$" + isbn_tag + isbn + "$$0" + \
                                str(recid_book) + "$$z1"
                            reference_flag = True
                    else:
                        i = i + "$$" + isbn_tag + isbn  + "$$0" + \
                                str(recid_book) + "$$z1"
                        reference_flag = True
                    if not re.search(r'CURATOR', i):
                        i = i + "$$9CURATOR"
                    if reference_flag:
                        counter += 1
            new_record.append(i + '\n')
        if reference_flag:
            new_records.append(new_record)
    return new_records

@contextmanager
def stdout_redirected(new_stdout):
    save_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield None
    finally:
        sys.stdout = save_stdout


def main():
    '''Run the script.'''

    filename_1 = 'tmp_' + __file__
    filename_1 = re.sub('.py', '_1.out', filename_1)
    output = open(filename_1, 'w')
    new_records = []
    for book in BOOKS:
        new_record = process_references(book)
        if new_record:
            new_records += new_record
    if new_records:
        for record in new_records:
            for line in record:
                print line
                output.write(line)
    output.close()
    if not new_records:
        return None
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    with open(filename, "w") as final_output:
        with stdout_redirected(final_output):
            transform_file(filename_1)
    final_output.close()
    os.unlink(filename_1)
    print filename


if __name__ == '__main__':

    main()

