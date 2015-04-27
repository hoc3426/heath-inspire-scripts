from invenio.search_engine import perform_request_search
from invenio.search_engine import print_record
import re

SUBFILE = 'HEP'
#SUBFILE = 'HepNames'
SEARCH = '710__g:/[fF]*o[rf] the \w+ collabor/'
SEARCH = '710__g:"Collaboration for the *"'
SEARCH = 'find recid 1215702 or 1216022 or 1216926 or 1255017 or 1264950 or 1273524 or 1273643 or 1273646'
SEARCH = '693__e:FNAL-TEV-*'
SEARCH = '500:/youtube/ -8564_y:youtube'
SEARCH = '"Waseda U., Cosmic Ray Div." phenix "waseda u., rise"'
MARC_FIELD = '710'
MARC_FIELD = '037'
MARC_FIELD = '700'


def main():
    file_name = 'tmp_' + __file__
    file_name = re.sub('.py', '_correct.out', file_name)
    output = open(file_name,'w')
    output.write('<collection>')
    result = perform_request_search(p=SEARCH, cc=SUBFILE)
    result = result[:500]
    for recid in result:
        #info = print_record(recid, ot=['001','037'], format='xm')
        #info = re.sub(r'code="a">FERMILAB', r'code="z">FERMILAB', info)
        info = print_record(recid, ot=['001', MARC_FIELD], format='xm')
        #info = re.sub(r'>.*[fF]*o[rf] the (\w+) [Cc]oll.*<', r'>\1 Collaboration<', info)
        info = re.sub(r'>.* (\S+youtube\S+).*<', r'>\1<', info)
        info = re.sub(r'code="e">FERMILAB-TEV-', r'', info)
        info = re.sub(r'.*Waseda U., Cosmic Ray Div..*', r'', info)
        info += '\n\n'
        output.write(info)
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'


