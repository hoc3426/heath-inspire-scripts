#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Version 2.4: 30.03.17 (by Florian Schwennsen)
#
# This program translates an affiliation given as a plain string into the standardized ICN (or DLU)
# of the SPIRES/ INSPIRE database.
#
#  syntax: bestmatch(aff,'ICN')
#       or bestmatch(aff,'DLU')
#  to get an ordered list of ICNs (DLUs) which should fit the affiliation string aff. The first part
#  of the tupels in the list is a number indicating the quality of the fit - the larger, the better.
#  Number <~ 5 usually (but not always) indicates that no 'real' fit is found. Special attention has
#  to be paid if the first tupels in the list have very close values.
#  The last Third number in the tupel estimates the largest possible number indicating the quality
#  of the fit since by construction that first number is not normalized and depends on the length 
#  of the original string.

import unicodedata
import re
import math
import cPickle
import copy
import codecs
from itertools import imap
from operator import mul
import traceback
#from sets import Set

#from invenio.search_engine import search_pattern
#from invenio.search_engine import get_most_popular_field_values



#settings
knowledgebasepath = "/afs/desy.de/user/l/library/proc/aff-translation"
tmppath = "/tmp"

#bonus for matching acronyms #opt 100412
acronymbonus = 1.2 
#modification of 'acronymbonus' if acronym is resolved #opt 100412 
resolvedacronym = .1
#penalty for frequent words
frequentpenalty = -0.4 
#for levenshtein; decrease distance by epsilon times length difference of the two strings
epsilon = 1
#penalty if trying to match TU vs Uni (or similar) #opt 070412
unipenalty = -3.5
#bonus for matching numbers
numberbonus = 2;

#penalty to take ICN which has no DLU #opt 140412
icnpenalty = -3.8
#keep at least $reduceselection in selection when trying to reduce it
reduceselection = 10*10
#to get more output, increase verbatim
verbatim = 0
#maximal number of affiliations to check in a detailed way
maxaff = 20
#maximal number of affiliations to check for substrings
maxaffsubstring = 4



#weight for number of matches between to normalized affiliation strings (using routine normaff3) #opt 010412
weightGrepCount0 = 2.85      
#weight for relative number of matches between to normalized affiliation strings (using routine normaff3)
weightGrepCount = 0
#weight for relative length of matching words between to normalized affiliation strings (using routine normaff3)
weightGrepLength = 0.1

#weight for number of matches between to normalized affiliation strings (using routine normaff1) #opt 160312
weightGrepCount10= -0.2
#weight for relative number of matches between to normalized affiliation strings (using routine normaff1)
weightGrepCount11=  0
#weight for relative length of matching words between to normalized affiliation strings (using routine normaff1)
weightGrepCount12=  0
#weight for matches between to normalized affiliation strings depending on how significant the words are (using routine normaff1)
weightWeightOfWords=10   * 0

#weight for similarity between two simplified affiliation strings (using routine simaff; based on Levenshtein distance) #opt 290312
weightModifiedLevenshtein   = -0.9
#weight for similarity between two normalized affiliation strings (using routine normaff3; based on Levenshtein distance on word level) #opt 290312
weightModifiedLevenshteinN  =  0.3
#weight for similarity between two normalized affiliation strings (using routine normaff1; based on Levenshtein distance on word level) #opt 290312
weightModifiedLevenshteinN1 = -0.1


#weight for longest common substring of two simplified affiliations (using routine simaff)
weightSmithWaterman   = 0
#weight for longest common substring of two normalized affiliations (using routine normaff3) #opt 030412
weightSmithWatermanN  = 0.16
#weight for longest common substring of two normalized affiliations (using routine normaff1)
weightSmithWatermanN1 = 0

#weights between maximal and average similarity for final match value #opt 090312
weightMax = 0.8
weightAve = 0.1

#weight for  number of matches between a normalized affiliation strings and a normalized DLU(using routine normaff3) #opt 010412
weightGrepDLU = 2.7 
#relative weight of matches between a normalized affiliation strings and the normalized part of DLU identifying the sub-institute part (using routine normaff3) #opt 120412
subinstituterelativeweight = 1.25
#relative weight of (negative) expected GrepDLU-matches  #opt 120412
grepdluexpect = 0.45
#weight for similarity between a normalized affiliation strings and a normalized DLU  (using routine normaff1; based on Levenshtein distance on word level) #opt 010412
weightSimDLU = -2.6

#averaging for affiliation found by splitting at ' and ' is too strong, instead we add the qualities and subtract 'combominus' for each additional affiliation #opt 130312
combominus = 6
#penalty if combination of institutes seems to fit best, but no ' and ' in affiliation string #opt 130312
noandpenalty = -3

#whether to combine two collections of affiliations found by different indices
#via union (+1) or intersection (-1)
enrichflag = -1

#how many variations of affiliation string are necessary to look
#for an 'omnipresent' word
omniminimum = 5 * 1.5 / 1.5
#bonus if 'omnipresent' word is NOT present #opt 040412
omnibonus = -1.8           
#'weight of words'-slope - measure for additional bonus for (nearly) unique words
wowslope = 5

###thanks to feedback by Heath:
#penalty if aff or proposed ICN has INFN but other not (same penalty used for 'Chicago U.' vs 'Illinois U. Chicago'
INFNpenalty = -10
#weight for number of papers from an affiliation #opt 170412
weightPaperCount = .2 * 1
#affiliation string length to ICN string length #opt 170412
afftoicnaverage = 6
afftoicnweight = -.1 * 1
#threshold to check string without accents instead
thresholdquality = 5 * 1 - 2


##to estimate maximal possible match of an affiliation string
#number of words in DLU/ICN
grepdluaverage = 3.2
#log of number of papers
logpapercountaverage = 2

##precomile basic regular expressions
regexpspace = re.compile(' ')
regexpspaces = re.compile('  +')
regexppossiblespaces = re.compile(' *')
regexpsuperfluidspaces = re.compile('  +')
regexpstartingspaces = re.compile('^ +')
regexptrailingspaces = re.compile(' +$')
regexpspaceorcomma = re.compile('[ ,]')
regexpcomma = re.compile(' , ')
regexpdash = re.compile('[\-–]')
regexpsemikolon = re.compile(';')
regexpsemikolonicns = re.compile(' *; *')
regexpsemilonseperator = re.compile(';   ')
regexptrainlingsemikolon = re.compile(';$')
regexptwoletters = re.compile('^[A-Z][A-Z]+$')
regexpthreeleters  = re.compile('[a-z]{3}')
regexpPLZ1 = re.compile('.*(\d{6}).*')
regexpPLZ2 = re.compile('.*(\d{5}).*')
regexpPLZ3 = re.compile('.*(\d{4}).*')
regexpPLZ4a = re.compile('[0-9\-–]{6}')
regexpPLZ4b = re.compile('.*?\D(\d{5,})\D.*')
regexppureword = re.compile('^[A-Z]*$')
regexppurenumber = re.compile('^[0-9]*$')
regexptruncafterdash = re.compile('[\-–].*')
regexptruncaftercomma = re.compile(',.*')
regexphash = re.compile('^#')
regexpszet = re.compile(u'ß')
regexpsnormcity = [re.compile('^[\-–] '), re.compile(' [\-–]$'), re.compile(' \/ ')]
regexptwist = re.compile('(.*?) (.*)')
regexpand1 = re.compile(' +and +')
regexpand2 = re.compile(' AND ')
regexpand3 = re.compile(' & ')
regexpunlisted = re.compile('^Unlisted')
regexpinst = re.compile('INST')
regexpnonalphanum = re.compile('\W')
regexpdlu = re.compile('find or create a DLU for. *')
regexpcity = re.compile('^[Cc]ity\?')
regexpnoicn = re.compile('noICNfound')

#workaround as Python 2.3 does not have sort(reverse=True)
def anticmp(a,b):
    return cmp(b,a)

#dictionary for country codes
inf = open(knowledgebasepath+'/countriescc.pickle')
countriescc = cPickle.load(inf)
inf.close()
countriescc.update({"USA": "US", "Montenegro": "ME", "Tadzhikistan": "TJ"})
#dictionaries to norm different writings and to keep countries and cities as 1! word
normcountries = {"People.?s Republic of China":  "China"}
normcountries.update({"Rumania": "Romania", "Italia": "Italy", "Brasil": "Brazil", "Deutschland": "Germany", "New Mexico": "New-Mexico", "Ivory Coast": "Cote-D'Ivoire", "The Netherlands": "Netherlands"})
normcountries.update({"România": "Romania", "Rumania": "Romania", "Italia": "Italy", "Brasil": "Brazil", "Deutschland": "Germany", "New Mexico": "New-Mexico", "Ivory Coast": "Cote-D'Ivoire", "Algérie": "Algeria", "México": "Mexico", "España": "Spain", "Netherland": "Netherlands"})
for country in countriescc:
    if regexpdash.search(country):
        normcountries.update({regexpdash.sub(' ',country) : country})
    elif regexpspace.search(country):
        normcountries.update({country : regexpspace.sub('-',country)})
#print len(normcountries)
#?#for country in countriescc:
#?#    normcountries.update({country.upper(): country})
#print len(normcountries)
inf = open(knowledgebasepath+'/normcities.pickle')
normcities = cPickle.load(inf)
inf.close()
#dictionaries to assign university type
unitypes = {"Na[tzc]ion":  "n",  "Nat ":  "n",  "Nat'l": "n", "State" :  "s",  "Estad":  "s",  "Tech":  "t",  "Federal":  "f",  "Normal":  "r",  "Medi[zc]":  "m",  "Pedago":  "d"}
directtypes = {"RWTH":  "t",  "MSU":  "s",  "TU":  "t",  "TUM":  "t" }
othertypes = { u"Pol[iy]+t[eé][hc]":  "p",  "College":  "c",  "Coll ":  "c",  "O[bs]servator":  "o",  "[sS]ternwarte":  "o",  "A[ck]ad ":  "a",  "A[ck]adem":  "a"}
#these are no real or good acronyms
notacronym = ["CEDEX", "UNITED", "KINGDOM", "HEP", "USA", "CNRS", "CNRS-IN2P3", "IN2P3-CNRS", "NSW", "QLD", "III", "IN2P3", "UMR", "CNR"]
# load list of frequentwords
def tfstrip(x): return x.strip()
freqfil = open(knowledgebasepath+'/frequentwords', 'r')
frequentwords = map(tfstrip, freqfil.readlines())
for frequentword in frequentwords:
    frequentword = unicode(frequentword.upper(),'utf-8',errors='ignore')

##precomile advanced regular expressions
regexpdirects = []
for direct in directtypes.keys():
    regexpdirects.append((re.compile('(^| )'+direct+'( |$)'), directtypes[direct]))
regexpunitype1 = re.compile('Univer[a-z]*? (Blvd|Drive|Ave|Street|Circle|Place|Park|Parc|Pkwy)')
regexpunitype2 = re.compile('(^| )Universe( |$)')
regexpunitype3 = re.compile('\-Uni[bv]e')
regexpunitype4 = re.compile('( |^)U( |$)')
regexpunitype5 = re.compile('( |^)Univ?( |$)')
regexpunitype6 = re.compile('( |^)uni[bv]ersi.*?( |$)')
regexpunitype7 = re.compile('Uniwersytet')
regexpunitype8 = re.compile('Hochsch.*?( |$)')
regexpunitype9 = re.compile('([a-z])Univers')
regexpunitype10 = re.compile('(.*Uni[bv].*?) (,|\#|\-) .*')
regexpunitype11 = re.compile('(^| )Univ.*')
regexpunitype12 = re.compile('(Univ.*? [a-zA-Z0-9\-\'\&\.]+ [a-zA-Z0-9\-\'\&\.]+ [a-zA-Z0-9\-\'\&\.]+ ).*')
regexpunitype13 = re.compile('.*( [a-zA-Z0-9\-\'\&\.]+ [a-zA-Z0-9\-\'\&\.]+ [a-zA-Z0-9\-\'\&\.]+ Univ.*).*')
regexpunitypes = []
for kw in unitypes.keys():
    regexpunitypes.append((re.compile(kw), unitypes[kw]))
