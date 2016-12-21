"""
A system to extract collaboration author lists from tex files.
"""

import getopt, gzip
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

def download_source(eprint, download_path = ""):
    """Download a tar file from arXiv and choose the right file."""

    download_path = os.path.expanduser(download_path)
    filename = download_path + eprint.replace('/', '-')
    urllib.urlretrieve('http://arxiv.org/e-print/' + eprint, filename + ".dum")
    filename_dum = filename + ".dum"
    try:
        #print '%20s  %s' % (filename_dum, tarfile.is_tarfile(filename_dum))
        try:
            this_tarfile = tarfile.open(filename_dum, 'r')
        except tarfile.ReadError:
            print 'No tarfile for', eprint
            return None
        tarfiles = {}
        file_count = 0
        for this_file in this_tarfile.getnames():
            if re.search(r'(tex|xml)$', this_file):
                file_count += 1
                tarfiles[file_count] = this_file
                print file_count, tarfiles[file_count]
        if file_count == 1:
            file_choice = file_count
        else:
            file_choice = raw_input('Choose a file: ')
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

def author_first_last(author):
    """Determines the components of the author's name.."""

    #Anything ending in a period is the firstname block
    if re.search(ur'\. [^\.]+$', author, re.U):
        return re.sub(ur'(.*\.) ([^\.]+)', r'\2, \1', author, re.U)
    #Anything with only two parts
    if re.search(ur'^\S+ \S+$', author, re.U):
        return re.sub(ur'(.*) (.*)', r'\2, \1', author, re.U)
    #Anything starting with a lower-case letter, e.g. Oscar de la Hoya
    pattern = re.compile(ur' (\w+)', re.U)
    for last_guess in re.findall(pattern, author):
        firstname = False
        if last_guess in ['Da', 'De', 'Del', 'Della', 'Van', 'Von']:
            firstname = re.sub(last_guess + u'.*', '', author)
        elif last_guess[0].lower() == last_guess[0]:
            firstname = re.sub(last_guess + u'.*', '', author)
        if firstname:
            return author.replace(firstname, '') + ',' + firstname
    match = re.match(u'(.*) (.*)', author, re.U)
    if match:
        return match.group(2) + u', ' + match.group(1)
    return author


def process_author_name(author):
    """Convert author to INSPIRE form."""

    #re.search(ur'[\u0041-\u005A\u00c0-\u024e\u0370-\u03e0]', name, re.U)
    #http://www.fileformat.info/info/unicode/category/Lu/list.htm
    #for i in range(int('c0', 16), int('024e', 16)+1):
    #    print unichr(int("{0:0{1}x}".format(i, 4), 16))

    #author = translate_latex2unicode(author)
    author = author.replace(r'\.', r'xxxx')
    author = author.replace(r'.', '. ')
    author = author.replace(r'xxxx', r'\.')
    author = re.sub('[ ]+', ' ', author)
    author = re.sub(r'\\(cor|corauth|fn)ref\{\w+\}', r'', author)
    author = re.sub(r'\}?\\thanks\{\\?.*\}?', r'', author)
    author = author.replace(r'\~', r'xxxx')
    author = author.replace(r'~', r' ')
    author = author.replace(r'xxxx', r'\~')
    author = translate_latex2unicode(author)
    author = author_first_last(author)

    #Get author name into Last, First format.
    #Include A-Zuh to allow for Russian Yu. and German Th.
    #compound_letters = ["Ch", "Chr", "Gy", "Iu", "Ju",
    #                    "Kh", "Md", "Ph", "Sh", "St",
    #                    "Sz", "Th", "Ts", "Ya", "Ye",
    #                    "Yu", "Zh", "Zs"
    #                   ]

    #if re.search(r'^\\?\"?[A-Z][uh]?[\.\-]', author):
    #    author = re.sub(r'(\\?\"?[A-Z][uh]?[\.\-]\\?\"?[A-Zuh\s\.\-]*)
    #                    (\w.*)', \
    #                    r'\2, \1', author)
    #elif re.search(r'^\\?\"?[A-Z]\w+ \\?\"?[A-Z][a-z]+$', author):
    #    author =  re.sub(r'(^\\?\"?[A-Z]\w+) (\\?\"?[A-Z][a-z]+)', \
    #                     r'\2, \1', author)
    #elif re.search(r'^\\?\"?[A-Z]\w+ \\?\"?[A-Zuh\.\-]+', author):
    #    author =  re.sub(r'(.* \\?\"?[A-Zu\.\-]+) (.*)', r'\2, \1', author)
    #elif re.search(r' [a-z]', author):
    #    match = re.search(r' ([a-z].*)', author)
    #    compound_surname = match.group(1)
    #    firstnames = author.replace(compound_surname, '')
    #    author = compound_surname + ', ' + firstnames
    author = re.sub(r'\s+', ' ', author)
    author = re.sub(r'\s+$', '', author)
    author = re.sub(r'^\s+', '', author)
    author = re.sub(r'\.\s+', r'.', author)
    author = re.sub(r'(.*) ([IVJr.]+), (.*)', r'\1, \3, \2', author)
    #author = translate_latex2unicode(author)

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
                for inst in affiliation_dict[affiliation]:
                    inst = re.sub(r'^\s+', '', inst)
                    subfields.append(('u', inst))
            except KeyError:
                inspire_affiliation = get_aff(unidecode(affiliation))
                for inst in inspire_affiliation:
                    inst = re.sub(r'^\s+', '', inst)
                    subfields.append(('u', inst))
                affiliation_dict[affiliation] = inspire_affiliation
            subfields.append(('v', affiliation))
        record_add_field(record, tag[0:3], tag[3], tag[4], \
                         subfields=subfields)
        tag = '700__'

    return print_rec(record)

