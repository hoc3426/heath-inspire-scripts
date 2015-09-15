import re 
from titlecase import titlecase 
from invenio.search_engine import perform_request_search 
from invenio.search_engine import get_fieldvalues

VERBOSE = True
VERBOSE = False

words = ['AND', 'AROUND', 'FOR', 'FROM', 'IN', 'OF', 'THE', 'WITH']  

acronyms = ['AdS', 'ADC','AGN', 'AGS', 'ALICE', 'ATLAS', 'BaBar', 'BCS','BEBC',
              'BELLE', 'BH', 'BL', 'BNL', 'BPM', 'BPS', 'BRS','BRST', 
              'CAMAC','CDF', 'CDM', 'CEBAF', 'CERN', 'CESR', 'CFT', 'CKM', 
              'CLEO', 'CLIC', 'CM', 'CMB', 'CMS', 'CP', 'CPT', 'CPV', 
              'DAPHNE', 'DAQ','DC', 'DELPHI', 'DESY', 'DIS','DTU', 'EAS','ECFA',
              'EDM', 'EFT','EMC', 'EOS', 'EW', 'EWSB', 'FEL', 'FCNC', 'Fermilab',
              'GEM', 'GeV', 'GHZ', 'GR', 'GRB', 'GUT', 'GUTs','HERA', 'HERMES', 'HST',
              'ICFA', 'IHEP','II', 'III', 'IV', 'ILC',
              'IR', 'IRAS', 'ISM', 'ISR', 'IV', 'IX','JINR','KdV', 'KEK', 'KEKB','KNO', 'LAr','LAMPF','LAT',
              'LC','LEAR', 'LEP', 'LGT', 'LHC', 'LHCb', 'LINAC', 'LISA','LLNL', 'LMC', 'LQCD', 'LSS',
              'MACSYMA','MAGIC', 'MC', 'MeV', 'MHD', 'MIT', 'MR', 'MSSM', 'NAL', 'NC', 'NCG', 'NGC', 'NJL',
              'NLC', 'NLO', 'NP','OBE', 'OZI','PCAC', 'PEP', 'PETRA', 'PHENIX', 'PPP', 'PQCD',
              'QCD', 'QED', 'QFT', 'QGP', 'QH', 'QM', 'QSO', 'RED', 
              'RF', 'RFQ', 'RG', 'RHIC', 'SDC', 'SDSS', 'SGR', 'SLAC', 'SLC',
              'SM', 'SMC', 'SN','SN1987A', 'SNR', 'SNS','SPEAR', 'SPS', 'SRF', 'SSB', 'SSC', 
              'SSM', 'SUGRA', 'SUSY', 'SUSYM', 'SYM', 'TOF', 'TPC', 'TRIUMF',
              'UHE', 'UHECR', 'USA', 'UV', 'VCS', 'VHE', 'VI', 'VII', 'VIII', 'WIMP', 'WKB','WMAP','XXZ',
              'WZW', 'WZNW','XY', 'Yang-Mills','ZEUS',
'Adler-Bell-Jackiw',
'Aharonov-Bohm',
'Bethe-Heitler',
'Bethe-Salpeter',
'Bogomolny-Prasad-Sommerfield',
'Born-Infeld',
'Bose-Einstein',
'Cabibbo-Kobayashi-Maskawa',
'Calabi-Yau',
'Chern-Simons',
'Coleman-Weinberg',
'Drell-Yan',
'Einstein-Podolsky-Rosen',
'Feynman-Hellmann',
'Feynman-Kac',
'Fokker-Planck',
'Friedmann-Robertson-Walker',
'Gauss-Bonnet',
'Goldberger-Treiman',
'Gross-Neveu',
'Hamilton-Jacobi',
'Hartree-Fock',
'Hooft-Polyakov'
'Hooft-Veltman',
'Kac-Moody',
'Kaluza-Klein',
'Kerr-Newman',
'Klein-Gordon',
'Kobayashi-Maskawa',
'Kogut-Susskind',
'Nambu-Goldstone',
'Nambu-Jona-Lasinio',
'Pati-Salam',
'Peccei-Quinn',
'Reissner-Nordstrom',
'Robertson-Walker'
'Robertson-Walker',
'Sine-Gordon',
'Slavnov-Taylor',
'Thomas-Fermi',
'Weinberg-Salam',
'Wess-Zumino-Novikov-Witten',
'Wess-Zumino-Witten',
'Wess-Zumino',
'Wu-Yang',
'Yang-Baxter',
'Zweig-Okubo-Iizuka',
]

