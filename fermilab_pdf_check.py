#!/usr/bin/python
#
# TS 12/2015

from invenio.bibdocfile import bibdocfile_url_to_bibdocfile
from invenio.search_engine import get_fieldvalues, perform_request_search


def check_magic():
    """
    search HEP for FERMILABPUB URLs and flag files with '.pdf' extension
    which do not have 'application/pdf' mime-type as determined by magic
    """
    
    count = 0

    for r in perform_request_search(p='8564_y:FERMILABPUB'):
        urls = get_fieldvalues(r, '8564_u')
        for url in urls:
            if url.find('inspirehep.net') >= 0 \
               and url.endswith('.pdf') \
               and (url.find('-pub') >= 0 or
                    url.find('pub-') >= 0):
                count += 1
                bd = bibdocfile_url_to_bibdocfile(url)
                mimetype = bd.get_magic()[-1]
                if mimetype != 'application/pdf':
                    print "%s:\t%s" % (mimetype, url)
    print "total of %d files checked" % count

if __name__ == '__main__':
    check_magic()