regexpothertypes = []
for kw in othertypes.keys():
    regexpothertypes.append((re.compile(kw), othertypes[kw]))
regexpcities1 = re.compile('(.*?) State ')
regexpcities2 = re.compile('^[A-Z][A-Z]*\-')
regexpcities3 = re.compile('^CERN$')
regexpcities4 = re.compile('Mons-Hainaut')
regexpacro1 = re.compile('^[A-Z][A-Z0-9\-]*$')
regexpacro2 = re.compile('^[A-Z]\-[0-9]*$')
regexpacro3 = re.compile('^[A-Z][A-Z0-9]*$')
regexpsimplifyaff0 = re.compile(' _([DILQTU])[A-Z][A-Z] ')
regexpssimplifyaff = [(re.compile(' _ACA '), ' A '),
                      (re.compile(' _CEN '), ' C '),
                      (re.compile(' _EXP '), ' E '),
                      (re.compile(' _NUC '), ' N '),
                      (re.compile(' _PHY '), ' P '),
                      (re.compile(' _SEC '), ' S '),
                      (re.compile(' _AST '), ' AS '),
                      (re.compile(' _CHE '), ' Che '),
                      (re.compile(' _COM '), ' Com '),
                      (re.compile(' _COS '), ' Cos '),
                      (re.compile(' _EDU '), ' Edu '),
                      (re.compile(' _ELE '), ' Ele '),
                      (re.compile(' _ENG '), ' Eng '),
                      (re.compile(' _GRA '), ' Grav '),
                      (re.compile(' _OBS '), ' Obs '),
                      (re.compile(' _MAT '), ' Math '),
                      (re.compile(' _MEC '), ' Mec '),
                      (re.compile(' _MED '), ' Med '),
                      (re.compile(' _NAT '), ' Nat '),
                      (re.compile(' _PED '), ' Ped '),
                      (re.compile(' _POL '), ' Pol '),
                      (re.compile(' _RAD '), ' Rad '),
                      (re.compile(' _SEM '), ' Sem ')]
regexpsnormaff1 = [(re.compile(r'(?i)( |\-)U\.? '), ' _UNI '),
                   (re.compile(r'([a-z])\-Uni'), r'\1 Uni'),
                   (re.compile(r'([a-z])\-([A-Za-z])'), r'\1_____\2'),
                   (re.compile(r'([0-9])\-([0-9])'), r'\1_____\2'),
                   (re.compile(r' ([dl])[`~\']'), r' \1'),
                   (re.compile(r'[`~\'\-\(\)\[\]\.,;\:\"\/\?\\]'), ' '),
                   (re.compile('_____'), '-'),
                   (re.compile(r'\&'), ' and '),
                   (re.compile(u' (fuer|for|voor|für) '), ' '),
                   (re.compile(' (of|des?|di|dell?|da|do|van|von|degli) '), ' '),
                   (re.compile(' and '), ' '),
                   (re.compile(' (the|le|la|der|die|das) '), ' '),
                   (re.compile(u'_Str(aße|asse|ae|eet)? '), r'_Str '),
                   (re.compile('(?i)( |\-)Universi.*? '), ' _UNI '),
                   (re.compile('(?i)( |\-)Univ? '), ' _UNI '),
                   (re.compile('(?i) (Ph|F)[iy]si[ckq].*? '), ' _PHY '),
                   (re.compile('(?i) (Ph|F)[iy]s '), ' _PHY '),
                   (re.compile(' PH '), ' _PHY '),
                   (re.compile(' Fsica '), ' _PHY '),
                   (re.compile('(?i)( |\-)Inst\w*? '), ' _INS '),
                   (re.compile('(?i)( |\-)Istitut\w*? '), ' _INS '),
                   (re.compile('(?i)( |\-)A[ck]ad\w*? '), ' _ACA '),
                   (re.compile('(?i) Th?eor\w*? '), ' _THE '),
                   (re.compile('(?i) TH '), ' _THE '), 
                   (re.compile('(?i) Tech\w*? '), ' _TEC '),
                   (re.compile('(?i) Tecn[io]\w*? '), ' _TEC '),
                   (re.compile('(?i) Quant\w*? '), ' _QUA '),
                   (re.compile('(?i) Nu[ck]l\w*? '), ' _NUC '),
                   (re.compile('(?i) Experimen\w*? '), ' _EXP '),
                   (re.compile('(?i) Experimen\w*? '), ' _EXP '),
                   (re.compile('(?i) EXP '), ' _EXP '),
                   (re.compile('(?i) D[ei]part\w*? '), ' _DEP '),
                   (re.compile('(?i) D[ei]p '), ' _DEP '),
                   (re.compile('(?i) Dept '), ' _DEP '),
                   (re.compile('(?i)( |\-)[CZ]ent[er]\w*? '), ' _CEN '),
                   (re.compile('(?i)( |\-)[CZ]ent '), ' _CEN '),
                   (re.compile('(?i) Se[ck]t\w*? '), ' _SEC '),
                   (re.compile('(?i) Sezio\w*? '), ' _SEC '),
                   (re.compile('(?i) Seccio\w*? '), ' _SEC '),
                   (re.compile('(?i) Sez '), ' _SEC '),
                   (re.compile('(?i) Laborat\w*? '), ' _LAB '),
                   (re.compile('(?i) Labs? '), ' _LAB '),
                   (re.compile('(?i)( |\-)O[bs]se?rv\w*? '), ' _OBS '),
                   (re.compile('(?i)( |\-)Obs '), ' _OBS '),
                   (re.compile('(?i) Astro\w*? '), ' _AST '),
                   (re.compile('(?i) Mat '), ' _MAT '),
                   (re.compile('(?i) Math\w*? '), ' _MAT '),
                   (re.compile('(?i) Matem\w*? '), ' _MAT '),
                   (re.compile('(?i) Natl\.? '), ' _NAT '),
                   (re.compile('(?i) Na[tz]ion\w*? '), ' _NAT '),
                   (re.compile('(?i) Grav\w*? '), ' _GRA '),
                   (re.compile('(?i) Pol[iy]te\w*? '), ' _POL '),
                   (re.compile('(?i) Kernphys\w*? '), ' _NUC '),
                   (re.compile('(?i) Medi[cz]\w*? '), ' _MED '),
                   (re.compile('(?i) Med '), ' _MED '),
                   (re.compile('(?i) Ele[ck]tr\w*? '), ' _ELE '),
                   (re.compile('(?i) Elettro\w*? '), ' _ELE '),
                   (re.compile('(?i) Ele[ck]t?\.? '), ' _ELE '),
                   (re.compile('(?i) Ch[ei]mi\w*? '), ' _CHE '),
                   (re.compile('(?i) Inge[gn]\w*? '), ' _ENG '),
                   (re.compile('(?i) Engin\w*? '), ' _ENG '),
                   (re.compile('(?i) Eng\.? '), ' _ENG '),
                   (re.compile('(?i) Comput\w*? '), ' _COM '),
                   (re.compile('(?i) Radio\w*? '), ' _RAD '),
                   (re.compile('(?i) Mec[ch]ani\w*? '), ' _MEC '),
                   (re.compile('(?i) Mech\.? '), ' _MEC '),
                   (re.compile('(?i) Educa[ct]\w*? '), ' _EDU '),
                   (re.compile('(?i) Educ\.? '), ' _EDU '),
                   (re.compile(u'(?i) P[eä]dagog '), ' _PED '),
                   (re.compile('(?i) Pedag\.? '), ' _PED '),
                   (re.compile('(?i) Semicon\w*? '), ' _SEM '),
                   (re.compile('(?i) Halbleit\w*? '), ' _SEM '),
                   (re.compile('(?i) [CK]osm\w*? '), ' _COS '),    
                   (re.compile(' TU '), ' _TEC _UNI ')]   
regexpsnormcities = []
for key in normcities.keys(): 
    regexpsnormcities.append((re.compile(r'(?i)(\W|^)'+key+'(\W|$)'),
                              r'\1'+normcities[key]+r'\2'))
regexpsnormcountries = []
for key in normcountries.keys():
    regexpsnormcountries.append((re.compile(r'(?i)(\W|^)'+key+'(\W|$)'),
                                 r'\1'+normcountries[key]+r'\2'))
regexpjapancities = re.compile(r'([a-z])\-[sS]hi(\W|$)')
regexpsnorm3 = [(re.compile('Amirkabir'), 'Amir Kabir'),
                (re.compile('(\d) (\d)'), r'\1-\2'),
                (re.compile('[\,;\:]+'), ' , '),
                (re.compile(' \- '), ' , '),
                (re.compile(' (and|und|et|e|\&) '), ' and '),
                (re.compile(r'[\(\)\[\]"\/\?\\\^\$]'), '  '),
                (re.compile(r'[\(\)\[\]"\/\?\\\^\$]'), '  '),
                (re.compile('(?i)I\.N\.F\.N.'), 'INFN  '),
                (re.compile('In?stituto Nazional[ei] (di )?Fisica Nucleare'), 'INFN'),
                (re.compile('Istituto Naz Fis Nucleare'), 'INFN'),
                (re.compile('Consiglio Nazionale delle Ricerche'), 'CNR'),
                (re.compile(' A and M '), ' A\&M '),
                (re.compile('Deutsches Elektronen Synchrotron'), 'DESY'),
                (re.compile(' ([A-Za-z])\. '), r' \1 '),
                (re.compile(' ([A-Za-z])\.([A-Za-z])\.? '), r' \1\2 '),
                (re.compile(' ([A-Za-z])\.([A-Za-z])\.([A-Za-z])\.? '), r' \1\2\3  '),
                (re.compile(' ([A-Za-z])\.([A-Za-z])\.([A-Za-z])\.([A-Za-z])\.? '), r' \1\2\3\4 '),
                (re.compile('\.(\d)'), ' \1'),
                (re.compile('\.( |$)'), r'\1'),
                (re.compile('`'), '\''),
                (re.compile(' \& '), ' and '),
                (re.compile('(^|,) [tT]he '), ''),
                (regexpsuperfluidspaces, ' '),
                (regexptrailingspaces, ''),
                (regexpstartingspaces, ''),
                (re.compile(' POB ([0-9 ]*)'), r' POBox-\1 '),
                (re.compile(' P.?O[ \-\.]Box ([0-9 ]*)'), r' POBox-\1 '),
                (re.compile(' C P (\d)'), r' CP \1'),
                (re.compile(' P\.R\.China'), ' China'),
                (re.compile(' P ?R China'), ' China'),
                (re.compile('\. '), ' '),
                (re.compile(' \.'), ' '),
                (re.compile(', *$'), '')]
commoncombos = [('Astronomy', 'Astrophysics'), ('Astrophysical', 'Planetary'), ('Astrophysics', 'Cosmology'), ('Astrophysics', 'Space'), ('Chemistry', 'Biology'), ('Cosmology', 'Particle'), ('Earth', 'Space'), ('Economics', 'Management'), ('Education', 'Science'), ('Engineering', 'Optoeletronic'), ('Finance', 'Economics'), ('Galaxies', 'Cosmology'), ('General', 'Applied'), ('Health', 'Science'), ('Information', 'Communication'), ('Mathematics', 'Physics'), ('Mathematics', 'Psychology'), ('Particle', 'Nuclear'), ('Particles', 'Accelerators'), ('Physics', 'Applied'), ('Physics', 'Astronomy'), ('Physics', 'Astrophysics'), ('Physics', 'Cosmology'), ('Physics', 'Mathematics'), ('Physics', 'Mathematics'), ('Physics', 'Nuclear'), ('Physics', 'Phenomenology'), ('Physics', 'Technology'), ('Posts', 'Telecommunications'), ('Research', 'Development'), ('Research', 'Education'), ('Research', 'Exploration'), ('Research', 'Production'), ('Science', 'Innovation'), ('Science', 'Technology'), ('Sciences', 'Technology'), ('Scientific', 'Educational')]
regexpscommoncombos = []
for combo in commoncombos:
    regexpscommoncombos.append((re.compile(combo[0]+' +and +'+combo[1]),
                                combo[0]+' AND '+combo[1]))
