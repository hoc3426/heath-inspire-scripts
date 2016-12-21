OSTI_URL = 'https://www.osti.gov/elink/docs/2411dtd.htm'
XML_PREAMBLE  = '<?xml version="1.0" encoding="UTF-8" ?>'
XML_PREAMBLE += '<!DOCTYPE records SYSTEM "' + OSTI_URL + '">'


TYPE_DICT = {
'ANNUAL':'PD',
'BACHELORS':'TD',
'CONF':'CO',
'CRADA':'TR',
'DESIGN':'TR',
'FN':'TR',
'HABILITATION':'TD',
'INDUSTRIAL':'PD',
'MASTERS':'TD',
'MUCOOL':'TR',
'PLAN':'PD',
'PROPOSAL':'TR',
'PUB':'JA',
'REVIEW':'PD',
'THESIS':'TD',
'TM':'TR',
'VLHCPUB':'TR'
}

DIRECTORY = '/afs/cern.ch/project/inspire/TEST/hoc/osti/'

ACCEPTED_SEARCH = '8564_z:openaccess or 8564_z:postprint or \
8564_y:"article from scoap3" ignore'

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
'BAPL':'Bettis Atomic Power Laboratory (BAPL), West Mifflin, PA (United States)',
'BNL':'Brookhaven National Laboratory (BNL), Upton, NY (United States)',
'DRI':'Desert Research Institute (DRI), Nevada System of Higher Education, Reno,NV (United States)',
'ETTP':'East Tennessee Technology Park (ETTP), Oak Ridge, TN (United States)',
'ETEC':'Energy Technology Engineering Center (ETEC), Canoga Park, CA (United States)',
'EML':'Environmental Measurements Laboratory (EML), New York, NY (United States)',
'FETC-MGN':'Federal Energy Technology Center-Morgantown (FETC-MGN), Morgantown, WV (United States)',
'FETC-PGH':'Federal Energy Technology Center-Pittsburgh (FETC-PGH), Pittsburgh, PA (United States)',
'FNAL':'Fermi National Accelerator Laboratory (FNAL), Batavia, IL (United States)',
'FEMP':'Fernald Environmental Management Project, Cincinnati, OH (United States)',
'HNF':'Hanford Site (HNF), Richland, WA (United States)',
'INEL':'Idaho National Engineering Laboratory (INEL), Idaho Falls, ID (United States)',
'INEEL':'Idaho National Engineering and Environmental Laboratory (INEEL), Idaho Falls, ID (United States)',
'INL':'Idaho National Laboratory (INL), Idaho Falls, ID (United States)',
'ITRI':'Inhalation Toxicology Research Institute (ITRI), Albuquerque, NM (United States)',
'ITLV':'International Technologies Corporation, Las Vegas, NV (United States)',
'KCP':'Kansas City Plant (KCP), Kansas City, MO (United States)',
'KAPL':'Knolls Atomic Power Laboratory (KAPL), Niskayuna, NY (United States)',
'LREH':'Laboratory of Radiobiology and Environmental Health (LREH), San Francisco, CA (United States)',
'LBNL':'Lawrence Berkeley National Laboratory (LBNL), Berkeley, CA (United States)',
'LLNL':'Lawrence Livermore National Laboratory (LLNL), Livermore, CA (United States)',
'LANL':'Los Alamos National Laboratory (LANL), Los Alamos, NM (United States)',
'MOUND':'Mound Plant (MOUND), Miamisburg, OH (United States)',
'NETL':'National Energy Technology Laboratory (NETL), Pittsburgh, PA, and Morgantown, WV (United States)',
'NIPER':'National Institute for Petroleum and Energy Research (NIPER), Bartlesville, OK (United States)',
'NPTO':'National Petroleum Technology Office (NPTO), Tulsa, OK (United States)',
'NREL':'National Renewable Energy Laboratory (NREL), Golden, CO (United States)',
'NNES':'Navarro Nevada Environmental Services (NNES), Las Vega, NV (United States)',
'N-I':'Navarro-Intera, LLC (N-I), Las Vegas, NV (United States)',
'NTS':'Nevada Test Site (NTS), Mercury, NV (United States)',
'NBL':'New Brunswick Laboratory (NBL), Argonne, IL (United States)',
'NDRL':'Notre Dame Radiation Laboratory (United States)',
'ORGDP':'Oak Ridge Gaseous Diffusion Plant (K-25), Oak Ridge, TN (United States)',
'ORISE':'Oak Ridge Institute for Science and Education (ORISE), Oak Ridge, TN (United States)',
'ORNL':'Oak Ridge National Laboratory (ORNL), Oak Ridge, TN (United States)',
'Y-12':'Oak Ridge Y-12 Plant (Y-12), Oak Ridge, TN (United States)',
'PNNL':'Pacific Northwest National Laboratory (PNNL), Richland, WA (United States)',
'PADGDP':'Paducah Gaseous Diffusion Plant, Paducah, KY (United States)',
'PTX':'Pantex Plant (PTX), Amarillo, TX (United States)',
'PORTGDP':'Portsmouth Gaseous Diffusion Plant, Piketon, OH (United States)',
'PPPL':'Princeton Plasma Physics Laboratory (PPPL), Princeton, NJ (United States)',
'REHL':'Radiobiology & Environmental Health Laboratory (REHL) (United States)',
'RSL':'Remote Sensing Laboratory (RSL), Las Vegas, NV (United States)',
'RFP':'Rocky Flats Environmental Technology Site (RFP), Golden, CO (United States)',
'RMOTC':'Rocky Mountain Oilfield Testing Center (RMOTC), Casper, WY (United States)',
'SLAC':'SLAC National Accelerator Laboratory (SLAC), Menlo Park, CA (United States)',
'SNL-CA':'Sandia National Laboratories (SNL-CA), Livermore, CA (United States)',
'SNL-NM':'Sandia National Laboratories (SNL-NM), Albuquerque, NM (United States)',
'SREL':'Savannah River Ecology Laboratory (SREL), Aiken, SC (United States)',
'SRP':'Savannah River Plant (SRP), Aiken, SC (United States)',
'SRS':'Savannah River Site (SRS), Aiken, SC (United States)',
'SRTC':'Savannah River Technology Center (SRTC), Aiken, SC (United States)',
'STL':'Special Technologies Laboratory (STL), Santa Barbara, CA (United States)',
'S-N':'Stoller-Navarro Joint Venture (United States)',
'TJNAF':'Thomas Jefferson National Accelerator Facility (TJNAF), Newport News, VA (United States)',
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




