from invenio.search_engine import perform_request_search
from invenio.search_engine import print_record
import re

def main():
    file_name = 'tmp_' + __file__
    file_name = re.sub('.py', '_correct.out', file_name)
    output = open(file_name,'w')
    output.write('<collection>')
    search = '693__e:cern-lhc-cms authorcount:2000+ 037__a:fermilab*'
    search = '980__a:D0-PRELIMINARY-NOTE 980__a:HEP'
    search = '001:1117275'
    result = perform_request_search(p=search, cc='HEP')
    result = result[:500]
    for recid in result:
        #info = print_record(r, ot=['001','037'], format='xm')
        #info = re.sub(r'code="a">FERMILAB', r'code="z">FERMILAB', info)
        try:
            #info = print_record(recid, ot=['001'], format='xm')
            info = print_record(recid, ot=['001','037'], format='xm')
            #info = print_record(recid)
            print info
            #info = re.sub(r'code="a">HEP<', r'code="a">NOTE<', info)
            #output.write(info)
        except:
            print 'problem with', recid
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'