particles = ['alpha','b','B','B0','c','chi','cos','d','D','DELTA','e','E','epsilon','EPSLION','eta','ETA',
               'g','G','gamma','GAMMA','H','H0','J','K','K0','l',
              'l','lambda','LAMBDA','LAMBDA0','lepton','mu','n','N','nu','omega','OMEGA','p','P','phi','pi0','pi', 'pp',
              'psi','Q','q','rho','rho0','s','SIGMA','SIGMA0','Sigma','Sigma0','sigma','sin','T', 'tau',
              'theta','Theta','u','UPSILON','V','W','XI','Xi','Z','z','Z0']


def titleFix_case(x):

  x = re.sub(r'[sS]\*\*\(1\/2\)\s*=\s*(\d+)',r'$\\9sqrt{ssss}=\1$',x)
  x = re.sub(r'[sS]\*\*\(1\/2\)',r'$\\9sqrt{ssss}$',x)
  #particles that are always lower case
  for z in ['ALPHA','E','ETA','GAMMA','MU','PHI','PI','PSI','RHO','THETA']:
    y = "\\b" + z  + "\\b"
    y0 = "\\b" + z  + "0"
    yy = z.lower()
    yy0 = z.lower()  + "0"
    x = re.sub(y0,yy0,x)
    x = re.sub(y,yy,x)
  #The elements
  
  elements = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar',
            'K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se',
            'Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn',
            'Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy',
            'Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi',
            'Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es',
            'Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Uut','Fl','Uup','Lv','Uus','Uuo']
  for e in elements:
    x = re.sub("\\b" + e.upper() + "\-(\d+)",r'$^{\1}$protectedchemicalelement' + e + 'protectedchemicalelement',x)
    x = re.sub("\\b" + e + "\-(\d+)",r'$^{\1}$protectedchemicalelement' + e + 'protectedchemicalelement',x)

  #Convert subscript underscores to latex
  if re.search(r'\_', x):
      x = re.sub(r' (\S+)\_(\S*\w)([\s\,\:])', r' $\1_\2$\3', x)
      x = re.sub(r'\$\$', r'$', x)

  #Set up case protection for particles
  particleCase = {}
  for particle in particles:
    y = "\\b" + particle + "\\b" 
    yp = "\\b" + particle + "\'"
    ypp = "\\b" + particle + "\'\'"
    zp = particle + "-prime"
    zpp = particle + "-pprime"
    x = re.sub(ypp,zpp,x)
    x = re.sub(yp,zp,x)
    if re.search("[A-Z]",particle): 
      particleCase[particle] = "999particlebig" + particle.lower()
    else:
      particleCase[particle] = "999particlesmall" + particle
    x = re.sub(y,particleCase[particle],x)
  
  #Lower because everything is in CAPS and titlecase() won't work on it.
  x = x.lower()
  #OK, now look for select group of acronyms
  for acronym in acronyms:
    y = "\\b" + acronym.lower() + "\\b" 
    x = re.sub(y,"{" + acronym + "}", x)
  #x = re.sub("anti\-","anti- ",x)

  x = titlecase(x) 
  #Now convert particles from particlebig and particlesmall back to proper form
  for particle in particles:
    y = "\\b" + particleCase[particle] + "\\b" 
    antiParticle1 = "\\bAnti\-" + particleCase[particle] 
    if re.search("[A-Z][A-Z]",particle): 
      particle = titlecase(particle.lower())
    if particle == "lepton" or particle == "l":
       particle = r'\\ell'
    elif len(particle) > 1 and particle != "K0":
      particle = r'\\' + particle
    particle = re.sub(r'0',r'XXXX',particle)
    antiParticle2 = r'$\\bar{' + particle + "}$"
    x = re.sub(antiParticle1,antiParticle2,x)
    x = re.sub(y,"$" + particle + "$", x)
    x = re.sub(r' \$'+particle+'\$ \((\d+)\) ',r' $YYYYYYY(\1)$ ',x)
    x = re.sub(r'YYYYYYY',particle,x)
  x = re.sub(r'XXXX',r'^0',x)
  #UNDO x = re.sub(r's\*\*\(1\/2\)\s*=\s*(\d+)',r'$\\sqrt{ssss}=\1$',x)
  x = re.sub(r'ssss',r's',x)
  x = re.sub(r'9sqrt',r'sqrt',x)
  x = re.sub(r'\b(\d+)\*\*(\d+)\b',r'$\1^{\2}$',x)
  x = re.sub(r'\bR\*\*(\d+)\b',r'$R^{\1}$',x)
  x = re.sub(r'So\(',r'SO(',x)
  x = re.sub(r'Su\(',r'SU(',x)
  x = re.sub(r'SU\(n\)',r'SU($N$)',x)
  x = re.sub(r'O\(n\)',r'O($N$)',x)
  x = re.sub(r'\<\-+\>',r' $\\leftrightarrow$ ',x) 
  x = re.sub(r'\-+\>',r' $\\to$ ',x)
  x = re.sub(r'\$\+\-',r'^\\pm$',x)
  x = re.sub(r'\$\-\+',r'^\\mp$',x)
  x = re.sub(r'\$\+\+','^{++}$',x)
  x = re.sub(r'\$\+','^+$',x)
  x = re.sub(r'([A-z])\$\-',r'\1^-$',x)
  x = re.sub(r'\$\*\*(\d+)',r'^\1$',x)
  x = re.sub(r'\$\*','^*$',x)
  x = re.sub(r'\$e\$(\(\d+\))',r'$E\1$',x)
  x = re.sub(r'\$u\$(\(\d+\))',r'$U\1$',x)
  x = re.sub(r'\$N\$(\=\d+)',r'$N\1$',x)
  x = re.sub(r'\$\\Delta\$ ([A-Z]) (\=\s*[\d\/]+)',r'$\\Delta \1 \2$',x)
  x = re.sub(r'-?\\theta\^\-\$w',r'\\theta_W$',x)
  x = re.sub(r'\$p\$\(t\)',r'$p_T$',x)
  x = re.sub(r'\$P\$\(\$T\$\)',r'$p_T$',x)
  x = re.sub(r'\$K\^0\$\(s\)',r'$K^0_S$',x)
  x = re.sub(r'\$K\^0\$\(l\)',r'$K^0_L$',x)
  x = re.sub(r'\$K\$\(s\)',r'$K_S$',x)
  x = re.sub(r'\$K\$\(l\)',r'$K_L$',x)
  x = re.sub(r'\$\\Sigma\$ Model',r'$\sigma$ Model',x)
  x = re.sub(r'\^\-\$dimen','$-dimen',x)
  x = re.sub(r'\^\-\$pprime',r'^{\\prime\\prime}$',x)
  x = re.sub(r'\^\-\$prime',r'^\\prime$',x)
  x = re.sub(r'[Aa]nti\-[eE]lectron\-neutrino',r'$\\bar{\\nu}_e$',x)
  x = re.sub(r'[Aa]nti\-[mM]uon\-neutrino',r'$\\bar{\\nu}_\\mu$',x)
  x = re.sub(r'[Aa]nti\-[tT]au\-neutrino',r'$\\bar{\\nu}_\\tau$',x)
  x = re.sub(r'[eE]lectron\-neutrino',r'$\\nu_e$',x)
  x = re.sub(r'[mM]uon\-neutrino',r'$\\nu_\\mu$',x)
  x = re.sub(r'[tT]au\-neutrino',r'$\\nu_\\tau$',x)
  x = re.sub(r'(\\?[emuta]+)\^\-\$neutrino',r'$\\nu_\1$',x)
  x = re.sub(r'\$?(\\?[emuta]+)\$\s*Neutrino',r'$\\nu_\1$',x)
  x = re.sub(r'\$N\$\(\$c\$\)',r'$N_c$',x) 
  x = re.sub(r'\$g\^\-\$2',r'$g-2$',x)
  #x = re.sub(r'Anti\-(\w+)',r'$\\bar{\1}$',x) 
  x = re.sub(r'\'\$T\$',r"'t",x) 
  x = re.sub(r"\'t \{Hooft",r"{'t Hooft",x)
  x = re.sub(r"\'T Hooft",r"'t Hooft",x) 
  x = re.sub(r"\{CP\}\(?\*\*\(?\$[Nn]\^\-\$1\)",r"{CP}$^{(N-1)}$",x) 
  x = re.sub(r"\{CP\}\*\*\(\$\^\{1\}\$N\)",r"{CP}$^{(N-1)}$",x)
  x = re.sub(r"\{CP\}\*\*\$N\$",r"{CP}$^{N}$",x)
  x = re.sub(r"SU\(2\)-l X U\(1\)",r"SU(2)$_L \\times$ U(1)",x)
  x = re.sub(r"SU\(2\)-l X SU\(1\)-r",r"SU(2)$_L \\times$ SU$_R$(1)",x)
  x = re.sub(r"SU\(\$N\^\+\$1\)",r"SU($N+1$)",x)
  x = re.sub(r"\$s\$ Matrix",r"$S$ Matrix",x) 
  x = re.sub(r'\$\\eta\$\(\$(\w)\$\)',r'$\\eta_c$',x)
  x = re.sub(r'\$\\gamma\^\-\$ray',r'gamma-ray',x)
  x = re.sub(r'R+r\*\*2','$R+R^2$',x)
  x = re.sub(r'&',r' and ',x) 
  x = re.sub(r'\$(\s*)\(\s*\$',r'\1(',x)
  x = re.sub(r'\s*\<\=\s*',r' $\\le$ ',x)
  x = re.sub(r'\s*\>\=\s*',r' $\\ge$ ',x)
  x = re.sub(r'\$\s*=\s*(\d+)',r'=\1$',x) 
  x = re.sub(r'\$\s*\$',' ',x)
  x = re.sub(r'\$(\s*)([\/\=\-\+\d]+)(\s*)\$',r'\1\2\3',x)
  x = re.sub(r'\s+',' ',x)
  x = re.sub(r'J \/ \\psi',r'J/\\psi',x)
  for e in elements:
    lower = 'protectedchemicalelement' + e.lower() + 'protectedchemicalelement'
    x = re.sub(lower,e,x)
  return x

