"""
A system to extract collaboration author lists from tex files.
"""

import gzip
import os
import re
import sys
import tarfile
import time
import urllib
from unidecode import unidecode

from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field
from invenio.textutils import translate_latex2unicode

from hep_aff import get_aff

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

def process_author_name(author):
    """Convert author to INSPIRE form."""

    #re.search(ur'[\u0041-\u005A\u00c0-\u024e\u0370-\u03e0]', name, re.U)
    #http://www.fileformat.info/info/unicode/category/Lu/list.htm


    #print author
    author = author.replace(r'\~', r'xxxx')
    author = author.replace(r'~', r' ')
    author = author.replace(r'xxxx', r'\~')
    if re.search(r'^\\?\"?[A-Z][\.\-]', author):
        author = re.sub(r'(\\?\"?[A-Z][\.\-]\\?\"?[A-Z\s\.\-]*) (\w.*)', \
                        r'\2, \1', author)
    elif re.search(r'^\\?\"?[A-Z]\w+ \\?\"?[A-Z][a-z]+$', author):
        author =  re.sub(r'(^\\?\"?[A-Z]\w+) (\\?\"?[A-Z][a-z]+)', \
                         r'\2, \1', author)
    elif re.search(r'^\\?\"?[A-Z]\w+ \\?\"?[A-Z\.\-]+', author):
        author =  re.sub(r'(.* \\?\"?[A-Z\.\-]+) (.*)', r'\2, \1', author)
    elif re.search(r' [a-z]', author):
        match = re.search(r' ([a-z].*)', author)
        compound_surname = match.group(1)
        firstnames = author.replace(compound_surname, '')
        author = compound_surname + ', ' + firstnames
    author = author.replace(r'\s+', ' ')
    author = author.replace(r'\s+$', '')
    author = re.sub(r'\.\s+', r'.', author)
    author = translate_latex2unicode(author)

    #print author
    return author

def create_xml(eprint, author_dict):
    """Take in the author dictionary and write it out as xml."""

    try:
        search = 'find eprint ' + eprint
        recid = perform_request_search(p=search, cc='HEP')[0]
    except IndexError:
        print 'Do not have eprint', eprint
        return None
    affiliation_dict = {}
    record = {}
    record_add_field(record, '001', controlfield_value=str(recid))
    tag = '100__'
    for key in author_dict:
        subfields = []
        subfields.append(('a', author_dict[key][0]))
        for affiliation in author_dict[key][1]:
            affiliation = translate_latex2unicode(affiliation)
            affiliation = re.sub(r'(\w)\W*$', r'\1', affiliation)
            try:
                #subfields.append(('u', affiliation_dict[affiliation]))
                for inst in affiliation_dict[affiliation]:
                    subfields.append(('u', inst))
            except KeyError:
                inspire_affiliation = get_aff(unidecode(affiliation))
                #subfields.append(('u', inspire_affiliation))
                for inst in inspire_affiliation:
                    subfields.append(('u', inst))
                affiliation_dict[affiliation] = inspire_affiliation
            subfields.append(('v', affiliation))
        record_add_field(record, tag[0:3], tag[3], tag[4], \
                         subfields=subfields)
        tag = '700__'

    return print_rec(record)

