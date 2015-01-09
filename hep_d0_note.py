from invenio.search_engine import perform_request_search
from invenio.search_engine import print_record
from invenio.search_engine import search_unit

import re

SUBFILE = 'NOTE'
#SUBFILE = 'HepNames'
SEARCH = '980__a:D0-PRELIMINARY-NOTE'
MARC_FIELD = '710'
MARC_FIELD = '037'
MARC_FIELD = "'100', '700'"


def main():
    file_name = 'tmp_' + __file__
    file_name = re.sub('.py', '_correct.out', file_name)
    output = open(file_name,'w')
    output.write('<collection>')
    result_hep = perform_request_search(p=SEARCH, cc=SUBFILE)
    result = search_unit(p="*D0-PRELIMINARY-NOTE*",m='a',f='980*')
    result = result[:5]
    for recid in result:
        #info = print_record(recid, ot=['001','037'], format='xm')
        #info = re.sub(r'code="a">FERMILAB', r'code="z">FERMILAB', info)
        info = print_record(recid, ot=['001', '100', '700', '980'], format='hm')
        #info = re.sub(r'>.*[fF]*o[rf] the (\w+) [Cc]oll.*<', r'>\1 Collaboration<', info)
        #info = re.sub(r'>\w+tion [fF]*or [Tt]he (\w+)<', r'>\1 Collaboration<', info)
        info = re.sub(r'code="e">FERMILAB-TEV-', r'', info)
        info = re.sub(r'<\/?pre[^\>]*>', r'', info)
        info += '\n\n'
        output.write(info)
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'