regexpgrepmatch = re.compile('(\*|\(|\)|\$|\^|\-)')


#printing comments
def printcomment(string):
    if verbatim > 1:
        tracestack = traceback.extract_stack()
        #trace = '->'.join([tracestack[i][2] for i in range(1, len(tracestack)-1)])
        trace = tracestack[-2][2]
        intro = ' -{verbose}'+''.join('---' for i in range(len(tracestack)-3))
        comment = '-{%s}-{%s}-' % (trace, string)
        print intro + comment
    return


# loads list of cityambiguities and applies it to 'icncity'
def resolvecityambiguities():
    global FILREPORT
    FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
    #pairs are of form (city-name in plain string, city to also check)
    pairs = set([("Essen","Duisburg"), ("Delhi","New-Delhi"), ("New-Delhi","Delhi"), ("Wonju","Gangneung-City"), ("Clermont","Aubiere"), ("Saint-Jean","Edmonton")])
    #find city in affiliation string
    for icn in icndictionary:
        citiesinName = set([])
        for na in icndictionary[icn].naffs:
            citiesinName = citiesinName.union(extractCities(na))
        for cityinName in citiesinName-icndictionary[icn].cities:
            for city in icndictionary[icn].cities:
                if len(city) > 1:
                    pairs.add((cityinName,city))
    #suburbs
    for city in icncity.institutes:
        if regexpdash.search(city):
            stamm = regexptruncafterdash.sub('',city)
            if icncity.institutes.has_key(stamm):
                pairs.add((city,stamm))
                pairs.add((stamm,city))
    #work with copy to avoid 'chain reaction'
    institutescopy = icncity.institutes.copy()
    for staedte in set(pairs):
        if institutescopy.has_key(staedte[1]):
            if institutescopy.has_key(staedte[0]): 
                icncity.institutes[staedte[0]] = icncity.institutes[staedte[0]].union(institutescopy[staedte[1]])
                #icncity.institutes[staedte[1]] = icncity.institutes[staedte[1]].union(institutescopy[staedte[0]])
            else:
                for icn in institutescopy[staedte[1]]:
                    icncity.addinst(icn, staedte[0])
        #elif institutescopy.has_key(staedte[0]):
        #    for icn in institutescopy[staedte[0]]:
        #        icncity.addinst(icn, staedte[1])
    FILREPORT.close()

#def tgstrip(x): return x.strip()
def tgstrip(x): 
    try:
        return unicode(x.strip(),'utf-8')
    except:
        #print 'UTF-PROBELM',x.strip(),type(x)
        #        print 'UTF-PROBELM',x.strip(),type(x),type(unicode(x.strip(),'utf-8',errors='ignore'))
        #return unicode(x.strip(),'utf-8',errors='ignore')
        return x.strip()

# generates knowledgebase
def generateknowledgebase(file,forced):
    #global icnicn    
    global allinstitutes
    global icndictionary
    global icncity
    global icncountry
    #PLZ#global icnplz
    global icnsaff
    global icnacronym
    global icnword
    global coreinstitutes
    global unlisted
    global countryofcity
    global plaindictionary
    global resulthash
    global sjset1
    global sjset2
    regexp_gkb_ccdict = {}
    regexp_gkb_citydict = {}
    plaindictionary = {}
    resulthash = {}
    if forced:
        icncity = collection()
        icncountry = collection()
        #PLZ#icnplz = collection()
        icnsaff = collection()
        icnacronym = collection()
        #icnicn = collection()
        icndictionary = {}
        icnword = collection()
        coreinstitutes = set([])
        unlisted = {}
        countryofcity = {}
    else:
        inf = open(knowledgebasepath+'/'+file)
        icndictionary = cPickle.load(inf)
        icncity = cPickle.load(inf)
        icncountry = cPickle.load(inf)
        #plz#icnplz = cPickle.load(inf)
        icnsaff = cPickle.load(inf)
        icnacronym = cPickle.load(inf)
        icnword = cPickle.load(inf)
        unlisted = cPickle.load(inf)
        countryofcity = cPickle.load(inf)
        coreinstitutes = set([])
        #icnword = collection()
        inf.close()
    newicns = set([])
    if file  == 'aff-translator-old.pickle':
        databasefil = open(knowledgebasepath+'/aff-dlu-from-inspire-old.afb')
    else:
        databasefil = open(knowledgebasepath+'/aff-dlu-from-inspire.afb')
    databaseentries = map(tgstrip, databasefil.readlines())
    databasefil.close()
    databasefil = codecs.open(knowledgebasepath+'/sj.afb',encoding='utf-8',mode='r')
    sjset = map(tgstrip, databasefil.readlines())
    if (file  == 'aff-translator-1sthalf.pickle') or (file == 'aff-translator-2ndhalf.pickle'):
        #half=len(sjset)/2
        #global sjset1, sjset2
        #sjset1 = sjset[:half]
        #sjset2 = sjset[half:]
        sjset1 = []
        sjset2 = []
        i = 1
        for sjentry in sjset:
            if (i % 2) == 0:
                sjset1.append(sjentry)
            else:
                sjset2.append(sjentry)
            i += 1
        if (file  == 'aff-translator-1sthalf.pickle'):
            sjset = sjset1
        else:
            sjset = sjset2
    databaseentries.extend(sjset)
    databasefil.close()
    #databasefil = codecs.open(knowledgebasepath+'/wrongicns.afb',encoding='utf-8',mode='r')
    #databaseentries.extend(map(tgstrip, databasefil.readlines()))
    #databasefil.close()
    databasefil = open(knowledgebasepath+'/footnotes.afb')
    databaseentries.extend(map(tgstrip, databasefil.readlines()))
    databasefil.close()
    i=1
    print "generating icndictionary..."
    for entry in databaseentries:
        if regexphash.search(entry):
            sou = regexphash.sub('', entry)
            if regexpinst.search(entry): sou = 'INST' 
        else:
            if (i % 2000 == 0):
                print ' [gen] '+str(i)+' out of '+str(len(databaseentries)),sou,":",akzenteabstreifen(entry)
            elif (i % 200 == 0):
                print ' [gen] %6i/%6i' % (i,len(databaseentries))
            #icnicn.addline(entry,sou)
            parts = regexpsemilonseperator.split(entry)
            parts[-1] = regexptrainlingsemikolon.sub('',parts[-1])
            #print '\n-----------------------\n',entry
            #print parts
            if len(parts) < 2:
                print 'zu wenige Semikolons',entry
            else:
                icn = ordericns(parts[1])
                if icndictionary.has_key(icn):
                    if forced or not (parts[0] in icndictionary[icn].affs):
                        icndictionary[icn].addline(entry, sou)
                        newicns.add(icn)
                    #just update all combos in case on of its part has been updated
                    elif regexpsemikolon.search(icn):
                        newicns.add(icn)
                else:
                    try:
                        if len(parts) > 4:
                            icndictionary[icn] = standardinstitute(icn, parts[2], parts[0], parts[4], parts[3], sou, parts[-1])
                            newicns.add(icn)
                        else:
                            tdlu = ''
                            tcc = ''
                            tcity = ''
                            tcore = ''
                            for sicn in regexpsemikolonicns.split(icn):
                                #print ' [sicn] %s' % (sicn)                                
                                inst = icndictionary[sicn]
                                #inst.display()
                                if hasattr(inst, 'dlu'):
                                    if tdlu == '':
                                        tdlu = inst.dlu
                                    else:
                                        tdlu += '; '+inst.dlu
                                if hasattr(inst, 'countries'):
                                    for cc in inst.countries:
                                        if tcc == '':
                                            tcc = cc
                                        else:
                                            if not regexp_gkb_ccdict.has_key(cc):
                                                regexp_gkb_ccdict[cc] = re.compile(cc)
                                            if not regexp_gkb_ccdict[cc].search(tcc):
                                                tcc += '; '+cc
                                if hasattr(inst, 'cities'):
                                    for city in inst.cities:
                                        if tcity == '':
                                            tcity = city
                                        else:
                                            if not regexp_gkb_citydict.has_key(city):
                                                regexp_gkb_citydict[city] = re.compile(city)
                                            if not regexp_gkb_citydict[city].search(tcity):
                                                tcity += '; '+city
                                if hasattr(inst,'core') and inst.core:
                                    tcore = 'CORE'
                            #print " [constructed] standardinstitute(%s, %s, %s, %s, %s, %s, %s)" % (icn, tdlu, parts[0], tcity, tcc, sou, tcore)
                            icndictionary[icn] = standardinstitute(icn, tdlu, parts[0], tcity, tcc, sou, tcore)
                            newicns.add(icn)
                    except:
                        try:
                            print '[!]','(((%s)))' % (icn), entry
                        except:
                            print '[!] not able to print no.', i
            i += 1
    i=1
    #completely unknown institute
    icndictionary['Unlisted'] = standardinstitute(u'Unlisted', u'unlisted', u'Unlisted', u'', u'XX', u'INST', u'')
    unlisted[u'XX'] = set([u'Unlisted'])
    unlisted[u'NONE'] = set([u'Unlisted'])
    print "finding omnipresent words and propagating informations to combinations..."
    #for icn in icndictionary:
    for icn in newicns:
        if (i % 2000 == 0):
            print ' [fin] '+str(i)+'/'+str(len(newicns)),akzenteabstreifen(icn)
        #find 'omnipresent' words in affiliationstrings of an institute
        icndictionary[icn].findomnipresent()
        # ... propagate into combinations
        if regexpsemikolon.search(icn):
            icnatoms = regexpsemikolonicns.split(icn)
            for icnatom in icnatoms:
                if len(icnatom) < 3:
                    print 'ICN', icn, 'leads to too short ICN',icnatom
                elif not icndictionary.has_key(icnatom):
                    print 'ICN',icnatom,'does not exist'
                else:
                    icndictionary[icn].word = icndictionary[icn].word.union(icndictionary[icnatom].word)
                    icndictionary[icn].omni = icndictionary[icn].omni.union(icndictionary[icnatom].omni)
                    icndictionary[icn].acronyms = icndictionary[icn].acronyms.union(icndictionary[icnatom].acronyms)
        elif not 'INST' in icndictionary[icn].sources:
            print 'ICN',icn,'not in INSPIRE'
        else:
            #keep city -> country information
            for stadt in list(icndictionary[icn].cities):
                for land in list(icndictionary[icn].countries):
                    if land != '':
                        if regexpunlisted.search(icn):
                            unlisted[land] = set([icn])
                        if stadt != '':
                            countryofcity[stadt] = land
            else:
                countryofcity[list(icndictionary[icn].cities)[0]] = land
            #read of mother/daughter constellation from ICN
            if re.search(',',icn) and not re.search(';',icn):
                mother = regexptruncaftercomma.sub('', icn)
                if icndictionary.has_key(mother):
                    icndictionary[icn].mother.add(mother)
                    icndictionary[mother].daughter.add(icn)
        i += 1
    #create indices
    i=1
    print "creating indices..."
    #for icn in icndictionary:
    for icn in newicns:
        if (i % 2000 == 0):
            print ' [crI] '+str(i)+'/'+str(len(newicns)),akzenteabstreifen(icn)
        #icnword.addinst(icn,icndictionary[icn].word)
        #PLZ#icnplz.addinst(icn,icndictionary[icn].plzs)
        icnsaff.addinst(icn,icndictionary[icn].saffs)
        icnacronym.addinst(icn,icndictionary[icn].acronyms)
        for cit in icndictionary[icn].cities:
            if cit != "Normal": icncity.addinst(icn,normcity(cit,[]))
                             
        icncountry.addinst(icn,icndictionary[icn].countries)
        i += 1
        if icndictionary[icn].core:
            coreinstitutes.add(icn)
    #remove cities and countries from word lists
    nowords = set(icncity.institutes.keys()).union(countriescc.keys())
    print "cleaning words..."
    #for icn in icndictionary:
    i = 1
    for icn in newicns:
        if (i % 2000 == 0):
            print ' [cle] '+str(i)+'/'+str(len(newicns)),akzenteabstreifen(icn)
        icndictionary[icn].word = icndictionary[icn].word.difference(nowords)
        i += 1
    #create indices
    i=1
    print "creating word-index..."
    #for icn in icndictionary:
    for icn in newicns:
        if (i % 2000 == 0):
            print ' [crW] '+str(i)+'/'+str(len(newicns)),akzenteabstreifen(icn)
        icnword.addinst(icn,icndictionary[icn].word)
        i += 1
    print "resolving city ambiguities..."    
    resolvecityambiguities()
    allinstitutes = set(icndictionary.keys())
    #save database and indices
    ouf = open(knowledgebasepath+'/'+file, 'w')
    cPickle.dump(icndictionary,ouf,2)
    cPickle.dump(icncity,ouf,2)
    cPickle.dump(icncountry,ouf,2)
    #PLZ#cPickle.dump(icnplz,ouf,2)
    cPickle.dump(icnsaff,ouf,2)
    cPickle.dump(icnacronym,ouf,2)
    cPickle.dump(icnword,ouf,2)
    cPickle.dump(unlisted,ouf,2)
    cPickle.dump(countryofcity,ouf,2)
    cPickle.dump(coreinstitutes,ouf,2)
    ouf.close()

