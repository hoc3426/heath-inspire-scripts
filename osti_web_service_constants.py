"""
Input for the osti_web_service.py script.
"""

from osti_web_service_constants_local import DIRECTORY

OSTI_URL = 'https://www.osti.gov/elink/docs/2411dtd.htm'
XML_PREAMBLE  = '<?xml version="1.0" encoding="UTF-8" ?>'
XML_PREAMBLE += '<!DOCTYPE records SYSTEM "' + OSTI_URL + '">'

'''
PRODUCT SUB-TYPE CODES
Code	Definition
A	Conference Paper
R	Conference Presentation (may receive a DOI)
O	Conference Poster (may receive a DOI)
P	Conference Proceedings

EXAMPLE CONFERENCE SUBTYPE

<records>
    <record>
        <!-- specify conference presentation metadata type -->
        <product_type product_subtype="R">CO</product_type>
        <!-- additional required metadata -->
    </record>
</records> 
'''


ENDING_COUNTER = 200

TYPE_DICT = {
'ANNUAL':'PD',
'BACHELORS':'TD',
'BOOK':'B',
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
'MICROBOONE':'TR',
'MUCOOL':'TR',
'PLAN':'PD',
'POSTER':'CO.O',
'PROPOSAL':'TR',
'PUB':'JA',
'REVIEW':'PD',
'SLIDES':'CO.R',
'THESIS':'TD',
'TM':'TR',
'VLHCPUB':'TR'
}

ACCEPTED_SEARCH = '8564_z:openaccess or 8564_z:postprint or \
8564_y:"article from scoap3" or 8564_y:"Fulltext from Publisher" \
0247_2:doi ignore'

ACCEPTED_SEARCH = '8564_y:"fermilab accepted manuscript" or \
8564_y:"open access fulltext" or 8564_y:"article from scoap3" or \
8564_y:"Fulltext from Publisher" 0247_2:doi ignore'


DADD_SEARCH = 'dadd:2012 or dadd:2013 or dadd:2014 or \
dadd:2015 or dadd:2016 or dadd:2017 or dadd:2018 or dadd:2019 or dadd:2020 \
-037__a:fermilab-code-*'

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

SEARCH6 = "035:1433215 or 035:1433247 or 035:1433248 or 035:1433249 \
or 035:1433365 or 035:1433366 or 035:1433909 or 035:1433910 \
or 035:1434698 or 035:1434699 or 035:1434700 or 035:1435931 \
or 035:1435932 ignore"

SEARCH7a = "find recid 1695806 \
or recid 1644100 \
or recid 1694473 \
or recid 1698421 \
or recid 1639208 \
or recid 1646260 \
or recid 1674951 \
or recid 1511868 \
or recid 1674549 \
or recid 1614453 \
or recid 1682779 \
or recid 1667734 \
or recid 1589842 \
or recid 1647350 \
or recid 446416 \
or recid 1695800 ignore"

SEARCH7b = "find recid 1631982 \
or recid 1634835 \
or recid 418647 \
or recid 1651149 \
or recid 1662307 \
or recid 1653680 \
or recid 1658447 \
or recid 1634843 \
or recid 1637327 \
or recid 1681439 \
or recid 1497146 \
or recid 440246 \
or recid 1515694 \
or recid 1277057 \
or recid 1623908 ignore"

SEARCH7c = "find recid 1647947 \
or recid 1681436 \
or recid 1666884 \
or recid 1508173 \
or recid 1604886 \
or recid 1472120 \
or recid 1601359 \
or recid 1630635 \
or recid 1702546 \
or recid 1594909 \
or recid 1508017 \
or recid 1631985 \
or recid 1654360 \
or recid 1481372 \
or recid 1676131 ignore"

SEARCH7d = "find recid 1594731 \
or recid 1666824 \
or recid 1507168 \
or recid 1650106 \
or recid 1684240 \
or recid 1689428 \
or recid 1513361 \
or recid 1685235 \
or recid 1459227 \
or recid 1635821 \
or recid 1685532 \
or recid 1685232 \
or recid 1512112 \
or recid 1593762 \
or recid 1680459 ignore"

SEARCH7e = "find recid 1668914 \
or recid 1682023 \
or recid 1700756 \
or recid 1636197 \
or recid 1635896 \
or recid 445214 \
or recid 1614779 \
or recid 1682776 \
or recid 1678111 \
or recid 1672072 \
or recid 1679804 \
or recid 1650785 \
or recid 1692399 \
or recid 1488626 \
or recid 1664547 ignore"

SEARCH7f = "find recid 1663566 \
or recid 1509984 \
or recid 1616054 \
or recid 1666015 \
or recid 1670997 \
or recid 1664621 \
or recid 1703224 \
or recid 1679268 \
or recid 1678715 \
or recid 444764 \
or recid 448756 \
or recid 1629160 \
or recid 1671087 \
or recid 109189 \
or recid 1647428 \
or recid 1695389 \
or recid 1601294 ignore"

SEARCH = None

SEARCH = "001:1472120 or 001:1713703 or 001:1742585 ignore"

SEARCH = None

