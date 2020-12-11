#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import unicodedata
#import re
#import operator
#import os
#import pprint
#import string
#from datetime import date
#import sys
#from check_url import checkURL

#from invenio.search_engine import perform_request_search
#from invenio.search_engine import get_fieldvalues
#from invenio.search_engine import get_record
#from invenio.search_engine import get_all_field_values
#from invenio.search_engine import print_record
#from invenio.bibformat_engine import BibFormatObject
#from hep_convert_email_to_id import *
#from invenio.bibrecord import print_rec, record_get_field_instances, \
#     record_add_field
#from invenio.intbitset import intbitset
from invenio.textutils import translate_latex2unicode
##from invenio.search_engine import search_unit
#from invenio.search_engine import get_collection_reclist

#from hep_convert_email_to_id import get_hepnames_anyid_from_recid, \
#                                    get_hepnames_recid_from_email, \
#                                    bad_orcid_check
#from hep_collaboration_authors import author_first_last
#from osti_web_service import get_osti_id
#from hep_msnet import create_xml
#from osti_web_service import check_already_sent
#from datetime import datetime

def primarch():
    from invenio.search_engine import perform_request_search
  
    primarch = 'quant-ph'
    for year in range(1995, 2020):
        search = 'find primarch {0} and de {1}'.format(primarch, year)   
        result = perform_request_search(p=search, cc='HEP')
        print '{0:12s} {1:6d}'.format(str(year), len(result))

def author_count():
    from invenio.search_engine import perform_request_search

    for count in range(1, 10):
        search = 'find primarch hep-lat and ac ' + str(count)
        result = perform_request_search(p=search, cc='HEP')
        print '{0:12s} {1:6d}'.format(str(count), len(result))
    z = [(count, mag) for mag in range(1, 4) for count in range(1, 10)]
    for count, mag in z:
        count = '{0}{1}->{0}{2}'.format(str(count), '0'*mag, '9'*mag)
        search = 'find primarch hep-lat and ac ' + count
        result = perform_request_search(p=search, cc='HEP')
        print '{0:12s} {1:6d}'.format(count, len(result))

def latex_check(input):

    for math in (r'_', r'^', r'\\'):
        if math in input and not r"$" in input:
            return input 
    for symbol in (r'&', r'#', r'%'):
        slash_symbol = '\\' + symbol
        if symbol in input and not slash_symbol in input:
            return input
    if input.count('$') % 2 != 0:
            return input
    return None    


def tex_title(title):

    title = re.sub(r'\b(\S+[_^]\S+)\b', r'$\1$', title)
    title = title.replace('$ x $', ' \times ')
    return title

def check_titles(search):

    from invenio.search_engine import perform_request_search, get_fieldvalues
    LIMIT = 100
    result = perform_request_search(p=search, cc='HEP')
    print search
    print 'Checking {0} records'.format(len(result))
    icount = 0
    for iteration, recid in enumerate(result):
        if icount > LIMIT:
            break
        try:
            title = get_fieldvalues(recid, '245__a')[0]
        except IndexError:
            print 'PROBLEM with title', get_fieldvalues(recid, '245__a')
            print 'https://old.inspirehep.net/record/{0}'.format(recid)
            return
        check = latex_check(title)
        if check:
            print 'https://inspirehep.net/record/{0}'.format(recid)
            print '   ', check
            #print '   ', tex_title(check)
            icount += 1
    print '{0} out of {1} records checked'.format(icount, iteration)

def add_date():

    import re
    from invenio.search_engine import get_fieldvalues,\
                                      perform_request_search

    search = '037:/\-20[012][0-9]/ -date:1000->3000 -980:thesis'
    search = '037:/\-[789][0-9]\-/ -date:1000->3000 -980:thesis'
    search = '773__w:c* -date:1000->3000 -269__c:1000->3000'
    #print search
    result = perform_request_search(p=search, cc='HEP')
    #print len(result)
    for recid in result[:500]:
        #for report in get_fieldvalues(recid, '037__a'):
        for report in get_fieldvalues(recid, '773__w'):
            year = re.search(r'\d{4}', report)
            year = re.search(r'\-[789][0-9]\-', report)
            year = re.search(r'\-[12][0-9]\-', report)
            year = re.search(r'C\d\d\-', report)
            if year:
                year = year.group(0)
                year = re.sub(r'-', '', year)
                year = re.sub(r'C', '', year)
                if year.startswith('0'):
                    year = '20' + year
                elif int(year) > 30:
                    year = '19' + year
                else:
                    year = '20' + year
                #print report
                print create_xml(recid, '269__', 'c', year)