#This search is for a project Mary is working on where
#OSTI said they didn't have the full-text.
SEARCH = "fin r FERMILAB-CONF-16-015-ND or \
FERMILAB-CONF-15-319-E or \
FERMILAB-CONF-15-637-AD or \
FERMILAB-CONF-15-167-APC or \
FERMILAB-CONF-15-525-ND 1512 or \
FERMILAB-CONF-15-446-AD-APC or \
FERMILAB-CONF-15-528-CD or \
FERMILAB-CONF-15-470-PPD or \
FERMILAB-CONF-15-532-APC or \
FERMILAB-CONF-15-558-ND-PPD or \
FERMILAB-CONF-15-238-TD or \
FERMILAB-CONF-15-120-ND \
ignore"

SEARCH = None

SEARCH = "035:1244508 \
or 035:1234899 \
or 035:1322155 \
or 035:1322156 \
or 035:1327017 \
or 035:1249522 \
or 035:1249524 \
or 035:1250476 \
or 035:1250478 \
or 035:1250482 \
or 035:1250488 \
or 035:1250493 \
or 035:1250806 \
or 035:1250808 \
or 035:1250815 \
or 035:1250821 \
ignore"

SEARCH = "035:1244501 \
or 035:1244503 \
or 035:1244504 \
or 035:1244506 \
or 035:1244512 \
or 035:1244514 \
or 035:1253588 \
or 035:1260393 \
or 035:1288739 \
or 035:1288740 \
or 035:1288742 \
or 035:1288743 \
or 035:1288745 \
or 035:1288746 \
or 035:1288750 \
or 035:1288741 \
or 035:1289924 \
or 035:1289927 \
or 035:1289928 \
or 035:1289930 \
or 035:1289931 \
or 035:1289932 \
or 035:1289933 \
or 035:1289934 \
or 035:1244500 \
or 035:1294439 \
or 035:1294440 \
or 035:1294442 \
or 035:1294443 \
or 035:1294444 \
or 035:1294445 \
or 035:1294446 \
or 035:1294447 \
or 035:1294448 \
or 035:1294449 \
or 035:1294450 \
or 035:1294510 \
ignore"

SEARCH = "035:1244501 \
or 035:1244503 \
or 035:1244504 \
or 035:1244506 \
or 035:1244512 \
or 035:1244514 \
or 035:1253588 \
or 035:1288739 \
or 035:1288740 \
or 035:1288742 \
or 035:1288743 \
or 035:1288745 \
or 035:1288746 \
or 035:1288750 \
or 035:1288741 \
or 035:1244500 \
ignore"


SEARCH = None