def preprocess_file_braces(read_data):
    """Try to close braces."""
    #print repr(read_data)
    read_data = re.sub(r'\\institute\{', \
                       r'\\section*{Affiliations}', read_data)
    read_data = re.sub(r'(\{[^\}]*)\n+', r'\1', read_data)
    read_data = re.sub(r'(\{[^\}]*\{[^\}]*\}[^\}]*)\n+', r'\1', read_data)
    read_data = re.sub(r'([\{\(\[])\s+', r'\1', read_data)
    read_data = re.sub(r'\s+([\}\)\]])', r'\1', read_data)
    read_data = read_data.replace(r'\\', '\n')
    #print repr(read_data)
    return read_data

def preprocess_file(read_data):
    """Get file into a form that can be properly processed."""

    read_data = preprocess_file_braces(read_data)

    #Process any user commands in latex.
    command_dict = {}
    for line in read_data.split('\n'):
        match = None
        if re.search('command', line):
            match = re.search(r'\\r?e?newcommand\*?\{\\(\w+)\}\{(.*)\}', line)
        elif re.search(r'\\def\\', line):
            match = re.search(r'\\def\\(\w+)\{(.*)\}', line)
        if match:
            command_value = match.group(2)
            if re.search(r'^\\\w', command_value):
                command_value = '\\' + command_value
            command_dict[match.group(1)] = command_value
    for key in command_dict:
        try:
            command_string = re.compile(r'\\%s\b' % key)
            read_data = re.sub(command_string, command_dict[key], read_data)
        except re.error:
            print '!!! Problem with user commands:', key, command_dict[key]
            sys.exit()

    #Special treatment for BaBar
    for line in read_data.split('\n'):
        #BaBar \affiliation{Fermilab$^{a}$, SLAC$^{b}$}
        if re.search(r'\\affiliation\{.*\$\^\{?[abc]\}?\$', line):
            line_new = re.sub(r'\$\^\{?[abc]\}?\$', ' and ', line)
            read_data = read_data.replace(line, line_new)
        elif re.search(r'\\author\{.*\$\^\{?[abc]+\}?\$', line):
            line_new = re.sub(r'[ ]*\$\^\{?[abc]+\}?\$[ ]*', '', line)
            read_data = read_data.replace(line, line_new)
        elif re.search(r'\\author\{.*\\altaffiliation', line):
            line_new = re.sub(r'\\altaffiliation.*', '', line)
            read_data = read_data.replace(line, line_new)

    #Special treatment for DES and Fermi-LAT
    astro_aff_counter = 0
    for line in read_data.split('\n'):
        if re.search(r'\\section\*\{Affiliations\}', line):
            astro_aff_counter = 1
        if astro_aff_counter and re.search(r'^\\item', line):
            line_new = \
                re.sub(r'^\\item', r'$^{' + str(astro_aff_counter) + r'}$', \
                line)
            read_data = read_data.replace(line, line_new)
            astro_aff_counter += 1
        elif astro_aff_counter and re.search(r'\\and[ ]*$', line):
            line_new = \
                re.sub(r'(.*)[ ]*\\and[ ]*$', r'$^{' + \
                       str(astro_aff_counter) + r'}$ \1', \
                       line)
            read_data = read_data.replace(line, line_new)
            astro_aff_counter += 1
    #print read_data


    #Special treatment for LIGO and Virgo
    pattern_au = re.compile(r"([A-Z])\.([^-]*)([A-Z])([^A-Z]+)\s*\%\s*"
                         r"([a-z])([a-z]+)\.([a-z])([a-z]+)")
    pattern_af = re.compile(r"\\affiliation\s*\{(.*)\}\s*\%.*(\{\d+\})")
    for line in read_data.split('\n'):
        match = re.match(pattern_au, line)
        if match:
            if match.group(5).upper() == match.group(1) and \
               match.group(7).upper() == match.group(3):
                line_new = match.group(1) + match.group(6) + \
                           match.group(2) + match.group(3) + \
                           match.group(4)
                #print line_new, '\t\t', line
                read_data = read_data.replace(line, line_new)
        match = re.match(pattern_af, line)
        if match:
            line_new = "$^" + match.group(2) + "$" + match.group(1)
            #print line_new
            read_data = read_data.replace(line, line_new)

    #Remove spaces around braces and commas
    read_data = re.sub(r'[ ]*([\]\}\[\{\,])[ ]*', r'\1', read_data)
    read_data = re.sub(r'^[ ]+', '', read_data)

    read_data = re.sub(r'\-+', r'-', read_data)

    read_data = re.sub(r'%.*\n', '\n', read_data)
    read_data = re.sub(r'}\$,\s*', '}$\n', read_data)
    read_data = re.sub(r'\$\^(\w)\$,\s*', r'$^\1$\n', read_data)
    read_data = re.sub(r'\}?\\thanks\{[^\}]+\}?', r'', read_data)
    read_data = re.sub(r'\\item\[(\$\^\{?\w+\}?\$)\]', r'\1', read_data)
    read_data = re.sub(r'\\llap\{(\$\S+\$)\}', r'\1 ', read_data)
    read_data = re.sub(r'\\address', r'\\affiliation', read_data)
    read_data = re.sub(r'\\affil\b', r'\\affiliation', read_data)
    read_data = re.sub(r'}\s*\\affiliation', '}\n\\\\affiliation', read_data)
    read_data = re.sub(r'}\s*\\author', '}\n\\\\author', read_data)
    read_data = re.sub(r'[ ]*\\scriptsize[ ]+', '', read_data)
    read_data = re.sub(r'\\and[ ]+', '', read_data)
    read_data = re.sub(r'\$\s*\^', '$^', read_data)


    #I.J.~Arnquist\inst{10}
    read_data = re.sub(r'Irefn{(\w+)}\\Aref{(\w+)}\\Aref{(\w+)}', \
                       r'Irefn{\1,\2,\3}', read_data)
    read_data = re.sub(r'Irefnn?\{(.*)\}\\?A?r?e?f?s?\{(.*)\}', \
                       r'Irefn{\1,\2}', read_data)
    read_data = re.sub(r'Arefs?{(\w+)}', r'Irefn{\1}', read_data)
    #read_data = \
    #    re.sub(r'(\w\.?)[ \,]*\\(inst|altaffilmark|Irefn)\{(.*)\}', \
    #           r'\1$^{\3}$', read_data)
    read_data = \
        re.sub(r'[ \,]*\\(inst|altaffilmark|Irefn|thanksref)\{(.*)\}', \
               r'$^{\2}$', read_data)
    #\altaffiltext{2}{Fermilab, Batavia}
    read_data = \
        re.sub(r'\\altaffiltext\{([\w\,\-]+)\}\{(.*)\}', r'$^{\1}$ \2', \
               read_data)
    read_data = \
        re.sub(r'\\item\s*\\[IA]def\{([\w\,\-]+)\}\{(.*)\}', r'$^{\1}$ \2', \
               read_data)
    read_data = \
        re.sub(r'\\[IA]def\{([\w\,\-]+)\}\{(.*)\}', r'$^{\1}$ \2', \
               read_data)
    read_data = \
        re.sub(r'(.*)\s*\\label\{(.*)\}', r'$^{\2}$ \1', \
               read_data)
    #\author[b,c]{M. Zimmermann} \affiliation[b]{Fermilab}
    read_data = \
        re.sub(r'\\author\[([\w\,\-]+)\]\{(.*)\}', r'\2$^{\1}$', read_data)
    read_data = \
        re.sub(r'\\affiliation\[([\w\,\-]+)\]\{(.*)\}', r'$^{\1}$ \2', \
               read_data)
    #\author{M. Zimmermann$^{b,c}$} \affiliation{$^{b}$Fermilab} remove \author
    read_data = \
        re.sub(r'\\author\{(.*\$\^\{?[\w\,\-]+\}?\$)\}', r'\1', read_data)
    read_data = \
        re.sub(r'\\affiliation\{(\$\^\{?[\w\,\-]+\}?\$.*)\}', r'\1', read_data)

    read_data = re.sub(r'[\, ]+\}', '}', read_data)
    read_data = re.sub(r'[\, ]+\$\^', '$^', read_data)
    #print read_data
    new_read_data = []
    for line in read_data.split('\n'):
        if re.search('abstract', line, re.IGNORECASE) and astro_aff_counter < 1:
            break
        else:
            new_read_data.append(line)

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
            if babar_flag:
                author = re.sub(r'\$\^\{?[abc]+\}\$', '', author)
            author = process_author_name(match.group(1))
            author_dict[author_position] = [author, []]
            author_position += 1
            author_previous = True
        else:
            author_previous = False
        match = re.search(r'\\affiliation\{(.*)\}', line)
        if match and babar_flag:
            author_affiliation = match.group(1)
            author_affiliation = re.sub(r'\$\^\{?[abc]+\}?\$', ' and ', \
                                        author_affiliation)
            for key in author_dict:
                if not author_dict[key][1]:
                    #author_dict[key][1].append(match.group(1))
                    author_dict[key][1].append(author_affiliation)
        elif match:
            try:
                author_dict[author_position - 1][1].append(match.group(1))
            except KeyError:
                #print 'BaBar-style', author_position,  match.group(1)
                pass

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
        if not download_source(eprint):
            return

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_' + eprint + '_correct.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    update = process_file(eprint)
    if update:
        output.write(update)
    output.write('</collection>')
    output.close()
    print filename


    filename = __file__
    filename = filename.replace('.py', '.log')
    log = open(filename, 'a')
    date_time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    date_time_stamp = date_time_stamp + ' ' + eprint + '\n'
    log.write(date_time_stamp)
    log.close()
    print filename


if __name__ == '__main__':

    TEST = False

    try:
        OPTIONS, ARGUMENTS = getopt.gnu_getopt(sys.argv[1:], 't')
    except getopt.error:
        print 'error: you tried to use an unknown option'
        sys.exit(0)

    for option, aargument in OPTIONS:
        if option == '-t':
            TEST = True

    if TEST:
        def get_aff(aff):
            """Does nothing to affiliation."""
            return [aff]
    else:
        from hep_aff import get_aff

    if len(ARGUMENTS) != 1:
        print 'you didn\'t specify an eprint number'
        sys.exit(0)
    else:
        try:
            EPRINT = ARGUMENTS[0]
            main(EPRINT)
        except IndexError:
            print "Bad input", EPRINT
        except KeyboardInterrupt:
            print 'Exiting'

    #EPRINT = sys.argv[1:]
    #try:
    #    #EPRINT = EPRINT[0]
    #    #main(EPRINT)
    #    main(eprint)
    #except IndexError:
    #    print "Bad input", eprint
    #except KeyboardInterrupt:
    #    print 'Exiting'