def get_orcids(filename):
    #<cal:authorid source="Inspire ID">INSPIRE-00043063</cal:authorid>
    #<cal:orgName>Yerevan Physics Institute</cal:orgName>

    from hep_aff import get_aff
    from hep_convert_email_to_id import get_orcid_from_inspire_id
    with open(filename) as input: # Use file to refer to the file object
        lines = input.readlines()
    address = icn = None
    for line in lines:
        #print line
        inspire = re.search(r'INSPIRE\-\d{8}', line)
        if inspire and False:
            inspire = inspire.group(0)
            orcid = get_orcid_from_inspire_id(inspire)[1]
            if orcid:
                print line.replace('Inspire ID', 'ORCID').replace(inspire, orcid)
        if not address:
            address = re.search(r'<cal:orgName>([^\<]+)', line)
            #print 'address', address
        if not icn:
            icn = re.search(r'orgName source="INSPIRE">([^\<]+)', line)
        if address and False:
            address = address.group(1)
            icn = get_aff(address)
            try:
                #print '            <cal:orgName source="INSPIRE">{0}</cal:orgName>'.format(icn[0])
                print '{0} = {1}'.format(address, icn)
            except IndexError:
                print '\n Problem with: {0}\n'.format(address)
        if address and icn:
            print '"{0}" = "{1}"'.format(address.group(1), icn.group(1))
            address = icn = None
        #line = line.replace(r'\n', '')
        #print line



def papers_per_year(search, start, end, collection='HEP'):
    print collection
    for year in range(start, end):
        searchy = search + ' and jy ' + str(year)
        number = len(perform_request_search(p=searchy, cc=collection))
        print year, number


def bad_url(url):
    curl = 'curl --output /dev/null --silent --head --fail '
    if os.system(curl + url) != 0:
        return True
    return False

def check_bibcodes(file_name):

    URL = 'https://ui.adsabs.harvard.edu/abs/'
    ADS_REGEX = re.compile(r"\d{4}([a-z&]+)[\d.]+[a-z.\d]+",
                           re.IGNORECASE)
    with open(file_name) as input: # Use file to refer to the file object
        lines = input.readlines()
    for line in lines:
        try:
            bibcode = re.search(ADS_REGEX, line).group()
        except AttributeError:
            continue
        url = URL + bibcode
        if bad_url(url):
            continue
        print line

import requests
def new_url(line):

    headers = headers = {'user-agent': 'heath'}
    new_url = None
    url_search = re.search(r'(https?://.*linkedin.com/pub/.*)/?\$\$yLINKEDIN', line)
    if not url_search:
        return None
    url = url_search.group(1)
    req = requests.get(url, allow_redirects=False, headers=headers)
    new_url = req.headers.get('Location')
    print 'url     = ', url
    print 'new_url = ', new_url
    new_line = line.replace(url, new_url)
    return new_line


def cleanup(search, tag, cc='HEP', old='', new=''):
    import re
    from invenio.search_engine import perform_request_search, print_record

    pre_open = '<pre style="margin: 1em 0px;">'
    pre_close = '</pre>'
    if old and new:
        old = re.compile(old, re.I)
    print search
    result = perform_request_search(p=search, cc=cc)
    print len(result)
    for recid in result:
       try:
           if recid in RECIDS:
               print 'Already done', recid
               continue
           RECIDS.add(recid)
       except NameError:
           pass
       output = print_record(recid, ot=tag, format='hm')
       output = output.replace(pre_open, '')
       output = output.replace(pre_close, '')
       output = re.sub(r'.*Brief [Ee]ntry.*\n', '', output)
       output = re.sub(r'.*Temporary [Ee]ntry.*\n', '', output)
       #output = re.sub(r'\n', '', output)
       output = re.sub(r'^(\d)', r'\n\1', output)

       print output
       if new in output:
           output = re.sub(old, '', output)
       elif old.search(output):
           output = re.sub(old, new, output)
       #print 'NEW', output
       
       #if new_output:
       #    print new_output