particles_greek = ['alpha', 'beta', 'chi', 'gamma', 'delta', 'epsilon', 'eta',
                  'nu', 'pi', 'psi', 'sigma', 'Sigma']

def titleFix(x):
    if re.search(r'V\_([udstbc]{2})', x):
        x = re.sub(r'V\_([udstbc]{2})', r'$V_{\1}$', x)
    elif re.search(r'([sS])\_([nN]{2})', x):
        x = re.sub(r'([sS])\_([nN]{2})', r'$\1_{\2}$', x)
    elif re.search(r'\_', x) or re.search(r'\^', x):
        x = re.sub(r'^(\S+)([\_\^])(\S+)', r'$\1\2\3$', x)
        x = re.sub(r'(\S+)([\_\^])(\S+)$', r'$\1\2\3$', x)
        x = re.sub(r'(\S+)([\_\^])(\S+)([\, ])', r'$\1\2\3$\4', x)
    x = re.sub(r' \-?\-\> ', r' $\\to$ ', x)
    for acronym in acronyms:
        y = "\\b" + acronym + "\\b"
        x = re.sub(y, "{" + acronym + "}", x)
        y = "{{" + acronym + "}}"  
        x = re.sub(y, "{" + acronym + "}", x)
    for particle in particles:    
        initial = "\\b" + particle + "\\b"
        if particle == r'l':
            particle = r'\\ell'
        elif particle in particles_greek:
            particle = r'\\' + particle
        #elif particle == r'nu':
        #    particle = r'\\nu'
        #elif particle == r'pi':
        #    particle = r'\\pi'
        final = r"$" + particle + r"$"
        #print particle, y, z, x
        x = re.sub(initial, final, x)
        #print particle, y, z, x
    x = re.sub(r'\$\s*\/\s*\$', r'/', x)
    x = re.sub(r'\$\s*\$', r' ', x)
    x = re.sub(r'[ ]+', r' ', x)
    return x

