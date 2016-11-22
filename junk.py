#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unicodedata
import re
import os
import string
from datetime import date

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues
from invenio.search_engine import get_record
from invenio.search_engine import get_all_field_values
from invenio.search_engine import print_record
from invenio.bibformat_engine import BibFormatObject
from hep_convert_email_to_id import find_inspire_id_from_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field
from invenio.intbitset import intbitset

#from hep_aff import get_aff
#from numbers_beijing import IDS


search = "245__a:/\)$/ 372__9:inspire"
search = "037:/fermilab\-(apnote|d0\-en|en|exp|industrial|linac|pbarnote|research|review|upc|workbook)\-/ 8564_u:/shtml$/"
print search
result = perform_request_search(p=search, cc='HEP')
for recid in result:
    print print_record(recid, ot=['856'], format='xm')
quit()

emails = ["qinnian@ihep.ac.cn",
"hcai@whu.edu.cn",
"hanshuang@ihep.ac.cn",
"huanghp@ihep.ac.cn",
"jianglw@ihep.a.cn",
"yangle@ihep.ac.cn",
"zhangzhenyu@ihep.ac.cn",
"xiangzhou@whu.edu.cn",
"Marcel.Werner@physik.uni-giessen.de",
"fanjz@ihep.ac.cn",
"helloliukai@126.com",
"wangxf@ihep.ac.cn",
"like2029@163.com",
"liteng_shiyan@163.com",
"malte@ep1.rub.de",
"chuxk@ihep.ac.cn",
"qinyao@ihep.ac.cn",
"shanwei@ihep.ac.cn",
"kingyu.pku@gmail.com",
"dongchao@ihep.ac.cn",
"kangxsh@ihep.ac.cn",
"chizhangphy@gmail.com",
"guot@ihep.ac.cn",
"huchen@ihep.ac.cn",
"julin@physics.umn.edu",
"kloss@kph.uni-mainz.de",
"D.Lin@gsi.de",
"schumans@kph.uni-mainz.de",
"whyaqm@gmail.com",
"dwbennet@imail.iu.edu",
"lurq@mail.ihep.ac.cn",
"puyn@ihep.ac.cn",
"renhl@mail.ihep.ac.cn",
"rainxiayucat@163.com",
"yunzeng@hnu.edu.cn",
"yu.ruai@163.com",
"zhzhang@ihep.ac.cn",
"luhj9404@hsu.edu.cn",
"liuhh123qwe@126.com",
"licui@mail.ustc.edu.cn",
"simonlh@ustc.edu.cn",
"wzh1988@mail.ustc.edu.cn",
"yanl@ihep.ac.cn",
"wencheng@mail.ustc.edu.cn",
"kangli60@yahoo.com.cn",
"z.haddadi@rug.nl",
"m.tiemens@rug.nl",
"Svende.Braun@physik.uni-giessen.de",
"alperen.yuncu@boun.edu.tr",
"onurkolcu@gmail.com",
"baiciank@andrew.cmu.edu",
"liuqian@ucas.ac.cn",
"liuxiaoxia12@mails.ucas.ac.cn",
"wangbinlong12@mails.ucas.ac.cn"]

for email in emails:
    search = '371:' + email + ' 035__9:INSPIRE'
    result = perform_request_search(p=search,cc='HepNames')
    if len(result) != 1:
        print email

print 'Done!'

search = '100__m:/\@/ or 700__m:/\@/'
result = perform_request_search(p=search,cc='HEP')
unique_emails = []
for recid in result:
    emails = get_fieldvalues(recid, '100__m') + \
             get_fieldvalues(recid, '700__m')
    for email in emails:
        if not email in unique_emails:
            unique_emails.append(email)

if False:
    for ID in IDS:
        search = '035__a:' + ID
        x = perform_request_search(p=search,cc='HepNames')
        if x:
            print ID, x