def create_xml(recid, tag, subfield, value):
    from invenio.bibrecord import print_rec, record_add_field

    common_fields = {}
    common_tags = {}
    record_add_field(common_fields, '001', controlfield_value=str(recid))
    common_tags[tag] = [(subfield, value)]
    record_add_field(common_fields, tag[0:3], tag[3], tag[4],\
                     subfields=common_tags[tag])
    return print_rec(common_fields)



def create_xml_old(recid, urls=None, delete=False):
    common_fields = {}
    common_tags = {}
    record_add_field(common_fields, '001', controlfield_value=str(recid))
    if urls:
        tag = '8564_'
        for url in urls:
            #url = 'https://lss.fnal.gov/archive/openaccess/' + url
            common_tags[tag] = [('u', url), ('y', 'Open Access fulltext')]
            record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
                subfields=common_tags[tag])
    if delete:
        for (tag, subfield, value) in [('100__', 'a', 'Smith, John Q.'),
                                       ('980__', 'a', 'HepNames'),
                                       ('980__', 'c', 'DELETED')]:
            common_tags[tag] = [(subfield, value)]
            record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
                subfields=common_tags[tag])
    return print_rec(common_fields)



def counter_list(journals):
    from Counter import Counter
    import operator
    journals.sort()
    counted_all_refs=Counter(journals)
    sorted_count = sorted(counted_all_refs.items(),
                          key=operator.itemgetter(1), reverse=True)
    i = 1
    for recid_count, count in sorted_count:
        print('{2:3d} {0:30s} {1:3d}'.format(recid_count, count, i))
        i += 1


def url_accepted(recid):
    
    accepted = None
    url = None
    for item in BibFormatObject(int(recid)).fields('8564_'):
        if item.has_key('y'):
            if item['y'] in ['Article from SCOAP3',
                             'Fulltext from Publisher',
                             'Fulltext from publisher']:
                return None
        if item.has_key('z'):
            if item['z'] == 'openaccess':
                url = item['u']
                accepted = 'openaccess'
            elif item['z'] == 'postprint':
                url = item['u']
                accepted = 'postprint'
    if not url:
        return None
    if 'inspirehep' in url:
        url = url.replace('inspirehep', 'old.inspirehep')
        url = url.replace('old.old.', 'old.')
        url = url.replace('http', 'https')
        url = url.replace('httpss', 'https')
        return url
    return None

def fermilab_accepted():

    from osti_web_service import get_url
    search = '8564_z:postprint or 8564_z:openaccess'
    result = perform_request_search(p=search, cc='Fermilab')
    counter = 0
    pdfs = set()
    for recid in result:
        output = ''
        url = url_accepted(recid)
        if url:
            pdf = re.sub(r'.*\/([^\/]+)', r'\1', url)
            if pdf in pdfs:
                output = ' -O ' + str(recid) + '.pdf'
                pdf = str(recid) + '.pdf'
            #print 'wget{0} "{1}"'.format(output, url)
            #print '{0} https://lss.fnal.gov/archive/openaccess/{1}'.format(recid, pdf)
            url = 'https://lss.fnal.gov/archive/openaccess/' + pdf
            print create_xml(recid, urls=[url])
            counter += 1
            pdfs.add(pdf)
            #if counter % 25 == 0:
            #    print counter
    print counter



def experiment_papers():

    search = 'find primarch hep-ex and jy 2019 and tc p'
    result = perform_request_search(p=search, cc='HEP')
    experiments = []
    for recid in result:
        try:
            experiments.append(get_fieldvalues(recid, '693__e')[0])
        except IndexError:
            pass
    counter_list(experiments)

    


