#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unicodedata
import re
import os
import string

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import get_record
from invenio.search_engine import get_all_field_values
from invenio.search_engine import print_record
from invenio.bibformat_engine import BibFormatObject
from hep_convert_email_to_id import find_inspire_id_from_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field


if False:
  r = 1290484
  r = 1306437  

if False:
  search = '693__e:kek-bf-belle-ii 371__m:/\@/ -670__d:2014* -670__d:2013* -670__d:2012*'
  search = '8564_u:/today13-07/ or 8564_u:/today13-08/ or 8564_u:/today13-09/ or 8564_u:/today13-10/ or 8564_u:/today13-11/ or 8564_u:/today13-12/ 8564_u:/today14-01/ or 8564_u:/today14-02/ or 8564_u:/today14-03/ or 8564_u:/today14-04/ or 8564_u:/today14-05/ or 8564_u:/today14-06/'
  print search
  x = perform_request_search(p=search,cc='Deleted')
  print len(x)



if False:
  for i in range(94, 115):
    if i > 99: i = re.sub(r'1(\d\d)',r'\1',str(i))
    i = str(i)
    search = '037__a:arXiv:' + i + '*'
    search = search + ' or 037__a:physics/' + i + '*'
    search = search + ' and 037__c:physics.acc-ph'
    searchf = search + ' and 037__a:fermilab*'
    #print search
    x = perform_request_search(p=search,cc='HEP')
    xf = perform_request_search(p=searchf,cc='HEP')
    print i, len(x), len(xf) 

def create_xml(author,email,af,experiment):
    common_fields = {}
    common_tags = {}
   
    common_tags['980__'] = [('a', 'HEPNAMES')]
    common_tags['100__'] = [('a', author), ('g', 'ACTIVE')]
    common_tags['371__'] = [('m', email),('a', af),('z', 'current')]
    common_tags['693__'] = [('a', experiment),('z', 'current')]
    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    #return common_fields
    print print_rec(common_fields)



authors = [["E05","T.Nagae","Kyoto U","Spectroscopic Study of Ξ- Hypernucleus, 12ΞBe, via the 12C(K-, K+) Reaction"],
["E06","J.Imazato","KEK","Measurement of T-violating Transverse Muon Polarization in K+->π0μ+ν Decays"],
["E07","K.Imai, K.Nakazawa, H.Tamura","JAEA, Gifu U, Tohoku U","Systematic　Study of Double Strangeness System with an Emulsion-counter Hybrid Method"],
["E08","A.Krutenkova","ITEP","Pion double charge exchange on oxygen at J-PARC"],
["E10","A.Sakaguchi, T.Fukuda","Osaka U","Production of Nuetron-Rich Λ-Hypernuclei with the Double Charge-Exchange Reactions"],
["E11","T.Kobayashi","KEK","Tokai-to-Kamioka (T2K) Long Baseline Neutrino Oscillation Experimental Proposal"],
["E13","H.Tamura","Tohoku U","Gamma-ray spectroscopy of light hypernuclei"],
["E14","T.Yamanaka","Osaka U","Proposal for KL→ π0νν Experiment at J-PARC"],
["E15","M.Iwasaki, T.Nagae","RIKEN, Kyoto U","A Search for deeply-bound kaonic nuclear states by in-flight 3He(K-, n) reaction"],
["E16","S.Yokkaichi","RIKEN","Electron pair spectrometer at the J-PARC 50-GeV PS to explore the chiral symmetry in QCD"],
["E17","R.Hayano, H.Outa","U Tokyo, RIKEN","Precision spectroscopy of Kaonic 3He 3d → 2p X-rays"],
["E18","H.Bhang, H.Outa, H.Park","SNU, RIKEN, KRISS","Coincidence Measurement of the Weak Decay of 12ΛC and the three-body weak interaction process"],
["E19","M.Naruki","KEK","High-resolution Search for Θ+ Pentaquark in π-p → K-X Reactions"],
["E21","Y.Kuno","Osaka U","An Experimental Search for Lepton Flavor Violating μ−−e− Conversion at Sensitivity of 10−16 with a Slow-Extracted Bunched Proton Beam"],
["E22","S. Ajimura, A.Sakaguchi","Osaka U","Exclusive Study on the Lambda-N Weak Interaction in A=4 Lambda-Hypernuclei (Revised from Initial P10)"],
["E26","K. Ozawa","KEK","Search for ω-meson nuclear bound states in the π-+AZ → n+(A-1)(Z-1) ω reaction, and for ω mass modification in the in-medium &omega → π0γ decay."],
["E27","T. Nagae","Kyoto U","Search for a nuclear K bound state K-pp in the d(π+,K+) reaction"],
["E29","H. Ohnishi","RIKEN","Search for φ-meson nuclear bound states in the p + AZ → φ + (A-1)φ(Z-1) reaction"],
["E31","H. Noumi","RCNP, Osaka U","Spectroscopic study of hyperon resonances below KN threshold via the (K-, n) reaction on Deuteron"],
["E40","K.Miwa","Tohoku U","Measurement of the cross sections of Σp scatterings"]]