def loadknowledgebase(file):
    global icndictionary
    global icncity
    global icncountry
    #PLZ#global icnplz
    global icnsaff
    global icnacronym
    global icnword
    global coreinstitutes
    global unlisted
    global countryofcity
    global plaindictionary
    global resulthash
    global allinstitutes
    plaindictionary = {}
    resulthash = {}
    inf = open(knowledgebasepath+'/'+file)
    icndictionary = cPickle.load(inf)
    icncity = cPickle.load(inf)
    icncountry = cPickle.load(inf)
    #PLZ#icnplz = cPickle.load(inf)
    icnsaff = cPickle.load(inf)
    icnacronym = cPickle.load(inf) 
    icnword = cPickle.load(inf)
    unlisted = cPickle.load(inf)
    countryofcity = cPickle.load(inf)
    coreinstitutes = cPickle.load(inf)
    inf.close()
    allinstitutes = set(icndictionary.keys())
    unlisted[u'NONE'] = set([u'Unlisted'])
    icndictionary['Fermilab'].unitypes = []
    return

 
#how often is a word
def lenicnword(word):
    if icnword.institutes.has_key(word):
        return len(icnword.institutes[word])
    else:
        return 0

#how significant is a word (depending on how often it appears in affiliations)
def weightofword(word):
    if lenicnword(word) == 0:
        return 0
    else:
        return wowslope/lenicnword(word) + (1+frequentpenalty)

#=============================== aff normalization ... ============================================
#remove accents from a string
def akzenteabstreifen(string):
    if not type(string) == type(u'unicode'):
        string = unicode(string,'utf-8', errors='ignore')
        if not type(string) == type(u'unicode'):
            return string
        else:
            return unicode(unicodedata.normalize('NFKD',regexpszet.sub(u'ss', string)).encode('ascii','ignore'),'utf-8')
    else:
        return unicode(unicodedata.normalize('NFKD',regexpszet.sub(u'ss', string)).encode('ascii','ignore'),'utf-8')

#orders ICNs (DLUs) to avoid different records for 'aff A; aff B' and 'aff B; aff A'
def ordericns(ic):
    separatedicns = sorted(ic.split('; '))
    return "; ".join(separatedicns)

#extracts University type from a (normalized) affiliation string
#types: n = National Uni, t = Technical Uni, s = State Uni, r = Normal Uni,
#       f = Federal Uni, m = Medical Uni, d = Pedagocial Uni, p = Polytechnical,
#       u = 'just' Uni, r = Oberservatory, a = Academy, c = College
def getunitype(na):
    type =""
    #direct?'
    for directtup in regexpdirects:
        if directtup[0].search(na):
            return directtup[1]
    #do not look at streets and Universe
    na = regexpunitype1.sub('\-street\- ', na)
    na = regexpunitype2.sub(r'\1Weltall\2', na)
    #different writings
    na = regexpunitype3.sub(' Unive', na)
    na = regexpunitype4.sub(r'\1University\2', na)
    na = regexpunitype5.sub(r'\1University\2', na)
    na = regexpunitype6.sub(r'\1University\2', na)
    na = regexpunitype7.sub('University', na)
    na = regexpunitype8.sub('University\1', na)
    na = regexpunitype9.sub(r'\1 Univers', na)
    na = regexpunitype10.sub(r'\1', na)
    na = regexpsuperfluidspaces.sub(' ', na)
    if regexpunitype11.search(na):
	na = regexpunitype12.sub(r'\1', na)
	na = regexpunitype13.sub(r'\1', na)
        for unitup in regexpunitypes:
            if unitup[0].search(na):
                type += unitup[1]
        if (type==""):
            type = "u"
    else:
        for othertup in regexpothertypes:
            if othertup[0].search(na):
                type += othertup[1]
    return type

#extracts postal code from a (normalized) affiliation string
def extractPLZ(plzt):
    if regexpPLZ1.search(plzt):
        plzt = regexpPLZ1.sub(r'\1', plzt)
    elif regexpPLZ2.search(plzt):
        plzt = regexpPLZ2.sub(r'\1', plzt) 
    elif regexpPLZ3.search(plzt):
        plzt = regexpPLZ3.sub(r'\1', plzt) 
    elif regexpPLZ4a.search(plzt):
        plzt = regexpdash.sub('', plzt)
        plzt = regexpPLZ4b.sub(r'\1', plzt)
    else:
        plzt = ""
    return plzt

#extracts city (cities) from a (normalized) affiliation string
def extractCities(na):
    na = regexpcities1.sub('State ', na)
    nparts = regexpspace.split(na)
    cities = set()
    for npart in nparts:
        npart = regexpcities2.sub('', npart)
        #CERN is in Geneva!
        npart = regexpcities3.sub('Geneva', npart)
        if not icncity.institutes.has_key(npart):
            npart = npart.title()
        if icncity.institutes.has_key(npart):
            city = npart
            #if (verbatim > 0):
            #    FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
            #    FILREPORT.write(" City = "+city+"\n")
            #    FILREPORT.close()
            cities.add(city)
    if regexpcities4.search(na): cities.add('Mons')
    return cities

#extracts country (countries) type from a (normalized) affiliation string
def extractCountries(na):
    nparts = regexpspace.split(na)
    countries = set()
    for npart in nparts:
        if not countriescc.has_key(npart):
            npart = npart.title()
        if countriescc.has_key(npart):
	    country =  countriescc[npart]
            #if (verbatim > 0):
            #    global FILREPORT
            #    FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
            #    FILREPORT.write(" Country = "+country+"\n")
            #    FILREPORT.close()
            countries.add(country)
    #pick country code at end of adress
    if npart.upper() in countriescc.values():
        if (verbatim > 0):
            FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
            FILREPORT.write(" Country = "+npart.upper()+"\n")
            FILREPORT.close()
        countries.add(npart.upper())        
    return countries

#extracts acronyms from a (normalized) affiliation string
def extractAcronyms(na):
    #print ' eA from',na
    acronyms = set()
    #does it make sense to look for acronyms?
    if regexpthreeleters.search(na) or not regexpspace.search(na):
        nparts = regexpspaceorcomma.split(na)
        for npart in nparts:
            if regexpacro1.search(npart) and (len(npart) > 2) and not countriescc.has_key(npart.title()) and not (npart in notacronym) and not regexpacro2.search(npart):
                acronyms.add(npart)
            elif  regexpdash.search(npart):
                npartsparts = regexpdash.split(npart)
                for npartpart in npartsparts:
                    if regexpacro3.search(npartpart) and (len(npartpart) > 2) and not countriescc.has_key(npartpart.title()) and not (npartpart in notacronym):
                        acronyms.add(npartpart)                
    #print '  ',acronyms
    return acronyms

#normalizes cities inside a string
regexpnormcitydict = {}
def normcity(str,cities):
    for regexpnormcity in regexpsnormcity:
        str = regexpnormcity.sub('', str)
    for city in cities:
        try:
            if not regexpnormcitydict.has_key(city):
                regexpnormcitydict[city] = re.compile(r'(?i)(\W|^)'+city+'(\W|$)')
            str = regexpnormcitydict[city].sub(r'\1'+city+r'\2', str)
        except:
            print 'CITYPROBLEM:',city
    for regexpnormcities in regexpsnormcities:
        str = regexpnormcities[0].sub(regexpnormcities[1], str)
    for regexpnormcountries in regexpsnormcountries:
        str = regexpnormcountries[0].sub(regexpnormcountries[1], str)
    #Japanes cities
    str = regexpjapancities.sub(r'\1\2', str)
    return str
    #return str.title()


#simplifies an affiliation string radically to some kind of finger print
def simplifyaff(affiliation):
######    #insert spaces to be able to simplify e.g. "astrophysics & astronomy" at the same time
    affiliation = regexpspace.sub('  ', affiliation)
    affiliation = ' '+affiliation+' '
    # remove unspecific marks and words
    affiliation = regexpnonalphanum.sub('  ', affiliation)
    #affiliation = normcity(affiliation)
    #affiliation = re.sub(' (fuer|für|for|voor) ', ' ', affiliation)
    #affiliation = re.sub(' (of|des?|di|dell?|da|do|van|von|degli) ', ' ', affiliation)
    #affiliation = re.sub(' (and|und|et) ', ' ', affiliation)
    #affiliation = re.sub(' (the|le|la|der|die|das) ', r' ', affiliation)
    #simplify often used words 
    affiliation = regexpsimplifyaff0.sub(r' \1 ', affiliation)
    #affiliation = re.sub(' _DEP ', ' D ', affiliation)
    #affiliation = re.sub(' _INS ', ' I ', affiliation)
    #affiliation = re.sub(' _QUA ', ' Q ', affiliation)
    #affiliation = re.sub(' _LAB ', ' L ', affiliation)
    #affiliation = re.sub(' _THE ', ' T ', affiliation)
    #affiliation = re.sub(' _TEC ', ' T ', affiliation)
    #affiliation = re.sub(' _UNI ', ' U ', affiliation)
    for regexpsimplifyaff in regexpssimplifyaff:
        affiliation = regexpsimplifyaff[0].sub(regexpsimplifyaff[1], affiliation)
    #remove superfluid spaces
    #affiliation = re.sub('  *', ' ', affiliation)
    #remove all spaces
    affiliation = regexppossiblespaces.sub('', affiliation)
    #ignore cases
    affiliation = affiliation.upper()
    # remove unspecific marks and words
    #affiliation = re.sub(r'[\'\-\(\)\[\]\.,;\:`"\&\/\?\\]', '', affiliation)
    #print "affiliation\n";
    return affiliation

#normalizes an affiliation (old version) (no longer in use)
regexpplzdict = {}
def normaff1(affiliation):
    #additionally extract postal code
    plz = extractPLZ(affiliation)
    #specialities
    affiliation = ' '+akzenteabstreifen(affiliation)+' '
    for regexpnormaff1 in regexpsnormaff1:
        affiliation = regexpnormaff1[0].sub(regexpnormaff1[1], affiliation)
    #remove superfluid spaces
    affiliation = regexpsuperfluidspaces.sub(' ', affiliation)
    #remove spaces
    affiliation = regexptrailingspaces.sub('', affiliation)
    affiliation = regexpstartingspaces.sub('', affiliation)
    #ignore cases
    #affiliation =~ tr/[a-z]/[A-Z]', )
    #print "affiliation\n";
    #return normcity(affiliation)
    if plz and not regexpplzdict.has_key(plz):
        regexpplzdict[plz] = re.compile('( |^)'+plz+'( |$)')
    if plz and not regexpplzdict[plz].search(affiliation):
        return affiliation + ' ' + plz
    else:
        return affiliation