#search = '961__x:1980-1*'
#search = '961__x:1993-* and topcite 5+'
#search = 'find t An Isobar Model Partial Wave Analysis'
#search="find recid 9189 or 9208 or 153191 or 152935"
#search="find recid 24937"
#search = 'find date 2013 and recid:1255928->99999999'
#search = '037__a:fermilab-thesis* -245__a:/\$/'
#search = 'refersto:author:Giorgio.Bellettini.1 245__a:/\\pi/ -245__a:/\$/'
#search = '001:1339902'
#x = perform_request_search(p=search,cc='HEP')
search = '119__a:FNAL*'
if VERBOSE: print search
x = perform_request_search(p=search,cc='Experiments')
if VERBOSE: print search, len(x)
title = 'Meas alpha f the chi_c and chi_b quarkonium states in pp collisions with the ATLAS experiment'
print "<?xml version=\"1.0\" ?>"
print "<collection>"

iter_flag = 1
for r in x:
  if VERBOSE: print r, iter_flag
  title = get_fieldvalues(r,'245__a')[0]
  if re.search(r'[aeiou]', title):
      continue
  if iter_flag > 50:
      continue
  oldTitle = title
  oldTitle = re.sub(r'&',r' and ',oldTitle) 
  oldTitle = re.sub(r'\s+',' ',oldTitle)
  for word in words:
    wordCheck = "\\b" + word + "\\b" 
    #if re.search(wordCheck,title):
    if title:     
      iter_flag += 1
      title = titleFix_case(title)
      print '<record>'
      print '  <controlfield tag="001">'+str(r)+'</controlfield>'
      print '  <datafield tag="245" ind1=" " ind2=" ">'
      print '    <subfield code="a">' + title + '</subfield>'
      print '  </datafield>'
      #print '  <datafield tag="246" ind1=" " ind2=" ">'
      #print '    <subfield code="a">' + oldTitle + '</subfield>'
      #print '  </datafield>' 
      print '</record>'
      break
print "</collection>"  