if False:
    search = 'find (fc p or fc t or fc l or fc g) and tc p'
    theory = intbitset(perform_request_search(p=search,cc='HEP'))
    for i in range(1,100):        
        search = 'find ac ' + str(i)
        result = intbitset(perform_request_search(p=search,cc='HEP'))
        x = theory & result
        print i, len(x), x[0:3]


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

def create_xml(author,nicname,vname,email,af,rank,experiment,start):
    common_fields = {}
    common_tags = {}
   
    common_tags['980__'] = [('a', 'HEPNAMES')]
    common_tags['100__'] = [('a', author), ('q', nicename), ('g', 'ACTIVE')]
    common_tags['371__'] = [('m', email),('a', af),('r', rank), ('z', 'current')]
    common_tags['400__'] = [('a', vname)]
    common_tags['693__'] = [('a', experiment),('s', start), ('z', 'current')]
    common_tags['670__'] = [('a', 'ihep')]
    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    #return common_fields
    print print_rec(common_fields)


if False:
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
    recid = 355574 
    output.write(print_record(recid, ot=['001','700'],format='xm'))

if False:
  result = [1317852, 1319472, 1324458, 1325164, 1326367, 1327466, 1328450, 1328598, 1328943, 1333186, 1333470]
  for r in result:
    #print r
    print print_record(r,ot=['001','980'],format='xm')
    print \
'''<datafield tag="980" ind1=" " ind2=" ">
    <subfield code="a">HEP</subfield>
  </datafield>
'''


if False:
  all_refs = []
  search = 'cn CMS and ac 300+ and 037__a:fermilab*'
  #search = 'cn ATLAS and ac 300+ and 037__a:fermilab*'
  #search = '037__z:fermilab*'
  #search = "0247_9:ads 035:/[0-9]L\./"
  #search = 'fin tc core and de 2014-01-01->2014-02-28'
  #search = 'fin tc core and tc arxiv and de 2014-01-01->2014-02-28'
  #search = 'find primarch hep-th and de 2014-01-01->2014-02-28'
  search = 'standard model'
  search = '"dark matter"'
  search = 'qcd sum rules'
  x = perform_request_search(p=search, cc='HEP')
  print 'Number of Fermilab reports', len(x)
  #output.write(print_record(r,format='xm'))
  output.write(search)
  output.write('\n')
  output.write(str(len(x)))
  output.write('\n')
  #x = x[:50]
  for r in x:
      try:
          #output.write(print_record(r,ot=['037'],format='xm'))
          search = 'citedby:recid:' + str(r)
          refs = perform_request_search(p=search, cc='HEP')
          #refs_0  = get_fieldvalues(r, '999C50')
          #refs_r  = get_fieldvalues(r, '999C5r')
          #refs_s  = get_fieldvalues(r, '999C5s')
          #refs_r0 = []
          #refs_s0 = []
          #for ref_r in refs_r:
          #    search = 'find r ' + ref_r
          #    result = perform_request_search(p=search, cc='HEP')
          #    if result:
          #        refs_r0.append(result)
          #for ref_s in refs_s:
          #    search = 'find j ' + ref_s
          #    result = perform_request_search(p=search, cc='HEP')
          #    if result:
          #        refs_s0.append(result)
          #refs = refs_0 + refs_r0 + refs_s0
          for ref in refs:
              all_refs.append(ref)
          #print refs
          #output.write(print_record(r,ot=['999C5'],format='hm'))
      except:
          print 'problem with', r
  #print all_refs
  from Counter import Counter
  counter=Counter(all_refs)
  #print all_refs
  d = Counter(all_refs)
  l = list(set(all_refs))
  topcites = {}
  #topcites = dict( (my_dict[k], k) for k in my_dict)
  for key in d:
      #if d[key] > 200: 
      topcites[d[key]] = key
  #sorted(topcites, key=topcites.get)
  #print topcites
  import collections
  od = collections.OrderedDict(sorted(topcites.items()))
  for k, v in od.iteritems(): 
      print k, v
      title = get_fieldvalues(v, '245__a')[0]
      print '  ', title


  #for letter in c:
  #    print '%s : %d' % (letter, c[letter])