#normalizes an affiliation (newer version) 
def normaff3(affiliation):
    affiliation = ' '+affiliation+' '
    #very special
    #return normcity(affiliation)
    affiliation = regexpsuperfluidspaces.sub(' ', affiliation)
    affiliation = regexptrailingspaces.sub('', affiliation)
    affiliation = regexpstartingspaces.sub('', affiliation)
    for regexporm3 in regexpsnorm3:
         affiliation = regexporm3[0].sub(regexporm3[1], affiliation)
    return affiliation


#twists first two words of a string
def twist(str):
    str = regexptwist.sub(r'\2 \1', str)
    return str

#splits an affiliation string at 'and's in all possible wways
def splitaff(string):
    commoncombos = [('Astronomy', 'Astrophysics'), ('Astrophysical', 'Planetary'), ('Astrophysics', 'Cosmology'), ('Astrophysics', 'Space'), ('Chemistry', 'Biology'), ('Cosmology', 'Particle'), ('Earth', 'Space'), ('Economics', 'Management'), ('Education', 'Science'), ('Engineering', 'Optoeletronic'), ('Finance', 'Economics'), ('Galaxies', 'Cosmology'), ('General', 'Applied'), ('Health', 'Science'), ('Information', 'Communication'), ('Mathematics', 'Physics'), ('Mathematics', 'Psychology'), ('Particle', 'Nuclear'), ('Particles', 'Accelerators'), ('Physics', 'Applied'), ('Physics', 'Astronomy'), ('Physics', 'Astrophysics'), ('Physics', 'Cosmology'), ('Physics', 'Mathematics'), ('Physics', 'Mathematics'), ('Physics', 'Nuclear'), ('Physics', 'Phenomenology'), ('Physics', 'Technology'), ('Posts', 'Telecommunications'), ('Research', 'Development'), ('Research', 'Education'), ('Research', 'Exploration'), ('Research', 'Production'), ('Science', 'Innovation'), ('Science', 'Technology'), ('Sciences', 'Technology'), ('Scientific', 'Educational')]
    for regexpcommoncombos in regexpscommoncombos:
        string =  regexpcommoncombos[0].sub(regexpcommoncombos[1], string)
    liste = [regexpand1.split(string)]
    for i in range(len(liste[0])):
        liste[0][i] = regexpand2.sub(' and ', liste[0][i])
    if len(liste[0]) > 1:
        for i in range(len(liste[0])-2,-1,-1):
            liste2 = []
            for li in liste:
                li2 = li[:]
                li2[i] = li2[i]+' and '+li2[i+1]
                del li2[i+1]
                liste2.append(li2)
            liste.extend(liste2)
    return liste

#=============================== similarity measures ============================================
#counts matching words of two strings
def grepmatch(af,ka):
    afparts = regexpspace.split(af)
    kaparts = regexpspace.split(ka)
    kparts = 0
    for part in kaparts:
        if len(part) > 2:
            kparts += 1
    nparts=0
    matches=0
    wowmatches=0
    length=0
    #does it make sense to look for acronyms?
    if regexpthreeleters.search(af):
        acronyms = True
        #check whether acronym is written explicitly
        for part in set(kaparts):
            if regexptwoletters.search(part) and not re.search(part,af) and len(part) > 2:
                acronym = '.* '+''.join([x+'.* ' for x in part])
                if re.search(acronym,af):
                    matches += 1 + resolvedacronym * acronymbonus
    else:
        acronyms = False
    if (len(ka) > 1):
        #for part in afparts:
        for part in set(afparts):
            if len(part) > 2: 
                part = regexpgrepmatch.sub(r'\\\1',part)
		nparts += 1
                if re.search('(?i)( |^|\-)'+part+'( |\-|$)', ka):
                    #print '-found->',part
		    length += len(part)*len(part)
		    matches += 1
                    wowmatches += weightofword(part)
		    #number counts twice
                    if regexppurenumber.search(part):
                        matches += numberbonus
		    #acronym counts twice
                    elif (regexppureword.search(part) and acronyms and not (part == "USA")):
                          matches += acronymbonus
		    #frequent words are not that important
		    else:
                          part = part.upper()
                          if part in frequentwords:
                              matches += frequentpenalty
		#else:
                    #None
		    #$partn = normaff($part);
		    #if ($kan =~ /( |^)$partn( |$)/i)
		    #  {
		    #	$matches += 1 + $notationpenalty;
		    #  }
        #print "_| ".$matches."   ".round($matches/$nparts)."   ".round(math.sqrt($length)/length($af))."\n";
        if nparts > 0:
            return (matches, matches/nparts, math.sqrt(length)/len(af),wowmatches)
            #return matches
	else:
            return (-1,0,0,0)
            #-1
    else:
        return (-2,0,0,0)
        #-2

#maximal possible 'grepmatch' (for comparison)
def grepmatchmax(af):
    afparts = regexpspace.split(af)
    nparts=0
    matches=0
    wowmatches=0
    length=0
    #does it make sense to look for acronyms?
    if regexpthreeleters.search(af):
        acronyms = True
    else:
        acronyms = False
    #for part in afparts:
    for part in set(afparts):
        if len(part) > 2: 
            nparts += 1
            length += len(part)*len(part)
            matches += 1
            wowmatches += weightofword(part)
	    #number counts twice
            if regexppurenumber.search(part):
                matches += numberbonus
	    #acronym counts twice
            elif (regexppureword.search(part) and acronyms and not (part == "USA")):
                matches += acronymbonus
	    #frequent words are not that important
	    else:
                part = part.upper()
                if part in frequentwords:
                    matches += frequentpenalty
    if nparts > 0:
        return (matches, matches/nparts, math.sqrt(length)/len(af),wowmatches)
        #return matches
    else:
        return (-1,0,0,0)
        #-1



#bisschen schneller, bisschen ungenauer (case insensitive)
def grepmatchTEST(af,ka):
    afparts = regexpspace.split(af)
    kaparts = regexpspace.split(ka)
    gemeinsam = set(afparts).intersection(set(kaparts))
    kparts = 0
    length=0
    matches = 0
    nparts = 0
    for part in set(afparts):
        if len(part) > 2:
            nparts += 1
    #does it make sense to look for acronyms?
    if regexpthreeleters.search(af):
        acronyms = True
    else:
        acronyms = False
    wowmatches=0
    for word in gemeinsam:
        if len(word) > 2:
            matches += 1
            length += len(word)*len(word)
            wowmatches += weightofword(word)
            #number counts twice
            if regexppurenumber.search(word):
                matches += numberbonus
            #acronym counts twice
            elif (regexppureword.search(word) and acronyms and not (word == "USA")):
                matches += acronymbonus
            #frequent words are not that important
            word = word.upper()
            if word in frequentwords:
                matches += frequentpenalty
    if nparts > 0:
        return (matches, matches/nparts, math.sqrt(length)/len(af),wowmatches)
        #return matches
    else:
        return (-1,0,0,0)
        #-1

#calculates Levenshtein distance of two strings
def levenshtein(a,b):
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n        
    current = range(n+1)
    astripped = akzenteabstreifen(a)
    bstripped = akzenteabstreifen(b)
    if len(astripped) < len(a):
	astripped = a
    if len(bstripped) < len(b):
        bstripped = b
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                #be mild (.1 instead of 1) if letters differ only by accent | does not yet work: letters with accents take two places in string
                if (astripped[j-1] == bstripped[i-1]):
                    change = change + .1
                else:
                    change = change + 1
            current[j] = min(add, delete, change)
    return current[n]

#calculates Levenshtein distance of two strings on word level instead of character level
def levenshteinThorsten(ara,arb):
    n, m = len(ara), len(arb)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        ara,arb = arb,ara
        n,m = m,n
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if ara[j-1] != arb[i-1]:
                if levenshtein(ara[j-1],arb[i-1]) <= 1:
                    change += .1
                else:
                    change = change + 1
            current[j] = min(add, delete, change)
    return current[n]

#normalized Levenshtein measure on word level
def similarity(a,b):
    #print a,type(a), " ~? ",type(b)
    n, m = len(a), len(b)
    if min(n,m) > 0:
        return (levenshtein(a,b) - epsilon * abs(n-m))/math.sqrt(min(n,m))
    else:
        return 666

#normalized Levenshtein measure on word level
def similarityThorsten(a,b):
    ara = regexppossiblespaces.split(a)
    arb = regexppossiblespaces.split(b)
    n, m = len(ara), len(arb)
    if min(n,m) > 0:
        return (levenshteinThorsten(ara,arb) - epsilon * abs(n-m))/math.sqrt(min(n,m))
    else:
        return 666


#calculates overlap measure (~Smith-Waterman distance) of two strings
def smithwaterman(a,b):
    n, m = len(a), len(b)
    if n == 0: return m
    elif m ==0: return n
    else:
        gg = 1
        # Init the distance matrix
        mat = [ [ 0 for j in range(0,m+1) ] for i in range(0,n+1) ]
        for i in range(0,n):
            for j in range(0,m):
                if a[i] == b[j]:
                    cost = -1
                else:
                    cost = 0
                mat[i+1][j+1] = max(mat[i][j+1]-gg, mat[i+1][j]-gg, mat[i][j]-cost)
        maxs = [ apply(max,mat[i]) for i in range(0,n+1) ]
        return max(maxs)

#simple union does not work as different instances are not checked whether they are in fact identical
def enrichcandidates(kmenge, insti):
    if (enrichflag == -1):
        intersection = kmenge.intersection(insti)
        if len(intersection) > 0:
            return intersection
        elif len(kmenge) == 0:
            return insti
        else:
            return kmenge
    return kmenge.union(insti)

######## to be used from outside