def get_grid():
    from dune_affiliation_translations import DICT
    NEW_DICT = {}
    for dune_aff, inspire_affs in DICT.items():
        inspire_affs_dict = {}
        for inspire_aff in inspire_affs:
            search = '110__u:"{0}"'.format(inspire_aff)
            result = perform_request_search(p=search, cc='Institutions')
            if len(result) != 1:
                print search
                break
            fields = get_fieldvalues(result[0], '035__a')
            inspire_affs_dict[inspire_aff] = {}
            for field in fields:
                if field.startswith('grid'):
                    inspire_affs_dict[inspire_aff]['grid'] = field
                if field.startswith('https://ror.org'):
                    inspire_affs_dict[inspire_aff]['ror'] = field
            if len(inspire_affs_dict[inspire_aff]) < 2:
                print dune_aff, inspire_affs
                print '    https://inspirehep.net/record/{0}'.format(result[0])
                break
        NEW_DICT[dune_aff] = inspire_affs_dict
    pp = pprint.PrettyPrinter()
    pp.pprint(NEW_DICT)
    #print NEW_DICT
    

def twitter():
    search="8564_u:/twitter/"
    result = perform_request_search(p=search, cc='Conferences')
    print len(result)

def count_by_year(search):
    for year in range(1980, 2021):
        searcht = search + ' earliestdate:' + str(year)
        result = perform_request_search(p=searcht, cc='HEP')
        print year, len(result)


def get_recids(eprints):
    print len(eprints)
    for r in eprints:
        search = 'doi:' + r
        s = perform_request_search(p=search,cc='HEP')
        if s:
          print 'or {0}'.format(s[0])
        else:
          print search


def delete_records(search=None, collection=None, result=None):
    if search and collection:
        result = perform_request_search(p=search, cc=collection)
    for recid in result:
        print create_xml(recid, delete=True)



def json_read(file):
    import json
    with open(file) as json_file:
        data = json.load(json_file)
    print len(data)
    i = 1
    j = 1
    output = open('tmp_rivet_%d.out' % j, 'w')
    for key, value in data.iteritems():
        search = '001:{0} 8564_y:"Rivet analyses reference"'.format(key)
        if perform_request_search(p=search, cc='HEP'):
            continue
        #print key, value
        if i == 100:
            i = 1
            output.close()
            output = open('tmp_rivet_%d.out' % j, 'w')
            j += 1
        output.write(create_xml(key, value))
        i += 1
    output.close()



def doi_ending():
    dois = []
    for doi in get_all_field_values('0247_a'):
        if not doi:
            continue
        #dois.append(doi[-1:])
        if not re.match('\w', doi[-1:]):
            search = '0247_a:"{0}"'.format(doi)
            result = perform_request_search(p=search, cc='HEP')
            if result:
                print result, search
    #counter_list(dois)
        
def record_fix(search):
    for recid in perform_request_search(p=search, cc='HEP'):
        rec = print_record(recid, ot=['100', '700'], format='hm')
        rec = rec.replace('<pre style="margin: 1em 0px;">', '')
        rec = rec.replace('</pre>', '')
        print rec
#record_fix('700__u:/ U$/ or 100__u:/ U$/')


def cites_per_year(key, value, start='1970', end='2020'):

    from invenio.bibrank_citation_searcher import get_citation_dict
    citation_dict = get_citation_dict('citationdict')

    search = 'find {0} {1} and topcite 1+'.format(key, value)
    entity_papers = intbitset(perform_request_search(p=search, cc='HEP'))
    print 'The {0} papers of {1}'.format(len(entity_papers), value)

    all_papers = {}
    years = range(start, end)
    for year in years:
        search = 'earliestdate:' + str(year)
        all_papers[year] = intbitset(perform_request_search(p=search,
                                                          cc='HEP'))
    citations_year = {}
    total = 0
    for year in years:
        citations_year[year] = 0
        for entity_paper in entity_papers:
            citations_year[year] += len(citation_dict[entity_paper] &
                                      all_papers[year])
        total += citations_year[year]
        print '{0:6d} {1:6d} {2:6d}'.format(year, citations_year[year], total)
    #cites_per_year('ea', 't.c.brooks.1', start='1970', end='2020')