def preprocess_file(read_data):
    """Get file into a form that can be properly processed."""

    #Process any user commands in latex.
    command_dict = {}
    for line in read_data.split('\n'):
        match = re.search(r'\\r?e?newcommand\{\\(\w+)\}\{(.*)\}', line)
        if match:
            command_dict[match.group(1)] = match.group(2)
    for key in command_dict:
        command_string = re.compile(r'\\%s\b' % key)
        read_data = re.sub(command_string, command_dict[key], read_data)

    #Remove spaces around braces and commas
    read_data = re.sub(r'[ ]*([\]\}\[\{\,])[ ]*', r'\1', read_data)
    read_data = re.sub(r'^[ ]+', '', read_data)

    read_data = re.sub(r'%.*\n', '', read_data)
    read_data = re.sub(r'}\s*\\affiliation', '}\n\\\\affiliation', read_data)
    read_data = re.sub(r'}\$,\s*', '}$\n', read_data)

    #\author[b,c]{M. Zimmermann} \affiliation[b]{Fermilab}
    read_data = \
        re.sub(r'\\author\[([\w\,]+)\]\{(.*)\}', r'\2$^{\1}$', read_data)
    read_data = \
        re.sub(r'\\affiliation\[([\w\,]+)\]\{(.*)\}', r'$^{\1}$ \2', read_data)
    #\author{M. Zimmermann$^{b,c}$} \affiliation$^{b}$Fermilab} remove \author
    read_data = \
        re.sub(r'\\author\{(.*\$\^\{?[\w\,]+\}?\$)\}', r'\1', read_data)
    read_data = \
        re.sub(r'affiliation\{(\$\^\{?[\w\,]+\}?\$.*)', r'\1', read_data)

    read_data = re.sub(r'[\, ]+\}', '}', read_data)
    read_data = re.sub(r'[\, ]+\$\^', '$^', read_data)

    new_read_data = []
    for line in read_data.split('\n'):
        if re.search('abstract', line):
            break
        else:
            new_read_data.append(line)
    #print new_read_data
    return new_read_data



def process_file(eprint, file_type='tex'):
    """Obtain authors and affiliations from file.
       Creates a dictionary, author_dict, of the form
       {position:[author name, [list of affiliations]]
    """

    with open(eprint + '.' + file_type, 'r') as input_file:
        read_data = input_file.read()
    read_data = preprocess_file(read_data)
    author_position = 0
    author_dict = {}
    affiliation_dict = {}
    babar_flag = False
    author_previous = False
    for line in read_data:
        line = line.replace(r'\\', '')

        #Find author/affiliations for $^{1}$
        match = re.search(r'^(\\?\"?[A-Z].*)\$\^\{?([\w\-\s\,]+)\}?\$', line)
        if match:
            author = match.group(1)
            author = process_author_name(author)
            author_dict[author_position] = [author, match.group(2).split(',')]
            author_position += 1
        match = re.search(r'^\$\^\{?([\w\-\s\,]+)\}?\$\s*(.*)', line)
        if match:
            affiliation_dict[match.group(1)] = match.group(2)

        #Find author/affiliations for \\author, \\affiliation
        match = re.search(r'\\author\{(.*)\}', line)
        if match:
            if author_previous:
                babar_flag = True
            author = process_author_name(match.group(1))
            author_dict[author_position] = [author, []]
            author_position += 1
            author_previous = True
        else:
            author_previous = False
        match = re.search(r'\\affiliation\{(.*)\}', line)
        if match and babar_flag:
            for key in author_dict:
                if not author_dict[key][1]:
                    author_dict[key][1].append(match.group(1))
        elif match:
            try:
                author_dict[author_position - 1][1].append(match.group(1))
            except KeyError:
                print author_position,  match.group(1)

    print 'Number of authors:', author_position
    if affiliation_dict:
        for key in author_dict:
            for position, affiliation_key in enumerate(author_dict[key][1]):
                try:
                    author_dict[key][1][position] = \
                        affiliation_dict[affiliation_key]
                except KeyError:
                    print 'Unknown affkey for', author_dict[key]

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
    filename = re.sub('.py', '_' + eprint + '_correct.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    update = process_file(eprint)
    if update:
        output.write(update)
    output.write('</collection>')
    output.close()

    filename = __file__
    filename.replace('.py', '.log')
    log = open(filename, 'a')
    date_time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    date_time_stamp = date_time_stamp + ' ' + eprint + '\n'
    log.write(date_time_stamp)
    log.close()



if __name__ == '__main__':
    EPRINT = sys.argv[1:]
    try:
        EPRINT = EPRINT[0]
        main(EPRINT)
    except IndexError:
        print "Bad input", EPRINT
    except KeyboardInterrupt:
        print 'Exiting'

