""" Script to take in list of authors and their internal ID numbers.
    It outputs our records on the people if they are tagged with the
    collaboration in HEPNames.
"""

import re

from invenio.bibrecord import print_rec, record_add_field
from invenio.search_engine import get_fieldvalues
from hep_collaboration_authors import process_author_name, author_first_last
from hep_convert_experiment_to_id import get_hepnames_recid_from_search
from hep_convert_email_to_id import get_hepnames_aff_from_recid, \
                                    get_hepnames_anyid_from_recid


FILE_NAME = 'belle2-author-template.tex'
EXPERIMENT = 'KEK-BF-BELLE-II'

def create_xml(recid, experiment_id):
    "Create xml to append to INSPIRE record."

    record = {}
    tag_dict = {}
    tag = '035__'
    record_add_field(record, '001', controlfield_value=str(recid))
    tag_dict[tag] = [('9', EXPERIMENT), ('a', experiment_id)]
    record_add_field(record, tag[0:3], tag[3], tag[4], \
                     subfields=tag_dict['035__'])
    return print_rec(record)


def process_line(author, aff, experiment_id):
    """Process each line of the author file to check INSPIRE
       for the authors.
    """

    author = author_first_last(process_author_name(author))
    search = 'find a ' + author + ' and exp ' + EXPERIMENT
    recid = get_hepnames_recid_from_search(search)
    if recid:
        #print create_xml(recid, experiment, experiment_id)
        inspire_aff = get_hepnames_aff_from_recid(recid, 'current')
        inspire_author = get_fieldvalues(recid, '100__a')[0]
        inspire_id = get_hepnames_anyid_from_recid(recid, 'INSPIRE')
        orcid = get_hepnames_anyid_from_recid(recid, 'ORCID')
        return "{0}\t{1}\t{2}\t||\t{3}\t{4}\t{5}\t{6}\n".format(
               author, aff, experiment_id, inspire_author, inspire_aff,
               inspire_id, orcid)
    else:
        return "{0}\t{1}\t{2}\n".format(author, aff, experiment_id)

def main():
    "Run through file."

    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_out.txt', filename)
    output = open(filename, 'w')

    for line in open(FILE_NAME, 'r').readlines():
        match_obj = \
        re.match(r'.*\\author{([^\}]+)}.*inst(\w+).*\% (\d+)', line)
        if match_obj:
            author = match_obj.group(1)
            aff = match_obj.group(2)
            experiment_id = match_obj.group(3)
            output.write(process_line(author, aff, experiment_id))
    output.close()
    print filename


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
