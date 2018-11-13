"""
Input for the osti_web_service.py script.
"""


OSTI_URL = 'https://www.osti.gov/elink/docs/2411dtd.htm'
XML_PREAMBLE  = '<?xml version="1.0" encoding="UTF-8" ?>'
XML_PREAMBLE += '<!DOCTYPE records SYSTEM "' + OSTI_URL + '">'


TYPE_DICT = {
'ANNUAL':'PD',
'BACHELORS':'TD',
'CONF':'CO',
'CRADA':'TR',
'D0-EN':'TR',
'DESIGN':'TR',
'FACTSHEET':'FS',
'FN':'TR',
'HABILITATION':'TD',
'INDUSTRIAL':'PD',
'LOI':'TR',
'LU':'TR',
'MASTERS':'TD',
'MISC':'TR',
'MONTHLY':'PD',
'MUCOOL':'TR',
'PLAN':'PD',
'POSTER':'CO',
'PROPOSAL':'TR',
'PUB':'JA',
'REVIEW':'PD',
'SLIDES':'CO',
'THESIS':'TD',
'TM':'TR',
'VLHCPUB':'TR'
}

DIRECTORY = '/afs/cern.ch/project/inspire/TEST/hoc/osti/'

ACCEPTED_SEARCH = '8564_z:openaccess or 8564_z:postprint or \
8564_y:"article from scoap3" ignore'

DADD_SEARCH = 'dadd:2012 or dadd:2013 or dadd:2014 or \
dadd:2015 or dadd:2016 or dadd:2017 or dadd:2018'

THESIS_SEARCH = '8564_y:fermilabthesisf'

DOE_SUBJECT_CATEGORIES_DICT = {
'acc':'43 PARTICLE ACCELERATORS',
'ins':'46 INSTRUMENTATION RELATED TO NUCLEAR SCIENCE AND TECHNOLOGY',
'hep':'72 PHYSICS OF ELEMENTARY PARTICLES AND FIELDS',
'nucl':'73 NUCLEAR PHYSICS AND RADIATION PHYSICS',
'astro':'79 ASTRONOMY AND ASTROPHYSICS',
'math':'97 MATHEMATICS AND COMPUTING'
}

DOE_FERMILAB_DICT = {
'doe_contract_nos':'AC02-07CH11359',
'site_input_code':'FNAL',
#'language':'English',
'country_publication_code':'US',
'sponsor_org':'USDOE Office of Science (SC), High Energy Physics (HEP) (SC-25)',
'released_by':"Heath O'Connell",
'released_by_email':'hoc@fnal.gov',
'released_by_phone':'630-840-6017',
#'access_limitation':'unl',
'medium_code':'ED',
'file_format':'PDF/A'
}

