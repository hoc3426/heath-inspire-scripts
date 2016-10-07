"""
A system to extract collaboration author lists from tex files.
"""

import gzip
import os
import re
import sys
import tarfile
import urllib

from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field

def download_source(eprint, download_path = ""):
    """Download a tar file from arXiv and choose the right file."""

    download_path = os.path.expanduser(download_path)
    filename = download_path + eprint.replace('/', '-')
    urllib.urlretrieve('http://arxiv.org/e-print/' + eprint, filename + ".dum")
    filename_dum = filename + ".dum"
    try:
        print '%20s  %s' % (filename_dum, tarfile.is_tarfile(filename_dum))
        this_tarfile = tarfile.open(filename_dum, 'r')
        tarfiles = {}
        file_count = 1
        for this_file in this_tarfile.getnames():
            if re.search(r'.(tex|xml)', this_file):
                tarfiles[file_count] = this_file
                print file_count, tarfiles[file_count]
                file_count += 1
        file_choice = raw_input('Chose a file: ')
        file_choice = int(file_choice)
        source_file = this_tarfile.extractfile(tarfiles[file_choice])
        if re.search(r'xml', getattr(source_file, "name")):
            output = open(filename + ".xml", 'w')
            file_type = 'xml'
        else:
            output = open(filename + ".tex", 'w')
            file_type = 'tex'
        output.write(source_file.read())
        output.close()
    except IOError, err:
        print '%20s  %s' % (filename_dum, err)
    gzip_file =  gzip.GzipFile(filename + ".dum")
    source_file = open(filename, "w")
    source_file.write(gzip_file.read())
    source_file.close()
    gzip_file.close()
    os.remove(filename + ".dum")
    os.remove(filename)
    return file_type

def process_author(author):
    """Convert author to INSPIRE form."""

    author = author.replace(r'\~', r'xxxx')
    author = author.replace(r'~', r' ')
    author = author.replace(r'xxxx', r'\~')
    if re.search(r'^[A-Z][\.\-]', author):
        author = re.sub(r'([A-Z][\.\-][A-Z\s\.\-]*) (\w.*)', r'\2, \1', author)
    elif re.search(r'^[A-Z]\w+ [A-Z\.\-]+', author):
        author =  re.sub(r'(.* [A-Z\.\-]+) (.*)', r'\2, \1', author)
    elif re.search(r' [a-z]', author):
        match = re.search(r' ([a-z].*)', author)
        compound_surname = match.group(1)
        firstnames = author.replace(compound_surname, '')
        author = compound_surname + ', ' + firstnames
    author = author.replace(r'\s+', ' ')
    author = author.replace(r'\s+$', '')
    author = re.sub(r'\.\s+', r'.', author)
    return author

def create_xml(eprint, author_dict):
    """Take in the author dictionary and write it out as xml."""

    try:
        search = 'find eprint ' + eprint
        recid = perform_request_search(p=search, cc='HEP')[0]
    except IndexError:
        print 'Do not have eprint', eprint
        return None
    record = {}
    record_add_field(record, '001', controlfield_value=str(recid))
    tag = '100__'
    for key in author_dict:
        subfields = []
        subfields.append(('a', author_dict[key][0]))
        for affiliation in author_dict[key][1]:
            subfields.append(('v', affiliation))
        record_add_field(record, tag[0:3], tag[3], tag[4], \
                         subfields=subfields)
        tag = '700__'

    return print_rec(record)


def process_file(eprint, file_type='tex'):
    """Obtain authors and affiliations from file.
       Creates a dictionary, author_dict, of the form
       {position:[author name, [list of affiliations]]
    """

    filename = eprint + '.' + file_type
    with open(filename, 'r') as input_file:
        read_data = input_file.readlines()
    author_position = 0
    author_dict = {}
    affiliation_dict = {}
    for line in read_data:
        line = line.replace(r'\\', '')
        #Find author
        match = re.search(r'^([A-Z].*)\$\^\{?([\w\s\,]+)\}?\$', line)
        if match:
            author = match.group(1)
            author = process_author(author)
            author_affilations = match.group(2).split(',')
            author_dict[author_position] = [author, author_affilations]
            author_position += 1
        #Find author's affiliations
        match = re.search(r'^\$\^\{?([\w\s\,]+)\}?\$\s*(.*)', line)
        if match:
            affiliation_dict[match.group(1)] = match.group(2)
    print 'Number of authors:', author_position

    for key in author_dict:
        for position, affiliation_key in enumerate(author_dict[key][1]):
            author_dict[key][1][position] = affiliation_dict[affiliation_key]

    return create_xml(eprint, author_dict)

def main(eprint):
    """Get the author list."""

    eprint_tex = eprint + ".tex"
    eprint_xml = eprint + ".xml"
    if os.path.exists(eprint_tex) or os.path.exists(eprint_xml):
        pass
    else:
        download_source(eprint)

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_correct.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    update = process_file(eprint)
    if update:
        output.write(update)
    output.write('</collection>')
    output.close()



if __name__ == '__main__':
    EPRINT = sys.argv[1:]
    try:
        EPRINT = EPRINT[0]
        main(EPRINT)
    except IndexError:
        print "Bad input", EPRINT
    except KeyboardInterrupt:
        print 'Exiting'