search = "371__u:/a/ or 371__u:/e/ or 371__u:/i/ or 371__u:/o/ or 371__u:/u/"



#x = perform_request_search(p=search,cc='HepNames')
#x = x[:5]
#print len(x)

fileName = 'tmp_junk.out'
output = open(fileName,'w')

if True:
  search = 'cn CMS and ac 300+ and 037__a:fermilab*'
  search = 'cn ATLAS and ac 300+ and 037__a:fermilab*'
  search = '037__z:fermilab*'
  search = "0247_9:ads 035:/[0-9]L\./"
  x = perform_request_search(p=search, cc='HEP')
  #print 'Number of Fermilab reports', len(x)
  #output.write(print_record(r,format='xm'))
#  x = x[:50]
  for r in x:
      output.write(print_record(r,ot=['001','773'],format='xm'))

#atsearch = '100__m:/\@/ or 700__m:/\@/'
#x = perform_request_search(p=atsearch, cc='HEP')
#for r in x:
#  output.write(print_record(r,ot=['001','700'],format='xm'))

#for author in authors:
#    au = author[1] 
#    email = author[0]
#    af = author[2]
#    #print au
#    au = re.sub(r'(.*[A-Z][A-Z]) ([A-Z][a-z].*)',r'\1, \2',au)
#    au = re.sub(r'(.*[a-z]) ([A-Z][A-Z].*)',r'\2, \1',au)
#    au = string.capwords(au)
#    search = "find a " + au
#    x = perform_request_search(p=search,cc='HepNames')
#    print search,' : ',len(x)
#    if len(x) < 1:
#        print email,af
#        create_xml(au,email,af,'KEK-BF-BELLE-II')
#    #output.write(print_record(r,ot=['001','371'],format='xm'))
output.close()


if False:
  search = '035__a:/1900/'
  x = perform_request_search(p=search,cc='HEP')
  for r in x:
      bibkeys = get_fieldvalues(r, '035__a')
      #print bibkeys
      for bibkey in bibkeys:
          if re.search(':1900', bibkey):
              print r, bibkey

if False:
  authorId = None
  authorName = None
  email = None
  already_checked = []
  search = ''
  search = '100__a:Z*'
  x = perform_request_search(p=search,cc='HepNames')
  for r in x:
    #authorId = find_inspire_id_from_record(r)
    authorName = get_fieldvalues(r,'100__a')[0]
    #email = get_fieldvalues(r,'371__m')
    #if authorName : printLine = authorName
    #if email : 
      #email = email[0]
      #printLine = printLine  + ' | ' + email
    #else :
      #email = None
    #if authorId : printLine = printLine  + ' | ' + authorId
    #print authorName, '|', r, '|', email, '|', authorId
    #printLine = authorName  + ' | ' + email  + ' | ' + authorId
    #print printLine
    if authorName not in already_checked:
      already_checked.append(authorName)
      search = 'find ea ' + authorName
      y = perform_request_search(p=search,cc='HepNames')
      if len(y) > 1:
        for rr in y:
          authorId = find_inspire_id_from_record(rr)
          #print "%s10 %s40 [%s]" % (rr, authorName, authorId)
          print '{0:11d} {1:40s} {2:20s}'.format(rr, authorName, authorId)
          #print rr, authorName, '[', authorId, ']'