def authors():
  with open('tmp_1.out') as fp:
    dict_1 = {}
    counter = 0
    for line in fp.readlines():
      dict_1[counter] = line
      counter += 1
  COUNTER_MAX = counter
  with open('tmp_2.out') as fp:
    dict_2 = {}
    counter = 0
    for line in fp.readlines():
      dict_2[counter] = line
      counter += 1
  for counter in range(1, COUNTER_MAX):
    if dict_1[counter] != dict_2[counter]:
      print dict_1[counter][:40]
      print dict_2[counter][:40]
      print ' '


def experiment_notes():
  EXPERIMENT = 'FNAL-E-0974'
  COLLABORATION = 'MicroBooNE'
  FILE = 'tmp_microboone.in'
  URL_BASE = 'https://microboone.fnal.gov/wp-content/uploads/'
  REGEX = re.compile(r'^(\S+)\s+(\S+)\s+(.*)')
  COLLECTIONS = ['HEP', 'CORE', 'NOTE', 'Fermilab']

  EXPERIMENT = 'FNAL-E-0973'
  COLLABORATION = 'Mu2e'
  FILE = 'tmp_mu2e.in'
  URL_BASE = 'https://mu2e-docdb.fnal.gov/cgi-bin/sso/ShowDocument?docid='
  REGEX = re.compile(r'^([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+')
  DATE_REGEX = '%d-%b-%y'
  COLLECTIONS = ['Fermilab']
  #Date	Speaker	Home Institution	Venue	Title	Length (min)	Type		Doc-db (pwd)	Doc-db(cert)	Conference Web page

  AFF_DICT = {
'ANL':'Argonne',
'Berkeley':'UC, Berkeley',
'Caltech':'Caltech',
'FNAL':'Fermilab',
'Frascati':'Frascati',
'HZDR':'HZDR, Dresden',
'LBNL':'LBL, Berkeley',
'LNF':'Frascati',
'Manchester':'Manchester U.',
'Minn':'Minnesota U.',
'Pisa':'Pisa U.',
'Purdue':'Purdue U.',
'SouthAlabama':'South Alabama U.',
'SunYatSen':'SYSU, Guangzhou',
'Uminn':'Minnesota U.',
'UMN':'Minnesota U.',
'UVA':'Virginia U.',
'Yale':'Yale U.',
'York':'York Coll., N.Y.'
}

  with open(FILE) as fp:
    for line in fp.readlines():
        common_fields = {}
        common_tags = {}
        match_obj = REGEX.search(line)
        try:
            date = match_obj.group(1)
        except AttributeError:
            break
        #print date
        try:
            date = datetime.strptime(date, DATE_REGEX).strftime('%Y-%m-%d')
        except ValueError:
            continue
        report = match_obj.group(2)
        freport = 'FERMILAB-' + report
        author = match_obj.group(2) + ', ' + match_obj.group(3)
        affiliation = match_obj.group(4)
        title = match_obj.group(6)
        url = match_obj.group(10)
        if not url.isdigit():
            url = match_obj.group(9)
        if not url.isdigit():
            url = None
        if url:
            url = URL_BASE + url
        #url += report + '.pdf'
        #common_tags['037__'] = [('a', report), ('z', freport)]
        try:
            affiliation = AFF_DICT[affiliation]
            common_tags['100__'] = [('a', author), ('u', affiliation)]
        except KeyError:
            common_tags['100__'] = [('a', author), ('v', affiliation)]
        common_tags['245__'] = [('a', title)]
        common_tags['269__'] = [('c', date)]     
        common_tags['65017'] = [('2', 'INSPIRE'), ('a', 'Instrumentation'),
                                ('a', 'Experiment-HEP')]
        common_tags['693__'] = [('e', EXPERIMENT)]
        common_tags['710__'] = [('g', COLLABORATION)]
        if url:
            url_text = COLLABORATION + ' Server'
            common_tags['8564_'] = [('u', url), ('y', url_text)]
            url = url.replace('ShowDocument', 'RetrieveFile')
            #common_tags['FFT__'] = [('a', url), ('f', 'pdf'),
            #                        ('n', match_obj.group(2)),
            #                        ('t', 'INSPIRE-PUBLIC')]
            common_tags['FFT__'] = [('a', url),
                                    ('n', match_obj.group(2)),
                                    ('t', 'INSPIRE-PUBLIC')]
        for tag in common_tags:
            record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
                subfields=common_tags[tag])
        tag = '980__'
        for collection in COLLECTIONS:
            common_tags[tag] = [('a', collection)]
            record_add_field(common_fields, tag[0:3], tag[3], tag[4], 
                         subfields=common_tags[tag])

        print print_rec(common_fields)
        #print "wget {0}".format(url)