def bestmatchsimple(string, identifier,run,onlycore=False):
    global FILREPORT
    FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
    if not globals().has_key('icndictionary'): loadknowledgebase('aff-translator.pickle')
    if resulthash.has_key(string):
        return resulthash[string]    
    elif  plaindictionary.has_key(string):
        inst = plaindictionary[string]
    else:
        inst = plaininstitute(string)
        plaindictionary[string] = inst
    if verbatim > 1:
        inst.display()
        inst.fdisplay(FILREPORT)
    #try exact match
    if icnsaff.institutes.has_key(list(inst.saffs)[0]):
        if verbatim > 1: FILREPORT.write(' exact match\n')
        printcomment(' exact match')
        kandidatenmenge = icnsaff.institutes[list(inst.saffs)[0]]
        run = 3
    else:
        kandidatenmenge = set([])
        #try city match
        if len(inst.cities) > 0:
            if verbatim > 1: FILREPORT.write(' city match\n')
            printcomment(' city match')
            for city in inst.cities:
                if icncity.institutes.has_key(city):
                    if not ((city == 'Normal') and (len(inst.countries & set(['US'])) == 0)):
                        kandidatenmenge = kandidatenmenge.union(icncity.institutes[city])
                        if verbatim > 1: FILREPORT.write('   - kandidatenmenge +'+str(len(icncity.institutes[city]))+' = '+str(len(kandidatenmenge))+'\n')
        #try country match
        elif len(inst.countries) > 0:
            if verbatim > 1: FILREPORT.write(' country match\n')
            printcomment(' country match')
            for country in inst.countries:
                if icncountry.institutes.has_key(country):
                    kandidatenmenge = kandidatenmenge.union(icncountry.institutes[country])
                    if verbatim > 1: FILREPORT.write('   - kandidatenmenge +'+str(len(icncountry.institutes[country]))+' = '+str(len(kandidatenmenge))+'\n')
        else:
            kandidatenmenge = allinstitutes
        #try acronym match
        if len(inst.acronyms) > 0:
            if verbatim > 1: FILREPORT.write(' acronym match\n')
            printcomment(' acronym match')
            for acronym in inst.acronyms:
                if icnacronym.institutes.has_key(acronym):
                    kandidatenmenge = enrichcandidates(kandidatenmenge,icnacronym.institutes[acronym])
                    if verbatim > 1: FILREPORT.write('   - kandidatenmenge +'+str(len(icnacronym.institutes[acronym]))+' = '+str(len(kandidatenmenge))+'\n')
        #try ordinary words match
        if (run < 3):
            for naff1 in inst.naffs1:
                liste = [(lenicnword(np),np) for np in regexpspace.split(naff1) if lenicnword(np) > 0]
                if len(liste) > 0:
                    liste.sort(anticmp)
                    kandidatenmenge2 = kandidatenmenge
                    for tupel in liste:
                        kandidatenmenge = kandidatenmenge.intersection(icnword.institutes[tupel[1]])
                        if verbatim > 1: FILREPORT.write('   - kandidatenmenge [all words] = '+str(len(kandidatenmenge))+'\n')
                    if len(kandidatenmenge) == 0:
                        if len(liste) >= 2:
                            kandidatenmenge = kandidatenmenge2.intersection(icnword.institutes[liste[0][1]].intersection(icnword.institutes[liste[1][1]]))
                            if verbatim > 1: FILREPORT.write('   - kandidatenmenge [2words] = '+str(len(kandidatenmenge))+'\n')
                            if len(kandidatenmenge) == 0:
                                kandidatenmenge = kandidatenmenge2.intersection(icnword.institutes[liste[0][1]])
                                if verbatim > 1: FILREPORT.write('   - kandidatenmenge [1word] = '+str(len(kandidatenmenge))+'\n')
                            if len(kandidatenmenge) == 0:
                                kandidatenmenge = kandidatenmenge2
                                if verbatim > 1: FILREPORT.write('   - kandidatenmenge [0word] = '+str(len(kandidatenmenge))+'\n')
                        elif len(liste) == 1:
                            kandidatenmenge = kandidatenmenge2.intersection(icnword.institutes[liste[0][1]])
                            if verbatim > 1: FILREPORT.write('   - kandidatenmenge [1word] = '+str(len(kandidatenmenge))+'\n')
                else:
                    kandidatenmenge = set([])
        #try to reduce to core institutes
        if onlycore:
            nurcorekandidaten = kandidatenmenge.intersection(coreinstitutes)
            #print '>',len(coreinstitutes),len(kandidatenmenge),len(nurcorekandidaten)
            if len(nurcorekandidaten) > 0:
                kandidatenmenge = nurcorekandidaten
        #else:
            #print '>',len(kandidatenmenge)
        if len(kandidatenmenge) == 0:
            if len(inst.countries) > 0:
                for country in inst.countries:
                    kandidatenmenge = kandidatenmenge.union(unlisted[country])
            elif len(inst.cities) > 0:
                for city in inst.cities:
                    kandidatenmenge = kandidatenmenge.union(unlisted[countryofcity[city]])
            else:
                kandidatenmenge = unlisted['XX']
        #try postal code match
        #elif len(inst.plzs) > 0:
        #   if verbatim > 1: FILREPORT.write(' postal code match\n')
        #    for plz in inst.plzs:
        #        if icnplz.institutes.has_key(plz):
        #            kandidatenmenge = enrichcandidates(kandidatenmenge,icnplz.institutes[plz])
        #            if verbatim > 1: FILREPORT.write('   - kandidatenmenge +'+str(len(icnplz.institutes[plz]))+' = '+str(len(kandidatenmenge))+'\n')
        FILREPORT.write(" consider "+str(len(kandidatenmenge))+" affiliations\n")        
    result = inst.assignmatches(kandidatenmenge)
    finalresult = False
    #if accents (or ordinary words match) spoil the matching
    if (result[0][0] < thresholdquality) and (run < 3):
        if (run == 1):
            strippedstring = akzenteabstreifen(string)
            if strippedstring != string:
                finalresult = bestmatchsimple(strippedstring, identifier, 2)
            elif (len(liste) > 0):
                finalresult = bestmatchsimple(string, identifier, 3)
        elif (len(liste) > 0):
            finalresult = bestmatchsimple(string, identifier, 3)
    if not finalresult:
        if identifier == 'DLU':
            dluresult = []
            for res in result:
                if (hasattr(res[1],'dlu') and (res[1].dlu != 'NONE')):
                    dluresult.append((res[0],res[1].dlu,res[2]))
                else:
                    dluresult.append((res[0],"find or create a DLU for: "+res[1].icn,res[2]))
            finalresult = dluresult
        else:     
            finalresult = [(res[0],res[1].icn,res[2]) for res in result]    
    FILREPORT.close()
    resulthash[string] = finalresult
    return finalresult


#from Python Cookbook:
def crossloop(sequences):
    result = [[]]
    for seq in sequences:
        result = [sublist + [item] for sublist in result for item in seq]
    return result

def bestmatch(string, identifier, onlycore=False, old=False):
    if old:
        if not globals().has_key('icndictionary'): 
            loadknowledgebase('aff-translator-old.pickle')
    if string:
        bm = bestmatchu(string, identifier,1,onlycore)
        return [(res[0],res[1].encode('ascii','ignore'),res[2]) for res in bm]
    else:
        return [(0,'Unlisted',0)]



def bestmatchu(string, identifier,run,onlycore=False):
    try:
        string = unicode(string,'utf-8', errors='ignore')
    except:
        print '[unicodeproblem in bestmatchu]',type(string)
    global FILREPORT
    FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
    if not globals().has_key('icndictionary'): loadknowledgebase('aff-translator.pickle')
    if plaindictionary.has_key(string):
        inst = plaindictionary[string]
    else:
        inst = plaininstitute(string)
        plaindictionary[string] = inst
    string = regexpand3.sub(' and ', string)
    if re.search(' and ',list(inst.naffs)[0]):
        result = []
        combinations = splitaff(string)
        #check cities of substrings and whether 
        spafcities = {}
        allhavecities = {}
        for combo in combinations:
            #print "   A) combo = ", combo
            for substring in combo:
                if not spafcities.has_key(substring):
                    #spafcities[substring] = extractCities(normaff3(substring))
                    spafcities[substring] = extractCities(normcity(substring,[]))
        #get bestmatchsimple-lists for possible substrings
        spaflists = {}
        for combo in combinations:
            allhavecities = min([len(spafcities[x]) for x in combo])
            if not allhavecities:
                cities = set()
                for substring in combo:
                    cities = cities.union(spafcities[substring])
                citystring = ''.join([x+' ' for x in cities])
            for substring in combo:
                if not spaflists.has_key(substring):
                    if len(spafcities[substring]) == 0:
                        spaflists[substring] = bestmatchsimple(substring+' - '+citystring, identifier,run,onlycore)[0:maxaffsubstring]
                    else:
                        spaflists[substring] = bestmatchsimple(substring, identifier,run)[0:maxaffsubstring]
        #combine bestmatchsimple-lists
        for combo in combinations:
            for crosscombos in crossloop([spaflists[substring]  for substring in combo]):
                value = 0
                valuemax = 0
                assignedicns = set()
                for x in crosscombos:
                    value += x[0]
                    valuemax += x[2]
                    assignedicns.add(str(x[1])+"; ")
                stri = ''.join(list(assignedicns))[0:-2]
                value -= (len(crosscombos)-1) * combominus
                valuemax -= (len(crosscombos)-1) * combominus
                result.append((value,stri,valuemax))
        result.sort(anticmp)
        return result
    else:
        return bestmatchsimple(string, identifier,run,onlycore)
    FILREPORT.close()


#=============================== classes ============================================

