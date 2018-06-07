#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field


JOURNAL_PUBLISHED_DICT = {"Ann.Rev.Astron.Astrophys.":"10.1146/annurev-astro",
"Astron.Astrophys.":"10.1051/0004-6361/",
"Astron.J.":"10.1088/0004-6256/",
"Astron.Astrophys.Suppl.Ser.":None,
"Astrophys.J.":"10.1088/0004-637X/",
"Astrophys.J.Suppl.":"10.1088/0067-0049/",
"Europhys.Lett.":"10.1209/0295-5075",
"JHEP":"10.1007/JHEP",
"Mon.Not.Roy.Astron.Soc.":"10.1093/mnras",
"Nature":"10.1038/nature",
"Nature Phys.":"10.1038/nphys",
#"Nucl.Phys.":"10.1016/j.nuclphysb.",
"Phys.Lett.":"10.1016/j.physletb.",
"Phys.Rept.":"10.1016/j.physrep.",
"Phys.Rev.":"10.1103/PhysRevD.",
"Phys.Rev.Lett.":"10.1103/PhysRevLett.",
"Rev.Mod.Phys.":"10.1103/RevModPhys.",
"Sci.Rep.":"10.1038/srep",
"Science":"10.1126/science"}

CONFERENCE_DICT = {"AIP Conf.Proc.":None,
"ASP Conf.Ser.":None,
"EPJ Web Conf.":"10.1051/epjconf",
"J.Phys.Conf.Ser.":"10.1088/1742-6596",
"Int.J.Mod.Phys.Conf.Ser.":None,
"Nucl.Phys.Proc.Suppl.":"10.1016/j.nuclphysbps."
}

def create_xml(recid, type_code):
    record = {}
    record_add_field(record, '001', controlfield_value=str(recid))
    collection = [('a', type_code)]
    record_add_field(record, '980', '', '', subfields=collection)
    return print_rec(record)



def process(paper_type, collection):
    filename = 'tmp_' + re.sub('.py', '', __file__)
    filename += '_' + paper_type + '_' + collection + '_' + '_append.out'
    output = open(filename,'w')
    output.write('<collection>')
    search = ''
    if paper_type == 'pub':
        type_dict = JOURNAL_PUBLISHED_DICT
        type_code = 'Published'
    elif paper_type == 'conf':
        type_dict = CONFERENCE_DICT
        type_code = 'ConferencePaper'
    for key in type_dict:
        search  = '773__p:"' + key +  '" 773__y:1900->3000'
        if type_dict[key]:
            search += ' or doi:"' + type_dict[key] + '*"'
        search += ' -980:Published'
        search += ' -980:ConferencePaper'
        #search += ' -980:Lectures'
        search += ' -980:Proceedings'
        #search += ' -980:Book'
        #search += ' -980:BookChapter'
        #search += ' -980:Introductory'
        search_intro = search + ' 980:Introductory'
        result_intro = perform_request_search(p=search_intro, cc=collection)
        if len(result_intro) > 0:
            search += ' 980:arxiv cited:10->999 -980:Introductory'
        #search += ' -245:/erratum/'
        result = perform_request_search(p=search, cc=collection)
        result = result[:500]
        if len(result):
            for recid in result:
                record_update = create_xml(recid, type_code)
                try:
                    output.write(record_update)
                except:
                    print 'Cannot print:', recid
    output.write('</collection>')
    output.close()


def main():
    for collection in ('HEP', 'Fermilab'):
        for type in ('pub', 'conf'):
            process(type, collection)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'