def bad_aff():
    x=get_all_field_values('110__t')
    baddies = []
    for d in x:
       if 'hys' in d and 'ept' in d:
         result = \
         perform_request_search(p='110__t:"' + d + '"', cc='Institutions')
         if len(result):
             baddies.append(d)
    baddies.sort()
    for ab in baddies:
        print ab


def citation_primarch(recid):
  total = 3641
  for primarch in ['cond-mat*', 
                   'gr-qc', 'hep-ex', 'hep-lat', 'hep-lat',
                   'hep-th', 'math-ph', 'math*', 'nucl-ex', 'nucl-th',
                   'quant-ph',
'astro-ph or 037__c:astro-ph.he or 037__c:astro-ph.co or 037__c:astro-ph.GA \
or 037__c:astro-ph.EP or 037__c:astro-ph.IM or 037__c:astro-ph.sr']:
    search = '037__c:' + primarch
    search += ' refersto:recid:' + str(recid)
    number = len(perform_request_search(p=search, cc='HEP'))
    if 'astro' in primarch:
        primarch = 'astro-ph'
    primarch = primarch.replace('*', '')
    print "{0:10} {1:5d} {2:4f}".format(primarch, number, float(number)/float(total)*100)
    #total += number
  print 'Total citations:', total



def accepted_sent_check():
    ACCEPTED_SEARCH='8564_z:openaccess or 8564_z:postprint or \
8564_y:"article from scoap3" or \
8564_y:"Fulltext from Publisher" 0247_2:doi 035__9:osti'
    print ACCEPTED_SEARCH
    result = perform_request_search(p=ACCEPTED_SEARCH,cc='Fermilab')
    #print result
    print len(result)
    for recid in result:
        if not check_already_sent(recid):
            print 'or recid {0} \\'.format(recid)
        

def conference_papers():
    search = 'find primarch hep-ph or hep-ex and tc '
    for year in range(2000, 2020):
        search_c = search + ' c and date ' + str(year)
        search_p = search + ' p and date ' + str(year)
        result_c = len(perform_request_search(p=search_c, cc='HEP'))
        result_p = len(perform_request_search(p=search_p, cc='HEP'))

        print "{0}\t{1}\t{2}".format(year, result_p, result_c)



def create_grid_dict():
    grid_dict = {}
    search = '035__9:grid'
    result = perform_request_search(p=search, cc='Institutions')
    for recid in result:
        affiliations = get_fieldvalues(recid, '110__u')
        affiliations += get_fieldvalues(recid, '110__t')
        for affiliation in affiliations:
            grid = get_hepnames_anyid_from_recid(recid, 'GRID')
            if grid:
                grid_dict[affiliation] = grid
    for key in grid_dict:
        print key, grid_dict[key]
    import cPickle as pickle
    DIRECTORY = ''
    AFFILIATIONS_GRID_FILE = 'authorlist_institutions_grid.p'
    AFFILIATIONS_GRID_FILE = DIRECTORY + AFFILIATIONS_GRID_FILE
    pickle.dump(grid_dict, open(AFFILIATIONS_GRID_FILE, "wb"))
    print 'Institutions now in', AFFILIATIONS_GRID_FILE, len(grid_dict)