class institute:
    #add just the affiliation-string + generate normalization of it + extract postal code
    def addaff(self, aff):
        if aff not in self.affs:
            self.affs.add(aff)
            if hasattr(self,'cities'):
                ncaff = normcity(aff,self.cities)
            else:
                ncaff = normcity(aff,[])
            naff = normaff3(ncaff)
            naff1 = normaff1(naff)
            if naff not in self.naffs:
                self.naffs.add(naff)
                if naff1 not in self.naffs1:
                    self.naffs1.add(naff1)
                    saff = simplifyaff(naff1)
                    if saff not in self.saffs:
                        self.saffs.add(saff)
            words = set(regexpspace.split(re.sub(' , ',' ',naff1)))
            #PLZ#plz = extractPLZ(aff)
            acros = extractAcronyms(naff)
            #print " plz = ",plz
            unitype = getunitype(naff)
            for wo in words:
                if len(wo) > 2:
                    self.word.add(wo)
            #PLZ#if (plz != ""): self.plzs.add(plz)
            if (unitype != ""): self.unitypes.add(unitype)
            for acro in acros:
                self.acronyms.add(acro)
            #print aff, "|",plz, "|",saff
            #return (plz,saff,acros)
        #else:
            #return ("","",set())
    def quickmatch(self,otheraff):
        grep = -666
        grepdlu = -666
        for naff in self.naffs1:
            #for onaff in otheraff.naffs1:
            #     grep = max(grep,grepmatch(naff,onaff)[0])
            if hasattr(otheraff,'ndlu'):
                grepdlu = max(grepdlu,grepmatch(naff,otheraff.ndlu)[0],grepmatch(naff,otheraff.nicn)[0])
            else:
                grepdlu = max(grepdlu,grepmatch(naff,otheraff.nicn)[0])
        grepNEW = self.word.intersection(otheraff.word)
        grep = len(grepNEW)
        if (len(set(self.unitypes) & set(otheraff.unitypes))>0) or ((len(self.unitypes) == 0) and (len(otheraff.unitypes) == 0)):
            sauni = 0
        else:
            if (len(self.unitypes) == 0) or (len(otheraff.unitypes) == 0):
                sauni = unipenalty / 2
            else:
                sauni = unipenalty
        return grep + sauni + weightGrepDLU * grepdlu
    def match(self,otheraff):
        if verbatim > 2:
            FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
            FILREPORT.write(" <?> "+otheraff.icn+"\n")
            FILREPORT.close()
        if hasattr(otheraff,'dlu') and (otheraff.dlu != "NONE"):
            quality = [0]
        else:
            quality = [icnpenalty]
        naff = list(self.naffs)[0]
        naff1 = list(self.naffs1)[0]
        saff = list(self.saffs)[0]
        if (weightGrepCount0 != 0) or (weightGrepCount != 0) or (weightGrepLength != 0):
            grep = -666
            grepsummed = 0
            for onaff in otheraff.naffs:
                grept = sum(imap(mul, grepmatch(naff,onaff), (weightGrepCount0, weightGrepCount, weightGrepLength, 0)))
                grep = max(grep,grept)
                grepsummed += grept
            quality.append(weightMax*grep + weightAve*grepsummed/len(otheraff.naffs))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  grep=("+str(grep)+ ";" + str(grepsummed/len(otheraff.naffs))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if weightModifiedLevenshtein != 0:
            sim = -666
            simsummed = 0
            for osaff in otheraff.saffs:
                simt = similarity(saff,osaff)
                sim = max(sim,simt)
                simsummed += simt
            quality.append(weightModifiedLevenshtein * (weightMax*sim + weightAve*simsummed/len(otheraff.saffs)))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  sim=("+str(sim)+ ";" + str(simsummed/len(otheraff.saffs))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if weightSmithWaterman != 0:
            sw = -666
            swsummed = 0
            for osaff in otheraff.saffs:
                swt = smithwaterman(saff,osaff)
                sw = max(sw,swt)
                swsummed += swt
            quality.append(weightSmithWaterman * (weightMax*sw + weightAve*swsummed/len(otheraff.saffs)))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  sw=("+str(sw)+ ";" + str(swsummed/len(otheraff.saffs))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if weightModifiedLevenshteinN != 0:
            simN = -666
            simNsummed = 0
            for onaff in otheraff.naffs:
                simNt = similarityThorsten(naff,onaff)
                simN = max(simN,simNt)
                simNsummed += simNt
            quality.append(weightModifiedLevenshteinN * (weightMax*simN + weightAve*simNsummed/len(otheraff.naffs)))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  simN=("+str(simN)+ ";" + str(simNsummed/len(otheraff.naffs))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if weightSmithWatermanN != 0:
            swN = -666
            swNsummed = 0
            for onaff in otheraff.naffs:
                swNt = smithwaterman(naff,onaff)
                swN = max(swN,swNt)
                swNsummed += swNt
            quality.append(weightSmithWatermanN * (weightMax*swN + weightAve*swNsummed/len(otheraff.naffs)))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  swN=("+str(swN)+ ";" + str(swNsummed/len(otheraff.naffs))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if weightModifiedLevenshteinN1 != 0:
            simN1 = -666
            simN1summed = 0
            for onaff1 in otheraff.naffs1:
                simN1t = similarityThorsten(naff1,onaff1)
                simN1 = max(simN1,simN1t)
                simN1summed += simN1t
            quality.append(weightModifiedLevenshteinN1 * (weightMax*simN1 + weightAve*simN1summed/len(otheraff.naffs1)))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  simN1=("+str(simN1)+ ";" + str(simN1summed/len(otheraff.naffs1))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if weightSmithWatermanN1 != 0:
            swN1 = -666
            swN1summed = 0
            for onaff1 in otheraff.naffs1:
                swN1t = smithwaterman(naff1,onaff1)
                swN1 = max(swN1,swN1t)
                swN1summed += swN1t
            quality.append(weightSmithWatermanN1 * (weightMax*swN1 + weightAve*swN1summed/len(otheraff.naffs1)))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  swN1=("+str(swN1)+ ";" + str(swN1summed/len(otheraff.naffs1))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if (weightGrepCount10 != 0) or (weightGrepCount11 != 0) or (weightGrepCount12 != 0) or (weightWeightOfWords != 0):
            grep1 = -666
            grep1summed = 0
            for onaff1 in otheraff.naffs1:
                grep1t = sum(imap(mul, grepmatch(naff1,onaff1), (weightGrepCount10, weightGrepCount11, weightGrepCount12,weightWeightOfWords)))
                grep1 = max(grep1,grep1t)
                grep1summed += grep1t
            quality.append(weightMax*grep1 + weightAve*grep1summed/len(otheraff.naffs1))
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  grep1=("+str(grep1)+ ";" + str(grep1summed/len(otheraff.naffs1))+") quality="+str(quality)+"\n")
                FILREPORT.close()
        if weightGrepDLU != 0:
            grepdlu = -666
            if hasattr(otheraff,'ndlu'):
                gd = grepmatch(naff,otheraff.ndlu)[0]
                gi = grepmatch(naff,otheraff.nicn)[0]
                if gd > gi:
                    grepdlut = gd - len(set(regexpspace.split(otheraff.dlu))) * grepdluexpect
                else:
                    grepdlut = gi - len(set(regexpspace.split(otheraff.icn))) * grepdluexpect
                #grepdlut = max(grepdlu,grepmatch(naff,otheraff.ndlu)[0],grepmatch(naff,otheraff.nicn)[0])                
            else:
                grepdlut = max(grepdlu,grepmatch(naff,otheraff.nicn)[0]) - len(set(regexpspace.split(otheraff.icn))) * grepdluexpect
            grepdlu = max(grepdlu,grepdlut)
            if hasattr(otheraff,'mother') and len(otheraff.mother) > 0:
	        subinstitute = re.sub(icndictionary[list(otheraff.mother)[0]].nicn, '', otheraff.nicn)
                grepdlu += subinstituterelativeweight * (grepmatch(naff1,subinstitute)[0] - 1) 
            quality.append(weightGrepDLU * grepdlu)
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  grepdlu="+str(grepdlu)+" quality="+str(quality)+"\n")
                FILREPORT.close()
        if re.search(';',otheraff.icn) and not re.search(' and ',naff1):
            quality.append(noandpenalty * (len(re.split(';',otheraff.icn))-len(re.split(' and ',naff1))))
        else:
            quality.append(0)
        if weightSimDLU != 0:
            simdlu = -666
            simdlut = similarityThorsten(naff,otheraff.ndlu)
            simdlu = max(simdlu,simdlut)
            quality.append(weightSimDLU * simdlu)
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  simdlu="+str(simdlu)+" quality="+str(quality)+"\n")
                FILREPORT.close()
        if omnibonus != 0:
            omnib = 0
            for word in otheraff.omni:
                if not re.search(word,naff1):
                    omnib += omnibonus
            quality.append(omnib)
            if verbatim > 2:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write("  omnib="+str(omnib)+" quality="+str(quality)+"\n")
                FILREPORT.close()
        if (len(set(self.unitypes) & set(otheraff.unitypes))>0) or ((len(self.unitypes) == 0) and (len(otheraff.unitypes) == 0)):
            sauni = 0
        else:
            if (len(self.unitypes) == 0) or (len(otheraff.unitypes) == 0):
                sauni = unipenalty / 2.
            else:
                sauni = unipenalty
        quality.append(sauni)
        if verbatim > 2: 
            FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
            FILREPORT.write("  sauni="+str(sauni)+" quality="+str(quality)+"\n")            
            FILREPORT.close()
        #weight number of papers
        if weightPaperCount != 0:
            quality.append(weightPaperCount*otheraff.logpapercount)
        #weight affiliation string length to ICN string length
        if afftoicnweight != 0:
            afflen = len(list(self.affs)[0])
            quality.append(afftoicnweight * abs(afftoicnaverage - (afflen/len(self.affs)) / len(otheraff.icn)))
        #special INFN:
        if INFNpenalty != 0:
            if re.search('INFN',naff) or re.search('INFN',otheraff.icn):
                if not (re.search('INFN',naff) and re.search('INFN',otheraff.icn)):
                    quality.append(INFNpenalty)
                if re.search('U',naff) and not re.search('U',otheraff.icn):
                    quality.append(INFNpenalty)
                elif re.search('U',otheraff.icn) and not re.search('U',naff):
                    quality.append(INFNpenalty)
            #special US universities
            if re.search('Chicago',naff):
                if re.search('Illinois',naff):
                    if not re.search('Illinois',otheraff.icn):
                        quality.append(INFNpenalty)
                else:
                    if re.search('Illinois',otheraff.icn):
                        quality.append(INFNpenalty)
            if re.search('Madison',naff):
                if re.search('Wisconsin',naff):
                    if not re.search('Wisconsin',otheraff.icn):
                        quality.append(INFNpenalty)
                else:
                    if re.search('Wisconsin',otheraff.icn):
                        quality.append(INFNpenalty)
        if verbatim > 1:
            FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
            FILREPORT.write('qualityvector = (')
            for qu in quality:
                FILREPORT.write("%7.3f, " % (qu))
            FILREPORT.write(') ['+otheraff.icn+'] '+str(sum(quality))+'\n')
            FILREPORT.close()
        #TEST
        #for saff in self.saffs:
        #    if saff in otheraff.sidentifier:
        #        quality.append(1000
        #TEST2
        #if len(set(self.cities) & set(otheraff.cities))>0:
        #    print "___",len(set(self.cities) & set(otheraff.cities)),otheraff.icn,quality
        #TESTwordicn
        return sum(quality)
    def matchmax(self):
        quality = []
        naff = list(self.naffs)[0]
        naff1 = list(self.naffs1)[0]
        saff = list(self.saffs)[0]
        if (weightGrepCount0 != 0) or (weightGrepCount != 0) or (weightGrepLength != 0):
            quality.append(sum(imap(mul, grepmatchmax(naff), (weightGrepCount0, weightGrepCount, weightGrepLength, 0))))
	else:
	    quality.append(0)
        if weightSmithWaterman != 0:
            quality.append(weightSmithWaterman * len(saff))
	else:
	    quality.append(0)
        if weightSmithWatermanN != 0:
            quality.append(weightSmithWatermanN * len(naff))
	else:
	    quality.append(0)
        if weightSmithWatermanN1 != 0:
            quality.append(weightSmithWatermanN1 * len(naff1))
	else:
	    quality.append(0)
        if (weightGrepCount10 != 0) or (weightGrepCount11 != 0) or (weightGrepCount12 != 0) or (weightWeightOfWords != 0):
            quality.append(sum(imap(mul, grepmatchmax(naff1), (weightGrepCount10, weightGrepCount11, weightGrepCount12, 0))))
	else:
	    quality.append(0)
        if weightGrepDLU != 0:
            quality.append(weightGrepDLU * grepdluaverage)
	else:
	    quality.append(0)
        if weightPaperCount != 0:
            quality.append(weightPaperCount*logpapercountaverage)
	else:
	    quality.append(0)
        #if re.search(';',otheraff.icn) and not re.search(' and ',naff1):
        #if weightSimDLU != 0:
        #if omnibonus != 0:
        #weight number of papers
        #weight affiliation string length to ICN string length
        return sum(quality)
    def assignmatches(self, liste):
        #try to reduce list of candidates
        if len(liste) > reduceselection:
            qmhash = {}
            for aff in liste:
                qm = self.quickmatch(icndictionary[aff])
                if qmhash.has_key(qm):
                    qmhash[qm].append(aff)
                else:
                    qmhash[qm] = [aff]
            #lieber erstmal als echte liste
            liste2 = set([])
            qms = qmhash.keys()
            qms.sort(anticmp)
            if verbatim > 2:
                print "qms", [(qm,len(qmhash[qm])) for qm in qms]
            for qm in qms:
                liste2 = liste2.union(set(qmhash[qm]))
                if (len(liste2) > reduceselection) or ((len(liste2) > 0) and (qm < 0)):
                    break
            if verbatim > 1:
                FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
                FILREPORT.write(" %d reduced to %d (qm>=%f)\n" % (len(liste),len(liste2),qm))
                FILREPORT.close()
            liste = liste2
        if verbatim > 1:
            FILREPORT = codecs.open(tmppath + '/afftranslatorreport2', encoding='utf-8',mode='a+')
            FILREPORT.write('qualityvector = ( icnpen   ')
            if (weightGrepCount0 != 0) or (weightGrepCount != 0) or (weightGrepLength != 0):
                FILREPORT.write(" grep    ")
            if weightModifiedLevenshtein != 0:
                FILREPORT.write(" sim     ")
            if weightSmithWaterman != 0:
                FILREPORT.write(" sw      ")
            if weightModifiedLevenshteinN != 0:
                FILREPORT.write(" simN    ")
            if weightSmithWatermanN != 0:
                FILREPORT.write(" swN     ")
            if weightModifiedLevenshteinN1 != 0:
                FILREPORT.write(" simN1   ")
            if weightSmithWatermanN1 != 0:
                FILREPORT.write(" swN1    ")
            if (weightGrepCount10 != 0) or (weightGrepCount11 != 0) or (weightGrepCount12 != 0) or (weightWeightOfWords != 0):
                FILREPORT.write(" grep1   ")
            if weightGrepDLU != 0:
                FILREPORT.write(" grepdlu ")
            FILREPORT.write(" noand   ")
            if weightSimDLU != 0:
                FILREPORT.write(" simdlu  ")
            if omnibonus != 0:
                FILREPORT.write(" omnib   ")
            FILREPORT.write(" sauni   ") 
            if weightPaperCount != 0:
                FILREPORT.write(" paperc  ")
            if afftoicnweight != 0:
                FILREPORT.write(" aff/icn ")
            FILREPORT.write("\n")
            FILREPORT.close()
        score = [ ( self.match(icndictionary[aff]), icndictionary[aff], self.matchmax()) for aff in liste ]
        score.sort(anticmp)
        return score
    def findomnipresent(self):
        self.omni = set([])
        if len(self.naffs1) >= omniminimum:
            omnihash = {}
            for na1 in self.naffs1:
                nparts = set(regexpspace.split(na1))
                for npart in nparts:
                    if len(npart) > 3:
                        if omnihash.has_key(npart):
                            omnihash[npart] += 1
                        else:
                            omnihash[npart] = 1
            for omnicandidate in omnihash:
                if (omnihash[omnicandidate] == len(self.naffs1)) and (re.search('[a-zA-Z]',omnicandidate)):
                    self.omni.add(omnicandidate)
        elif re.search('_[A-Z]',self.nicn):
            omnicandidate = regexpspace.split(self.nicn)
            for oc in omnicandidate:
                if re.search('_[A-Z]',oc):
                    ocok = 1
                    for naff1 in self.naffs1:
                        if not re.search(oc,naff1):
                            ocok = 0
                    if ocok:
                        self.omni.add(oc)            
    def display(self):
        print "--------------------------"
        if hasattr(self,'core') and self.core:   print "CORE "
        if hasattr(self,'icn'):      print "ICN = ",self.icn
        if hasattr(self,'dlu'):      print "DLU = ",self.dlu
	if hasattr(self,'ndlu'):     print "ndlu= ",self.ndlu
        for aff in self.affs:        print "aff   = ",akzenteabstreifen(aff)
        for naff in self.naffs:      print "naff  = ",akzenteabstreifen(naff)
        for naff1 in self.naffs1:    print "naff1 = ",akzenteabstreifen(naff1)
        for saff in self.saffs:      print "saff  = ",saff
        #PLZ#for plz in self.plzs:      print "PLZ   = ",plz
        for cou in self.countries:   print "country    == ",cou
        for cit in self.cities:      print "city       == ",cit
        for typ in self.unitypes:    print "type       == ",typ
        for acro in self.acronyms:   print "acronym    == ",acro
        if hasattr(self,'sources'):
            for source in self.sources:
                print "source     == ",source
        if hasattr(self,'logpapercount'):
            print "logpapercount ==",self.logpapercount
        if hasattr(self,'omni'):
            for omni in self.omni:
                print "omni       == ",omni
        if hasattr(self,'word'):
            #print "word       == ",self.word
            liste = [(lenicnword(np),np) for np in self.word if lenicnword(np) > 0]
            liste.sort(anticmp)
            print "rel. word  == ",[tup[1] for tup in liste]
        if hasattr(self,'daughter'):
            if len(self.daughter) > 0:
                print "daughter   == ",self.daughter
        if hasattr(self,'mother'):
            if len(self.mother) > 0:
                print "mother   == ", self.mother
    def shortdisplay(self):
        print "--------------------------"
        if hasattr(self,'icn'): print "ICN = ",self.icn
        if hasattr(self,'dlu'): print "DLU = ",self.dlu
        for aff in self.affs: print "aff = ",aff
        for cou in self.countries: print "country == ",cou
        for cit in self.cities:  print "city == ",cit
    def fdisplay(self,file):
        file.write("\n--------------------------------------------------\n")
        if hasattr(self,'icn'): file.write("ICN = "+self.icn+"\n")
        if hasattr(self,'dlu'): file.write("DLU = "+self.dlu+"\n")
        for aff in self.affs: file.write("aff = "+aff+"\n")
        for naff in self.naffs: file.write("naff = "+naff+"\n")
        for naff1 in self.naffs1: file.write("naff1 = "+naff1+"\n")
        for saff in self.saffs: file.write("saff = "+saff+"\n")
        #PLZ#for plz in self.plzs: file.write("PLZ = "+plz+"\n")
        for cou in self.countries: file.write("country == "+cou+"\n")
        for cit in self.cities:  file.write("city == "+cit+"\n")
        for type in self.unitypes: file.write("type == "+type+"\n")
        for acro in self.acronyms: file.write("acronym == "+acro+"\n")
        if hasattr(self,'sources'):
            for source in self.sources:
                file.write("source == "+source+"\n")
        if hasattr(self,'logpapercount'):
            file.write("logpapercount =="+str(self.logpapercount)+"\n")
        if hasattr(self,'omni'):
            for omni in self.omni:
                file.write("omni == "+omni+"\n")

#class for affiliation given by author/ journal
class plaininstitute(institute):
    def __init__(self,aff):
        self.affs = set()
        self.saffs = set()
        self.naffs = set()
        self.naffs1 = set()
        #PLZ#self.plzs = set()
        self.acronyms = set()
        self.unitypes = set()
        self.omni = set()
        self.word = set()
        self.addaff(aff)
        self.cities = extractCities(list(self.naffs)[0])
        #extract country only if needed, i.e. if no city is found
        #if len(self.cities) == 0:
        self.countries = extractCountries(list(self.naffs)[0])
        #else:
        #    self.countries = set([])

#class for affiliation in knowledge base 
class standardinstitute(institute):
    def __init__(self, ic, dl, aff, cit, cou, sou, core):
        #print ic, dl, aff, cit, cou, sou, core
        self.cities = set(regexpsemikolonicns.split(normcity(cit.title(),[])))
        ic = ordericns(ic)
        dl = ordericns(dl)
        self.icn = ic        
        self.nicn = normaff1(normaff3(normcity(ic,self.cities)))
        if dl != None:
            self.dlu = dl
            self.ndlu = normaff1(normaff3(normcity(dl,self.cities)))
            self.sidentifier = set([simplifyaff(self.nicn),simplifyaff(self.ndlu)])
        else:
            #self.ndlu = self.nicn
            self.sidentifier = set([simplifyaff(self.nicn)])
        self.core = (core == 'CORE')
        self.affs = set()
        self.saffs = set()
        self.naffs = set()
        self.naffs1 = set()
        #PLZ#self.plzs = set()
	#self.acronyms = set()
        self.acronyms = extractAcronyms(ic+' '+dl)
        self.unitypes = set()
        self.sources = set([sou])
        self.omni = set()
        self.word = set()
        self.mother = set()
        self.daughter = set()
        self.addaff(aff)
        if dl != None:
            self.word = self.word.union(set(regexpspace.split(regexpcomma.sub(' ', self.ndlu))))
        self.word = self.word.union(set(regexpspace.split(regexpcomma.sub(' ', self.nicn))))
        #several cities possible + fill city-hash
        #cit = cit.title()
        #if re.search(';', cit):
        #    self.cities = set(regexpsemikolonicns.split(normcity(cit)))
        #else:
        #    self.cities = set([normcity(cit)])
        #several countries possible + fill country-hash
        if re.search(';', cou):
            self.countries = set(regexpsemikolonicns.split(cou))
        else:
            self.countries = set([cou])
        #papercount
        icrequest = "100__u:\""
        ics = regexpsemikolonicns.split(ic)
        for singic in ics:
            icrequest += singic + "\" and 100__u:\""
        self.logpapercount = math.log(len(search_pattern(p=icrequest[0:-13]))+.1)
    #add an alternative writing of the affiliation
    def addvariation(self, aff, cit, cou, sou):
        self.sources.add(sou)
        #print "   ",aff
        #several cities possible + fill city-hash
        #for cit2 in  regexpsemikolonicns.split(cit):
        #    cit2 = cit2.title()
        #    if cit2 not in self.cities:
        #        cit2 = normcity(cit2)
        for cit2 in regexpsemikolonicns.split(normcity(cit.title(),[])):
            self.cities.add(cit2)
        self.addaff(aff)
        #several countries possible + fill country-hash
        for cou2 in regexpsemikolonicns.split(cou):
            if cou2 not in self.countries:
                self.countries.add(cou2)
    #wrapper to add an alternative writing of the affiliation in one line
    def addline(self, line, sou):
        line = regexptrainlingsemikolon.sub('',line)
        parts = regexpsemilonseperator.split(line)
        if len(parts) > 4:
            self.addvariation(parts[0], parts[4], parts[3], sou)
        elif len(parts) > 3:
            self.addvariation(parts[0], '', parts[3], sou)
        else:
            self.addvariation(parts[0], '', '', sou)
    def __len__(self):
        return len(self.affs)

#collection of affiliations
class collection:
    def __init__(self):
        self.institutes = {}
    def addinst(self,icn,keys):
        if len(keys) > 0:
            if type(keys) != type(set()):
                keys = set([keys])
            for key in keys:                
                if self.institutes.has_key(key):
                    self.institutes[key].add(ordericns(icn))
                else:
                    self.institutes[key] = set([ordericns(icn)])

def displayall():
    loadknowledgebase('aff-translator.pickle')
    list(allinstitutes).sort()
    for icn in allinstitutes:
        icndictionary[icn].display()


#for text-database
def promote(file):
    loadknowledgebase('aff-translator.pickle')
    citydlu = {}
    icndlu = {}
    ccdlu = {}
    #create hashes with DLUs as keys
    for icn in icndictionary:
        if hasattr(icndictionary[icn],'dlu'):
            dlu = icndictionary[icn].dlu
            if dlu == 'NONE':
                dlu = "find or create a DLU for: "+icn
        else:
            dlu = "find or create a DLU for: "+icn
        if hasattr(icndictionary[icn],'cities'):
            citydlu[dlu] = icndictionary[icn].cities
        else:
            citydlu[dlu] = set([])
        icndlu[dlu] = icn
        ccdlu[dlu] = icndictionary[icn].countries
    #load file
    databasefil = open(knowledgebasepath+'/'+file,'r')
    databaseentries = map(tgstrip, databasefil.readlines())
    databasefil.close()    
    databasefil = codecs.open(knowledgebasepath+'/'+re.sub('\..*','.afb',file),encoding='utf-8',mode='w')
    databasenoICNfil = codecs.open(knowledgebasepath+'/'+re.sub('\..*','.noicn.afb',file),encoding='utf-8',mode='w')
    zeile = 1
    for entry in databaseentries:
        if re.search('^#',entry):
            databasefil.write(entry+'\n')
        else:
            parts = regexpsemilonseperator.split(entry)
            icn = []
            city = set([])
            cc = set([])
            if len(parts) < 2:
                print 'problematic line:',entry            
            elif icndlu.has_key(parts[0]):
                print 'institutename is in fact a DLU:',entry
            else:
                if len(parts) > 2:
                    if not re.search('\?$',parts[2]):
                        cc = set(regexpsemikolonicns.split(regexptrainlingsemikolon.sub('', parts[2])))
                    if (len(parts) > 3) and not re.search('\?$',parts[3]):
                        city = set(regexpsemikolonicns.split(regexptrainlingsemikolon.sub('',parts[3])))
                for dlu in regexpsemikolonicns.split(regexptrainlingsemikolon.sub('', parts[1])):
                    if icndlu.has_key(dlu):
                        icn.append(icndlu[dlu])
                        city = city.union(citydlu[dlu])
                        cc = cc.union(ccdlu[dlu])
                    elif regexpdlu.search(dlu):
                        icn.append(regexpdlu.sub('',dlu))
                    else:
                        print 'no ICN found for DLU=\"'+dlu+'\" (line '+str(zeile)+')'
                        icn.append('-noICNfound-')
                    if icndlu.has_key(parts[0]):
                        print 'aff \"'+parts[0]+'\" is a DLU (line '+str(zeile)+')'
                line = parts[0] + ';   '
                for it in set(icn):
                    try:
                        line += it+'; '
                    except:
                        print "PROBLEM IN ZEILE "+str(zeile)
                        print entry
                        line += it+'; '
                line += '  '+regexptrainlingsemikolon.sub('', parts[1])+';   '
                for ct in cc:
                    if (ct != 'cc?'):
                        line += ct+'; '
                line += '  '
                for ct in city:
                    if (len(ct) > 2) and not regexpcity.search(ct):
                        line += ct+'; '
                line = re.sub(';* *$', ';\n',line)
                if regexpnoicn.search(line):
                    databasenoICNfil.write(line)
                else:
                    databasefil.write(line)
        zeile += 1
    databasefil.close()
    databasenoICNfil.close()




#------------------
#displayall()
#generateknowledgebase('aff-translator.pickle',True)
#loadknowledgebase('aff-translator.pickle')
#icndictionary['Frascati'].display()
#icndictionary['Fermilab'].display()