if False:
    list_oth = ['hep-th','hep-ph','hep-ex','hep-lat','nucl-th','nucl-ex','gr-qc']
    list_ast = ['astro-ph.GA','astro-ph.CO','astro-ph.EP','astro-ph.HE','astro-ph.IP','astro-ph.SR']
    list_all = list_oth + list_ast
    print list_all
    for ast in list_ast:
        if ast in list_all:
            try:
               print list_all.remove(ast)
            except:
               print "ERROR", ast
            print list_all
    print list_all

if False:
    atsearch = '0247:10.1093/mnras/*l* -773__c:L*'
    atsearch = '773__p:Astron.Astrophys. 035__a:/A&A.*\dL\./ -773__c:L*'
    atsearch = '773__p:astron.astrophys. 773__y:2010->2016 -773__c:A*  -773__c:L*'
    x = perform_request_search(p=atsearch, cc='HEP')
    for r in x:
        output.write(print_record(r,ot=['001', '773'],format='xm'))

authors = [["Nian Qin", "Qin, N.", "Qin", "Wuhan University", "qinnian@ihep.ac.cn", "Graduate Student", "1/1/2013"],
["Hao Cai", "Cai, H.", "Cai", "Wuhan University", "hcai@whu.edu.cn", "Associate Prof.", "12/6/2011"],
["Shuang Han", "Han, S.", "Han", "Wuhan University", "hanshuang@ihep.ac.cn", "Graduate Student", "5/6/2013"],
["Haipeng Huang", "Huang, H.P.", "Huang", "Wuhan University", "huanghp@ihep.ac.cn", "Graduate Student", "1/1/2013"],
["Luwen Jiang", "Jiang, L.W.", "Jiang", "Wuhan University", "jianglw@ihep.a.cn", "Graduate Student", "1/1/2013"],
["Le Yang", "Yang, L.", "Yang", "Guangxi Normal University", "yangle@ihep.ac.cn", "Graduate Student", "9/1/2011"],
["Zhenyu Zhang", "Zhang, Z.Y.", "Zhang", "Wuhan University", "zhangzhenyu@ihep.ac.cn", "Lecture", "10/1/2009"],
["Xiang Zhou", "Zhou, X.", "Zhou", "Wuhan University", "xiangzhou@whu.edu.cn", "Lecture", "12/6/2011"],
["Marcel Werner", "Marcel Werner", "Werner", "Justus Liebig University Giessen", "Marcel.Werner@physik.uni-giessen.de", "PhD Student", "11/1/2010"],
["Jingzhou Fan", "Fan, J.Z.", "Fan", "Tsinghua University", "fanjz@ihep.ac.cn", "PhD Student", "9/1/2010"],
["Kai Liu", "Liu, K.", "Liu", "University of Chinese Academy of Sciences", "helloliukai@126.com", "PhD Student", "8/1/2009"],
["Xiongfei Wang", "Wang, X.F.", "Wang", "Tsinghua University", "wangxf@ihep.ac.cn", "PhD Student", "9/1/2009"],
["Ke Li", "Li, K.", "Li", "Shandong University", "like2029@163.com", "PhD Student", "9/1/2011"],
["Teng Li", "Li, T.", "Li", "Shandong University", "liteng_shiyan@163.com", "PhD Student", "4/1/2012"],
["Malte Albrecht", "Albrecht, M.", "Albrecht", "Bochum Ruhr-University", "malte@ep1.rub.de", "PhD Student", "1/1/2013"],
["xinkun Chu", "Chu, X.K.", "Chu", "Peking University", "chuxk@ihep.ac.cn", "Graduate Student", "9/1/2012"],
["Yao Qin", "Qin, Y.", "Qin", "Peking University", "qinyao@ihep.ac.cn", "PhD Student", "9/1/2010"],
["Wei Shan", "Shan, W.", "Shan", "Peking University", "shanwei@ihep.ac.cn", "Graduate Student", "9/1/2012"],
["Haiwang Yu", "Yu, H.W.", "Yu", "Peking University", "kingyu.pku@gmail.com", "PhD Student", "9/1/2011"],
["Chao Dong", "Dong, C.", "Dong", "Nankai University", "dongchao@ihep.ac.cn", "Graduate Student", "4/1/2012"],
["Xiaoshen Kang", "Kang, X.S.", "Kang", "Nankai University", "kangxsh@ihep.ac.cn", "PhD Student", "10/18/2012"],
["Chi Zhang", "Zhang, C.", "Zhang", "Nanjing University", "chizhangphy@gmail.com", "PhD Student", "9/1/2011"],
["Tun Guo", "Guo, T.", "Guo", "Nanjing Normal University", "guot@ihep.ac.cn", "Graduate Student", "9/1/2011"],
["Chen Hu", "Hu, C.", "Hu", "Nanjing Normal University", "huchen@ihep.ac.cn", "Graduate Student", "9/1/2011"],
["Andy Julin", "Julin, A.", "Julin", "University of Minnesota", "julin@physics.umn.edu", "Graduate Student", "1/1/2012"],
["Benedikt Kloss", "Kloss, B.", "Kloss", "Johannes Gutenberg University of Mainz", "kloss@kph.uni-mainz.de", "PhD Student", "4/1/2011"],
["Dexu Lin", "Lin, D.X.", "Lin", "Helmholtz Institute Mainz", "D.Lin@gsi.de", "PhD Student", "10/1/2011"],
["Sven Schumann", "Schumann, S.", "Schumann", "Johannes Gutenberg University of Mainz", "schumans@kph.uni-mainz.de", "PostDoc", "9/1/2012"],
["Yaqian Wang", "Wang, Y.Q.", "Wang", "Shandong University", "whyaqm@gmail.com", "Graduate Student", "1/1/2009"],
["Dan Bennett", "Bennett, D.W.", "Bennett", "Indiana University", "dwbennet@imail.iu.edu", "PhD Student", "4/1/2013"],
["Ruiqi Lu", "Lu, R.Q.", "Lu", "Hunan University", "lurq@mail.ihep.ac.cn", "Graduate Student", "8/1/2013"],
["Yanan Pu", "Pu, Y.N.", "Pu", "Hunan University", "puyn@ihep.ac.cn", "Graduate Student", "8/1/2013"],
["Hailong Ren", "Ren, H.L.", "Ren", "Hunan University", "renhl@mail.ihep.ac.cn", "Graduate Student", "8/1/2013"],
["Yu Xia", "Xia, Y.", "Xia", "Hunan University", "rainxiayucat@163.com", "Engineer", "6/30/2006"],
["Yun Zeng", "Zeng, Y.", "Zeng", "Hunan University", "yunzeng@hnu.edu.cn", "Professor", "1/1/2006"],
["Yujin Mo", "Mo, Y.J.", "Mo", "Central China Normal University", "yu.ruai@163.com", "Graduate Student", "9/1/2012"],
["Zhenghao Zhang", "Zhang, Z.H.", "Zhang", "Central China Normal University", "zhzhang@ihep.ac.cn", "Graduate Student", "8/31/2011"],
["Hai-jiang Lu", "Lu, H.J.", "Lu", "Huangshan College", "luhj9404@hsu.edu.cn", "Professor", "7/1/2009"],
["Huihui Liu", "Liu, H.H.", "Liu", "Henan University of Science and Technology", "liuhh123qwe@126.com", "Assistant Prof.", "6/6/2010"],
["Cui Li", "Li, Cui", "Li", "University of Science and Technology of China", "licui@mail.ustc.edu.cn", "Graduate Student", "6/30/2008"],
["Hao Liang", "Liang, H.", "Liang", "University of Science and Technology of China", "simonlh@ustc.edu.cn", "Associate Prof.", "1/1/2006"],
["Zhihong Wang", "Wang, Z.H.", "Wang", "University of Science and Technology of China", "wzh1988@mail.ustc.edu.cn", "Graduate Student", "9/6/2011"],
["Liang Yan", "Yan, L.", "Yan", "University of Science and Technology of China", "yanl@ihep.ac.cn", "PostDoc", "9/1/2004"],
["Wencheng Yan", "Yan, W.C.", "Yan", "University of Science and Technology of China", "wencheng@mail.ustc.edu.cn", "Graduate Student", "6/1/2012"],
["Kang Li", "Li, K.", "Li", "Unlisted", "kangli60@yahoo.com.cn", "Professor", "6/6/2010"],
["Zahra Haddadi", "Haddadi, Z.", "Haddadi", "KVI-CART, University of Groningen", "z.haddadi@rug.nl", "Graduate Student", "4/1/2013"],
["Marcel Tiemens", "Tiemens, M.", "Tiemens", "KVI-CART, University of Groningen", "m.tiemens@rug.nl", "Graduate Student", "4/1/2013"],
["Svende Braun", "Braun, S.", "Braun", "Justus Liebig University Giessen", "Svende.Braun@physik.uni-giessen.de", "Graduate Student", "7/1/2012"],
["Alperen Yuncu", "Yuncu, A.", "Yuncu", "Turkish Accelerator Center Particle Factory Group", "alperen.yuncu@boun.edu.tr", "Graduate Student", "2/1/2013"],
["Onur Bugra Kolcu", "Kolcu, O.B.", "Kolcu", "Turkish Accelerator Center Particle Factory Group", "onurkolcu@gmail.com", "PhD Student", "8/1/2013"],
["Bai-Cian Ke", "Ke, B.C.", "Ke", "Carnegie Mellon University", "baiciank@andrew.cmu.edu", "Graduate Student", "5/1/2013"],
["Qian Liu", "Liu, Q.", "Liu", "University of Chinese Academy of Sciences", "liuqian@ucas.ac.cn", "Research scientist", "6/30/2011"],
["Xiaoxia Liu", "Liu, X.X", "Liu", "University of Chinese Academy of Sciences", "liuxiaoxia12@mails.ucas.ac.cn", "Graduate Student", "6/1/2013"],
["Binlong Wang", "Wang, B.L.", "Wang", "University of Chinese Academy of Sciences", "wangbinlong12@mails.ucas.ac.cn", "Graduate Student", "6/1/2013"]]