DOE_AFF_DICT = {
'ARC':'Albany Research Center (ARC), Albany, OR (United States)',
'AMES':'Ames Laboratory (AMES), Ames, IA (United States)',
'ANL':'Argonne National Laboratory (ANL), Argonne, IL (United States)',
'BAPL':'Bettis Atomic Power Laboratory (BAPL), West Mifflin, \
PA (United States)',
'BNL':'Brookhaven National Laboratory (BNL), Upton, NY (United States)',
'DRI':'Desert Research Institute (DRI), Nevada System of Higher Education, \
Reno,NV (United States)',
'ETTP':'East Tennessee Technology Park (ETTP), Oak Ridge, TN (United States)',
'ETEC':'Energy Technology Engineering Center (ETEC), Canoga Park, \
CA (United States)',
'EML':'Environmental Measurements Laboratory (EML), New York, \
NY (United States)',
'FETC-MGN':'Federal Energy Technology Center-Morgantown (FETC-MGN), \
Morgantown, WV (United States)',
'FETC-PGH':'Federal Energy Technology Center-Pittsburgh (FETC-PGH), \
Pittsburgh, PA (United States)',
'FNAL':'Fermi National Accelerator Laboratory (FNAL), Batavia, \
IL (United States)',
'FEMP':'Fernald Environmental Management Project, Cincinnati, \
OH (United States)',
'HNF':'Hanford Site (HNF), Richland, WA (United States)',
'INEL':'Idaho National Engineering Laboratory (INEL), Idaho Falls, \
ID (United States)',
'INEEL':'Idaho National Engineering and Environmental Laboratory (INEEL), \
Idaho Falls, ID (United States)',
'INL':'Idaho National Laboratory (INL), Idaho Falls, ID (United States)',
'ITRI':'Inhalation Toxicology Research Institute (ITRI), Albuquerque, \
NM (United States)',
'ITLV':'International Technologies Corporation, Las Vegas, NV (United States)',
'KCP':'Kansas City Plant (KCP), Kansas City, MO (United States)',
'KAPL':'Knolls Atomic Power Laboratory (KAPL), Niskayuna, NY (United States)',
'LREH':'Laboratory of Radiobiology and Environmental Health (LREH), \
San Francisco, CA (United States)',
'LBNL':'Lawrence Berkeley National Laboratory (LBNL), Berkeley, \
CA (United States)',
'LLNL':'Lawrence Livermore National Laboratory (LLNL), Livermore, \
CA (United States)',
'LANL':'Los Alamos National Laboratory (LANL), Los Alamos, NM (United States)',
'MOUND':'Mound Plant (MOUND), Miamisburg, OH (United States)',
'NETL':'National Energy Technology Laboratory (NETL), Pittsburgh, \
PA, and Morgantown, WV (United States)',
'NIPER':'National Institute for Petroleum and Energy Research (NIPER), \
 Bartlesville, OK (United States)',
'NPTO':'National Petroleum Technology Office (NPTO), Tulsa, OK (United States)',
'NREL':'National Renewable Energy Laboratory (NREL), Golden, \
CO (United States)',
'NNES':'Navarro Nevada Environmental Services (NNES), Las Vega, \
NV (United States)',
'N-I':'Navarro-Intera, LLC (N-I), Las Vegas, NV (United States)',
'NTS':'Nevada Test Site (NTS), Mercury, NV (United States)',
'NBL':'New Brunswick Laboratory (NBL), Argonne, IL (United States)',
'NDRL':'Notre Dame Radiation Laboratory (United States)',
'ORGDP':'Oak Ridge Gaseous Diffusion Plant (K-25), Oak Ridge, \
TN (United States)',
'ORISE':'Oak Ridge Institute for Science and Education (ORISE), \
Oak Ridge, TN (United States)',
'ORNL':'Oak Ridge National Laboratory (ORNL), Oak Ridge, TN (United States)',
'Y-12':'Oak Ridge Y-12 Plant (Y-12), Oak Ridge, TN (United States)',
'PNNL':'Pacific Northwest National Laboratory (PNNL), Richland, \
WA (United States)',
'PADGDP':'Paducah Gaseous Diffusion Plant, Paducah, KY (United States)',
'PTX':'Pantex Plant (PTX), Amarillo, TX (United States)',
'PORTGDP':'Portsmouth Gaseous Diffusion Plant, Piketon, OH (United States)',
'PPPL':'Princeton Plasma Physics Laboratory (PPPL), Princeton, \
NJ (United States)',
'REHL':'Radiobiology & Environmental Health Laboratory (REHL) (United States)',
'RSL':'Remote Sensing Laboratory (RSL), Las Vegas, NV (United States)',
'RFP':'Rocky Flats Environmental Technology Site (RFP), Golden, \
CO (United States)',
'RMOTC':'Rocky Mountain Oilfield Testing Center (RMOTC), Casper, \
WY (United States)',
'SLAC':'SLAC National Accelerator Laboratory (SLAC), Menlo Park, \
CA (United States)',
'SNL-CA':'Sandia National Laboratories (SNL-CA), Livermore, CA (United States)',
'SNL-NM':'Sandia National Laboratories (SNL-NM), Albuquerque, \
NM (United States)',
'SREL':'Savannah River Ecology Laboratory (SREL), Aiken, SC (United States)',
'SRP':'Savannah River Plant (SRP), Aiken, SC (United States)',
'SRS':'Savannah River Site (SRS), Aiken, SC (United States)',
'SRTC':'Savannah River Technology Center (SRTC), Aiken, SC (United States)',
'STL':'Special Technologies Laboratory (STL), Santa Barbara, \
CA (United States)',
'S-N':'Stoller-Navarro Joint Venture (United States)',
'TJNAF':'Thomas Jefferson National Accelerator Facility (TJNAF), \
Newport News, VA (United States)',
'WIPP':'Waste Isolation Pilot Plant (WIPP), Carlsbad, NM (United States)'
}

INSPIRE_AFF_DICT = {'Argonne':'ANL',
                    'Brookhaven':'BNL',
                    'Fermilab':'FNAL',
                    'LBL, Berkeley':'LBNL',
                    'LLNL, Livermore':'LLNL',
                    'Los Alamos':'LANL',
                    'Oak Ridge':'ORNL',
                    'PNL, Richland':'PNNL',
                    'Princeton U., Plasma Physics Lab.':'PPPL',
                    'SLAC':'SLAC',
                    'Sandia':'SNL-CA',
                    'Sandia, Livermore':'SNL-NM',
                    'Jefferson Lab':'TJNAF'
}



SEARCH = "035:1422194 or 035:1434955 or 035:1434950 or \
035:1434957 or 035:1434951 or 035:1434948 or 035:1434947 ignore"

SEARCH = None

SEARCH1 = "035:15017018 or 035:15017308 or 035:784401 or 035:783404 \
or 035:804712 or 035:805567 or 035:811926 or 035:1226354 ignore"

SEARCH1a = "035:815976 or 035:816272 or 035:820745 or 035:820903 or 035:828011 or \
035:828681 or 035:825289 or 035:15011775 or 035:15011773 or \
035:15011784 or 035:15011768 or 035:15011779 ignore"

SEARCH2 = "035:939716 or 035:990844 or 035:815749 or 035:875566 or \
035:879050 or 035:892264 or 035:892333 or 035:892384 or 035:971008 or \
035:6472570 or 035:897155 or 035:993218 or 035:993216 or 035:993557 \
or 035:15017331 or 035:15011486 or 035:15020205 or 035:892513 or \
035:15017283 or 035:15020168 ignore"

SEARCH3 = "035:879160 or 035:15020356 or 035:892460 or 035:879031 or \
035:892452 or 035:892345 or 035:937252 or 035:5881220 or 035:6401803 \
or 035:5731078 or 035:878946 or 035:892287 or 035:7181 or 035:804448 \
ignore"

SEARCH4 = "035:1462102 or 035:1462101 or 035:1460566 or 035:1435932 or \
035:1435931 or 035:1468999 ignore"

SEARCH5 = "035:1434700 or 035:1434699 or 035:1434698 or 035:1433910 \
or 035:1433909 or 035:1433366 or 035:1433365 or 035:1433249 or \
035:1433248 or 035:1433247 or 035:1433215 ignore"

SEARCH = None
SEARCH = SEARCH4

SEARCH = None