def fermilab_tm():
    for year in range(1968, 2020):
        search = '999C5r:fermilab-tm-' + str(year) + \
                 '* and du:2019-05-15->2019-05-19'
        result_c = perform_request_search(p=search, cc='HEP')
        if len(result_c) == 0:
            continue
        search = 'find r fermilab-tm-' + str(year) + '*'
        result = perform_request_search(p=search, cc='HEP')
        print year, result[0], get_fieldvalues(result[0], '245__a')[0][:70]
        for recid in result_c:
            print '  ', recid, get_fieldvalues(recid, '245__a')[0][:70]



def topcites_by_year():
    for year in range(1960, 2020):
        search = 'find topcite 2000+ not t rpp and de ' + str(year)
        result = perform_request_search(p=search, cc='HEP')
        print year, len(result)



def bad_eprint():
    search = '037__9:arxiv -035__9:arxiv'
    for recid in perform_request_search(p=search, cc='HEP'):
    #for recid in [199609]:
        x = print_record(recid, ot=['037'], format='hm')
        #print x + '\n'
        x = re.sub(r'\n', '', x)
        #print x + '\n'
        x = re.sub(r'.*>(.*)<.*', r'\1', x)
        #print x + '\n'
        x = re.sub(r'(^\d+) .*037__ \$\$9arXiv\$\$a([^\$]+).*', 
                   r'\1 035__ $$9arXiv$$aoai:arXiv.org:\2', x)
        x = x.replace('arXiv.org:arXiv', 'arXiv.org')
        #print x + '\n'
        print x


def fermilab_experiments():
    SEARCH = "119__a:/^FNAL/ or 119__c:/^FNAL/ or \
    419__a:/^FNAL/ or 119__u:Fermilab"
    SEARCH += ' -980:ACCELERATOR'
    search=SEARCH
    result = perform_request_search(p=search, cc='Experiments')
    for recid in result:
        exp = get_fieldvalues(recid, '119__a')[0]
        try:
            url = get_fieldvalues(recid, '8564_u')[0]
        except IndexError:
            url = None
        print "{0}\t{1}".format(exp, url)


def fermilab_orcid():
    hidden_m = search_unit('*@fnal.gov', f='595__m', m='a')
    #print 'hiddenm', len(hidden_m)
    hidden_o = search_unit('*@fnal.gov', f='595__o', m='a')
    #print 'hiddeno', len(hidden_o)
    search = '371:/fnal.gov$/'
    result = intbitset(perform_request_search(p=search, cc='HepNames'))
    #print '371', len(result)
    result = hidden_m | hidden_o | result
    search = '693__e:FNAL* or 693__e:DUNE'
    result_e = intbitset(perform_request_search(p=search, cc='HepNames'))
    result = result_e | result
    #print 'result mor', len(result)
    search = '035__9:orcid'
    result = result & intbitset(perform_request_search(p=search, cc='HepNames'))
    print 'result orcid', len(result)

    #search = '035__9:inspire 035__9:orcid 693__e:fnal-e-973'
    # search = '693__e:fnal-e-0973'
    # result = perform_request_search(p=search, cc='HepNames')
    for recid in result:
        orcid = inspire = current_email = None
        orcid = get_hepnames_anyid_from_recid(recid, 'ORCID')
        if bad_orcid_check(orcid):
            print 'Bad orcid:', orcid
            continue
        inspire = get_hepnames_anyid_from_recid(recid, 'INSPIRE')
        author = get_fieldvalues(recid, '100__a')[0]
        email_fnal = None
        try:
            email_current = get_fieldvalues(recid, '371__m')[0]
        except:
            email_current = None
        emails = get_fieldvalues(recid, '371__m') + \
                 get_fieldvalues(recid, '371__o') + \
                 get_fieldvalues(recid, '595__m') + \
                 get_fieldvalues(recid, '595__o')
        for email in emails:
            if re.search(r'fnal.gov', email, re.IGNORECASE):
                x = get_hepnames_recid_from_email(email)
                if x != recid:
                    print "CHECK THIS", recid, email, x
                else:
                    email_fnal = email
                    break
        if email_fnal:
            email_current = email_fnal
        print '\"{0}\",{1},{2},{3},{4}'.format(author, inspire, orcid, 
                                           email_current, recid)



