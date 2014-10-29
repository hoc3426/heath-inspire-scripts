import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from hep_convert_email_to_id import get_hepnames_recid_from_email

for i in [1, 2, 3]:
  listOfIds = []
  listOfIdsKnownDuplicate = []
  if i == 1:
    field = '035__a'
    search = field + ':INSPIRE-*'
  elif i == 2:
#    emailsearch = '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s'
#    reclist = perform_request_search(p = \
#        emailsearch % (email, email, email, email), cc='HepNames')
    field = '371__m'
    search = field + ':/\@/'
  elif i == 3:
    field = '371__m'
    search = field + ':/\,/'
  x = perform_request_search(p=search,cc='HepNames')
  for r in x:
    if i == 3:
      print 'https://inspirehep.net/record/' + str(r)
    ids = get_fieldvalues(r,field)
    for id in ids:
      search = field + ':' + id
      if i == 2:
        email = id
        emailsearch = '371__m:%s or 371__o:%s or 595__o:%s or 595__m:%s'
        search = emailsearch % (email, email, email, email)
      #if id in listOfIds and not id in listOfIdsKnownDuplicate:
      if not id in listOfIdsKnownDuplicate:
        #print 'Duplicate - ' + search
        #print search
        xx = perform_request_search(p=search,cc='HepNames')
        if len(xx) > 1 :
          #print 'Multiple records -  (' + str(len(xx)) + ') ' + search
          print search
          if i == 1:
            search = '100__i:' + id + ' or 700__i:' + id
            xxx = perform_request_search(p=search,cc='HEP')
            if len(xxx) > 1 :
              print '  Multiple records -  (' + str(len(xxx)) + ') ' + search
          listOfIdsKnownDuplicate.append(id)
      listOfIds.append(id)
 

