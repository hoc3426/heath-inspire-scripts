"""
A system to extract collaboration author lists from tex files.
"""

import gzip
import os
import re
import sys
import tarfile
import urllib

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
        else:
            output = open(filename + ".tex", 'w')
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

if __name__ == '__main__':
    EPRINT = sys.argv[1:]
    try:
        EPRINT = EPRINT[0]
        download_source(EPRINT)
    except IndexError:
        print "Bad input", EPRINT
    except KeyboardInterrupt:
        print 'Exiting'