def convert_zenodo_url_to_doi():
    #https://zenodo.org/record/3257749#.XSzbl8hKhPY
    zenodo_url_regex = re.compile(r'\$\$uhttps://zenodo.org/record/(\d+)(#\.[A-z0-9]+)?')
    zenodo_doi_url_regex = re.compile(r'https://doi.org/\s*10.5281/\s*zenodo.(\d+)')
    zenodo_doi_regex = re.compile(r'\$\$adoi:10.5281/zenodo\.\d+')
    search = '999C5u:"https://zenodo.org/record/*"'
    lines = ''
    for recid in perform_request_search(p=search, cc='HEP'):
        lines += print_record(recid, ot=['999C5'], format='hm')
    for line in lines.split('\n'):
        if (re.search(zenodo_url_regex, line) or \
            re.search(zenodo_doi_url_regex, line)) and not \
            re.search(zenodo_doi_regex, line):
            line = re.sub(zenodo_url_regex, r'$$adoi:10.5281/zenodo.\1', line)
            line = re.sub(zenodo_doi_url_regex, r'$$adoi:10.5281/zenodo.\1', line)
        print line


def zenodo_citations():
    zenodo_regex = re.compile(r'^doi:10\.5281/zenodo\.\d+$')
    zenodos = []
    for ref in get_all_field_values('999C5a'):
        if ref.startswith('doi:10.5281/zenodo.'):
            search = '999C5a:' + ref
            cites =  perform_request_search(p=search, cc='HEP')
            if len(cites):
                if not re.match(zenodo_regex, ref):
                    print 'Problem with DOI extraction:', search, cites
                    continue
                url = 'https://doi.org/api/handles/' + ref.replace('doi:', '')
                try:
                    checkURL(url)
                except ValueError:
                    print 'Problem with DOI:', search, cites
                    continue
                zenodos.append((len(cites), ref, cites))
    for doi in sorted(zenodos, reverse=True):
        print doi[0], doi[1]
        for recid in doi[2]:
            url = 'https://inspirehep.net/record/' + str(recid) + '/references'
            print '   ', url





def bad_reports():

    RECIDS = set()
    search = ''
    for old, new in [('FERMILAB-FN-1025-T', 'CERN-2017-002-M'),
                     ('FERMILAB-FN-1025-T', 'CERN-2017-002'),
                     ('FERMILAB-FN-1021-T', 'CERN-TH-2016-112'),
                     ('FERMILAB-CONF-13-667-T', 'CERN-2013-004'),
                     ('FERMILAB-DESIGN-2012-01', 'CERN-LHCC-2012-015'),
                     ('FERMILAB-DESIGN-2012-02', 'CERN-LHCC-2012-016'),
                     ('FERMILAB-CONF-02-422', 'CERN-2003-002'),
                     ('FERMILAB-FN-1009-CD', 'CERN-LPCC-2016-001'),
                     ('FERMILAB-PUB-16-296-T', 'CERN-TH-2016-111'),
                     ('FERMILAB-FN-0779', 'CERN-2005-005')
                    ]:
        search = search + ' or 999C5r:' + old
    import re
    search = re.sub(r'^ or ', '', search)
    print search
        #tag = ['999C5']
        #cleanup(search, tag, cc='HEP', old='\$\$r' + old, new='$$r' + new)


if __name__ == '__main__':

    import re
    check_titles('find dadd 2020')
    #cleanup("100:'orcid.org' or 700:'orcid.org'", ['100','700'], cc='HEP', old=r'$$https?://orcid.org/0000', new='$$jORCID:0000')
    #cleanup("520__a:/github\.com/ -8564_y:github", ['520'], cc='HEP', old=r'500__ $$a.*https://github', new='8564_ $$yGitHub$$uhttps://github')
    #cleanup("678__a:/(prize|award|medal)/", ['678'], cc='HepNames')
    #cleanup("678__a:/dirac/", ['100', '678'], cc='HepNames')
    #author_count()
    #primarch()
    #cleanup('8564_u:"*linkedin.com/pub*"', ['8564'], cc='HepNames')
    #cleanup('773__t:"Presented at" -773__w:/\w/', ['773'], cc='HEP', old=r'^\d+ 773__ \$\$tPresented at', new='')
 