if False:
#for author in authors:
    nicename = author[0] 
    vname = author[1]
    af = author[3]
    af = get_aff(af)
    email = author[4]
    rank = author[5]
    rank = re.sub(r'Graduate Student', r'PHD', rank)
    rank = re.sub(r'Research scientist', r'SENIOR', rank)
    rank = re.sub(r'Associate Prof.', r'SENIOR', rank)
    rank = re.sub(r'Assistant Prof.', r'JUNIOR', rank)
    rank = re.sub(r'Professor', r'SENIOR', rank)
    xdate = author[6]
    matchobj = re.match(r'(\d+)\/(\d+)\/(\d+)', xdate)
    mon=int(matchobj.group(1))
    day=int(matchobj.group(2))
    yyy=int(matchobj.group(3))
    date_started = date(yyy, mon, day).isoformat()
    #print au
    au = re.sub(r'(.*[A-Z][A-Z]) ([A-Z][a-z].*)',r'\1, \2',nicename)
    au = re.sub(r'(.*[a-z]) ([A-Z].*)',r'\2, \1',nicename)
#    au = string.capwords(au)
#    search = "find a " + au
#    x = perform_request_search(p=search,cc='HepNames')
#    print search,' : ',len(x)
#    if len(x) < 1:
#        print email,af
    create_xml(au,nicename,vname,email,af,rank,'BEPC-BES-III',date_started)
    #output.write(print_record(r,ot=['001','371'],format='xm'))
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
  search =   search = '100__a:Z*'
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


