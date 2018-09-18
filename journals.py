import re
import collections
from Counter import Counter
import operator

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
eprints = ['gr-qc','hep-ex','hep-lat','hep-ph','hep-th','nucl-ex','nucl-th']
eprints = ['gr-qc']
for eprint in eprints :
    print eprint
    search = "find primarch " + eprint + " and tc p and (jy 2012 not jy 2011 not jy 2010 not jy 2009 not jy 2008 not jy 2007)"
    search = "035__9:ads - 035__a:/ICRC/"
    search = "773__v:/[0-9]N[0-9]/"
    search = "100__j:ORCID* or 700__j:ORCID*"
    search = "037:fermilab* 773__p:IEEE* (773__y:2011 or 773__y:2012 or 773__y:2013 or 773__y:2014 or 773__y:2015 or 773__y:2016)"
    search = "037:fermilab* 773__y:2016 980:published"
    search = "find exp fnal-e-0741 or exp fnal-e-0775 or exp fnal-e-0830"
    search = "037:/ND/ 980:published 773__y:2018" # authorcount:50+"
    x = perform_request_search(p=search,cc='Fermilab')
    journals = []
    for r in x :    
      try:
          #v = str(get_fieldvalues(r,'773__p')[0]) + str(get_fieldvalues(r,'773__v')[0])
          v = str(get_fieldvalues(r,'773__p')[0])
          v = re.sub(r"\d", "", v)
          journals.append(v)
      except:
          pass
    journals.sort()
    counted_all_refs=Counter(journals)
    sorted_count = sorted(counted_all_refs.items(), key=operator.itemgetter(1))
    total = 0
    for recid_count, count in sorted_count:
        url = "http://inspirehep.net/search?p=773__p:\"" + recid_count 
        url = url + "\" (" + search + ")"
        url = re.sub(' ', '+', url)
        total += count
        #print '%-25s %3d' % (recid_count, count)
        #print '%s\t\t\t%3d' % (recid_count, count)
        print('{0:30s} {1:3d}'.format(recid_count, count))

quit()
#c = Counter(journals)
#l = list(set(journals))
#for letter in c:
#    print '%s : %d' % (letter, c[letter])
