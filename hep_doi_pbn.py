import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

VERBOSE = 0

def yearCalc(journal,volume):
  year = 9999 
  if re.search("^[A-E]", volume):
    number = int(re.sub(r'[A-E]',r'',volume))
    if number%2==0:
      year = number/2 - 1 + 1970
    else:
      year = number/2 - 1/2 + 1970
  elif re.search("^[X]", volume):
    number = int(re.sub(r'X',r'',volume))
    year = number + 2010
  elif journal == "Phys.Rev.Lett.":
    number = int(volume)
    if number == 1:
      year = 1958
    elif number%2==0:
      year = number/2 - 1 + 1959
    else:
      year = number/2 - 3/2 + 1959
  elif journal == "Phys.Rev.ST Accel.Beams":
    year = int(volume) + 1997
  elif journal == "Phys.Rev.ST Phys.Educ.Res.":
    year = int(volume) + 2004
  elif journal == "Rev.Mod.Phys.":
    year = int(volume) + 1928
  return year

print "<?xml version=\"1.0\" ?>"
print "<collection>"

searches = ['0247_a:/PhysRev.*/ -773__p:/Phys.Rev./',
            '0247_a:/PhysRev.*/ -773__c:/[0-9]/',
            '0247_a:/PhysRev.*/ -773__y:/[0-9]{4}/',
            '0247_a:/RevModPhys.*/ -773__p:/Rev.Mod.Phys./',
            '0247_a:/RevModPhys.*/ -773__c:/[0-9]/',
            '0247_a:/RevModPhys.*/ -773__y:/[0-9]{4}/'
]


for search in searches:
  x = perform_request_search(p=search,cc='HEP')
  x = x[:200]
  for r in x:   
    if VERBOSE:
      print r
    doi = get_fieldvalues(r,'0247_a')[0]
    pbn = get_fieldvalues(r,'773__p')
    [publisher,jvp] = re.split('/',doi)
    [journal,volume,page] = re.split('\.',jvp)
    volumeNumber = int(volume)
    if journal == 'PhysRevSTAB' : journal = 'Phys.Rev.ST Accel.Beams'
    elif journal == 'PhysRevSTPER' : journal = 'Phys.Rev.ST Phys.Educ.Res.'
    elif journal == 'RevModPhys' : journal = 'Rev.Mod.Phys.'
    else :
      matchObj = re.search("[A-EX]$", journal)
      if matchObj :
        volume =  matchObj.group() + volume
        journal = re.sub(r'[A-EX]$',r'',journal)
      journal = journal + "."
      journal = re.sub(r'([a-z])([A-Z])',r'\1.\2',journal)
    year = str(yearCalc(journal,volume))
    #matchObj = re.search("\d\d\d\d", date)
    #year = matchObj.group()
    #year = '2013'
    print '<record>'
    print '  <controlfield tag="001">'+str(r)+'</controlfield>'
    print '  <datafield tag="773" ind1=" " ind2=" ">'
    print '    <subfield code="p">' + journal + '</subfield>'
    print '    <subfield code="v">' + volume + '</subfield>'
    print '    <subfield code="c">' + page + '</subfield>'
    print '    <subfield code="y">' + year + '</subfield>'
    print '  </datafield>'
    #print '  <datafield tag="260" ind1=" " ind2=" ">'
    #print '    <subfield code="c">' + date + '</subfield>'
    #print '  </datafield>'
    #print '  <datafield tag="980" ind1=" " ind2=" ">'
    #print '    <subfield code="a">Published</subfield>'
    #print '  </datafield>'
    print '</record>'

print "</collection>"

