"""
Script for getting records from ADS and adding any missing information to the
corresponding records in INSPIRE.
http://ads.harvard.edu/pubs/arXiv/ADSmatches.xml
http://ads.harvard.edu/pubs/arXiv/ADSmatches_updates.xml

"""

from invenio.search_engine import perform_request_search
from invenio.bibrecord import print_rec, record_add_field

import xml.etree.ElementTree as ET
import re

VERBOSE = 1
DEBUG = 0

#DOCUMENT = 'ADSmatches_updates.xml'
#DOCUMENT = 'ADS_astro2.xml'
#DOCUMENT = 'ADS_cond.xml'
#DOCUMENT = 'ADS_math.xml'
DOCUMENT = 'ADSmatches.xml'
#DOCUMENT = 'tmp.xml'

BADRECS = [1299943, 1263270, 782224, 799038, 834458]
#INPUT_COUNTER = 66885
#INPUT_COUNTER = 891510
#INPUT_COUNTER = 79900
INPUT_COUNTER = 1
OUTPUT_COUNTER = 501

JOURNAL_DICT = {
    'Acta.':'Acta Astron.',
    'Adv.Space.':'Adv.Space Res.',
    'AIP.':'AIP Conf.Proc.',
    'Annales':'Annales Henri Poincare',
    'Annals':'Annals Phys.',
    'ASP.':'ASP Conf.Ser.',
    'ASSL':'Astrophys.Space Sci.Libr.',
    'Astron.Nachr.':'Astron.Nachr.',
    'Astroph.J.':'Astrophys.J.',
    'Astrophys.Space.':'Astrophys.Space Sci.',
    'Baltic.':'Baltic Astron.',
    'Comm.Math.Phys.':'Commun.Math.Phys.',
    'Commun.Nonlinear.':'Commun.Nonlinear Sci.Numer.Simul.',
    'Contrib.Astron.Obs.Skalnate.':'Contrib.Astron.Obs.Skalnate Pleso',
    'EAS.Pub.Ser.':'EAS Publ.Ser.',
    'ESA.':'ESA Spec.Publ.',
    'Geophys.Astrophys.Fluid.':'Geophys.Astrophys.Fluid Dynamics',
    'Gravitat.Cosmol.':'Grav.Cosmol.',
    'IAU.':'IAU Symp.',
    'J.Fluid.':'J.Fluid Mech.',
    'J.Nonlin.Mathematical':'J.Nonlin.Mathematical Phys.',
    'Lect.Notes.':'Lect.Notes Phys.',
    'Low.':'Low Temp.Phys.',
    'New.':'New J.Phys.',
    'Phys.Rev.L.':'Phys.Rev.Lett.',
    'Proc.SPIE.':'Proc.SPIE Int.Soc.Opt.Eng.',
    'Res.Astron.Astroph.':'Res.Astron.Astrophys.',
    'Sov.Phys.JETP.Lett.':'JETP Lett.',
    'A&A':'Astron.Astrophys.',
    'A&ARv':'Astron.Astrophys.Rev.',
    'A&AS':'Astron.Astrophys.Suppl.Ser.',
    'A&AT':'Astron.Astrophys.Trans.',
    'A&G':'Astron.Geophys.',
    'AAS':'Amer.Astron.Soc.Meeting',
    'AcA':'Acta Astron.',
    'AcAau':'Acta Astronaut.',
    'AcApS':'Acta Astrophys.Sin.',
    'AcASn':'Acta Astron.Sin.',
    'AcC':'Acta Cosmologica',
    'AcEle':'Acta Electron.',
    'AcHPh':'Helv.Phys.Acta',
    'AcMec':'Acta Mech.',
    'AcMet':'Acta Metall.',
    'AcNum':'Acta Numer.',
    'AcOpt':'Opt.Acta',
    'AcPhA':'Acta Phys.Austriaca',
    'AcPhH':'Acta Phys.Hung.',
    'AcPSl':'Acta Phys.Slov.',
    'AcPSn':'Acta Phys.Sin.',
    'AcRhe':'Rheologica Acta',
    'ACSJ':'J.Amer.Ceramic Soc.',
    'AcSpe':'Spectrochim.Acta A',
    'AdA&A':'Adv.Astron.Astrophys.',
    'AdApM':'Adv.Appl.Math.',
    'adndt':'Atom.Data Nucl.Data Tabl.',
    'AdPhy':'Adv.Phys.',
    'AdSpR':'Adv.Space Res.',
    'AeJ':'J.Aeron.Sci.',
    'AExpr':'Astron.Express',
    'Afz':'Astrofiz.',
    'AIAAJ':'AIAA J.',
    'AIChE':'Aiche J.',
    'AIPC':'AIP Conf.Proc.',
    'AJ':'Astron.J.',
    'AJSE':'Arabian J.Sci.Eng.',
    'AmJPh':'Am.J.Phys.',
    'AmJS':'Am.J.Sci.',
    'AmMin':'Amer.Miner.',
    'AmSci':'Am.Sci.',
    'AN':'Astron.Nachr.',
    'AnaCh':'Anal.Chem.',
    'AnAp':'Annales Astrophys.',
    'AnGeo':'Ann.Geophys.',
    'AnIPS':'Annals Israel Phys.Soc.',
    'AnP':'Annalen Phys.',
    'AnPh':'Annales Phys.(France)',
    'AnPhy':'Annals Phys.',
    'AnRFM':'Ann.Rev.Fluid Mech.',
    'Ap':'Astrophysics',
    'Ap&SS':'Astrophys.Space Sci.',
    'ApEnM':'Appl.Envir.Microbiol.',
    'APh':'Astropart.Phys.',
    'ApJ':'Astrophys.J.',
    'ApJS':'Astrophys.J.Suppl.',
    'ApL':'Astrophys.Lett.',
    'ApL&C':'Astrophys.Lett.Commun.',
    'ApMaL':'Appl.Math.Lett.',
    'ApMaO':'Appl.Math.Optim.',
    'ApMM':'Appl.Math.Mech.',
    'ApMRv':'Appl.Mech.Rev.',
    'ApNM':'Appl.Numer.Math.',
    'ApNr':'Astrophys.Nor.',
    'ApOpt':'Appl.Opt.',
    'AppAn':'Appl.Anal.',
    'ApPhB':'Appl.Phys.B, Lasers Opt.',
    'ApPhL':'Appl.Phys.Lett.',
    'ApPhy':'Appl.Phys.',
    'ApPPL':'Appl.Phys.B Photophys.Laser Chem.',
    'ApScR':'Appl.Sci.Res.',
    'ApSpe':'Appl.Spectrosc.',
    'ApSS':'Appl.Surf.Sci.',
    'ApSup':'IEEE Trans.Appl.Supercond.',
    'ArA':'Ark.Mat.Astron.Fys.',
    'ARA&A':'Ann.Rev.Astron.Astrophys.',
    'ArApM':'Arch.Appl.Mech.',
    'ARep':'Astron.Rep.',
    'AREPS':'Ann.Rev.Earth Planet.Sci.',
    'arnps':'Ann.Rev.Nucl.Part.Sci.',
    'ArRMA':'Arch.Ration.Mech.Anal.',
    'ASAJ':'J.Acoust.Soc.Am.',
    'ASPC':'ASP Conf.Ser.',
    'AstBu':'Astrophys.Bull.',
    'AtERv':'At.Energy Rev.',
    'ATJFE':'J.Fluids Eng.',
    'AtO':'Atmos. Ocean Opt.',
    'AuJPh':'Austral.J.Phys.',
    'AuMSJ':'J.Austral.Math.Soc.Ser.B',
    'Autom':'Automatica',
    'AZh':'Astron.Zh.',
    'BAAA':'Bol.A.A.Astron.',
    'BaltA':'Baltic Astron.',
    'BASI':'Bull.Astron.Soc.India',
    'BlJPh':'Bulg.J.Phys.',
    'BSRSL':'Bull.Soc.Roy.Sci.Liege',
    'CAD':'Comput. Aided Geom. Des.',
    'CaJCh':'Can.J.Chem.',
    'CaJPh':'Can.J.Phys.',
    'CeMDA':'Celestial Mech.',
    'CGIP':'Comput.Vision Graphics Image Proc.',
    'ChA&A':'Chin.Astron.Astrophys.',
    'Chaos':'Chaos',
    'ChEnS':'Chem.Eng.Sci.',
    'ChGeo':'Chem. Geol.',
    'ChJNP':'Chin.J.Nucl.Phys.',
    'ChPhy':'Chin.Phys.',
    'CJLTP':'Chin.J.Low Temp.Phys.',
    'CMAME':'Comput.Methods Appl.Mech.Eng.',
    'CMaPh':'Commun.Math.Phys.',
    'CMT':'Contin.Mech.Thermodyn.',
    'CMwA':'Comput.Math.Appl.',
    'CoFl':'Combust.Flame',
    'ComAp':'Comments Astrophys.',
    'ComMP':'Comments Mod.Phys.',
    'Comp':'Computer',
    'ComPh':'Comput.Phys.',
    'ConPh':'Contemp.Phys.',
    'CoPhC':'Comput.Phys.Commun.',
    'CPAM':'Commun.Pure Appl.Math.',
    'CPL':'Chem.Phys.Lett.',
    'CQGra':'Class.Quant.Grav.',
    'Cryo':'Cryogenics',
    'CryRp':'Cystallogr.Rep.',
    'CSF':'Chaos Solitons Fractals',
    'CST':'Combust.Sci.Tech.',
    'CzJPh':'Czech.J.Phys.',
    'CzMJ':'Czech.Math.J.',
    'Disc':'Discover',
    'DokPh':'Phys.Dokl.',
    'DynCo':'J.Guid.Control Dyn.',
    'E&PSL':'Earth Planet.Sci.Lett.',
    'EcSJ':'J.Electrochem.Soc.',
    'EJPh':'Eur.J.Phys.',
    'EL':'Europhys.Lett.',
    'Elek':'Radiotekh.Elektron.',
    'ElL':'Electron.Lett.',
    'ElP':'Electron.Power',
    'EM&P':'Earth Moon Planets',
    'Endvr':'Endeavour',
    'EnST':'Environ.Sci.Tech.',
    'ESAJ':'ESA J.',
    'ExA':'Exper.Astron.',
    'ExT':'Instrum.Exp.Tech.',
    'FAAp':'Funct.Anal.Appl.',
    'FBS':'Few Body Syst.',
    'FCPh':'Fund.Cosmic Phys.',
    'Fiz':'Fizika',
    'FizMS':'Fiz.Mnogochast.Sistem',
    'FizTT':'Fiz.Tverd.Tela',
    'FlDy':'Fluid Dynamics',
    'FlDyR':'Fluid Dynamics Res.',
    'FlMSR':'Fluid Mech.Sov.Res.',
    'FoPh':'Found.Phys.',
    'GApFD':'Geophys.Astrophys.Fluid Dynamics',
    'GeCoA':'Geochim.Cosmochim.Acta',
    'GeGe':'Stud.Geophys.Geod.',
    'GeoJ':'Geophys.J.(U.S.)',
    'GeoJI':'Geophys.J.Int.',
    'GeoRL':'Geophys.Res.Lett.',
    'GReGr':'Gen.Rel.Grav.',
    'HDP':'Handb.Phys.',
    'HeaPh':'Health Phys.',
    'HiA':'Highlights Astron.',
    'HMT':'Int.J.Heat Mass Transf.',
    'HTHP':'High Temp.High Pressures',
    'IAUC':'IAU Circ.',
    'IAUS':'IAU Symp.',
    'Icar':'Icarus',
    'IComM':'IEEE Commun.Mag.',
    'ICSE':'Impact Comput.Sci.Eng.',
    'IDAQP':'Inf.Dim.Anal.Quant.Probab.Rel.Top.',
    'IER':'Int.Elek.Rundsch.',
    'IJBC':'Int.J.Bifurc.Chaos',
    'IJC':'Int.J.Control',
    'IJE':'Int.J.Electron.',
    'IJES':'Int.J.Eng.Sci.',
    'IJIMW':'Int.J.Infrared MM Waves',
    'IJMSI':'Int.J.Mass Spectr.Ion Process.',
    'IJNA':'IMA J.Numer.Anal.',
    'IJNME':'Int.J.Numer.Meth.Eng.',
    'IJNMF':'Int. J. Numer. Methods Fluids',
    'IJQC':'Int.J.Quant.Chem.',
    'IJQE':'IEEE J.Quant.Electron.',
    'IJRA':'IEEE J.Robot.Automat.',
    'IJScA':'Int.J.Supercomput.Appl.',
    'IJSSC':'IEEE J.Solid State Circuits',
    'IJTP':'Int.J.Theor.Phys.',
    'InCh':'Inorg.Chem.',
    'InfCo':'Info.Control',
    'InfPh':'Infrared Physics',
    'InJTP':'Indian J.Theor.Phys.',
    'InPhT':'Infrared Phys.Tech.',
    'IPTL':'IEEE Photonics Tech.Lett.',
    'IrAJ':'Irish Astron.J.',
    'IST':'Issues Sci.Technol.',
    'ITAC':'IEEE Trans.Automatic Control',
    'ITASS':'IEEE Trans.Acoust.Speech Signal Proc.',
    'ITBE':'IEEE Trans.Biomed.Eng.',
    'ITCmp':'IEEE Trans.Comput.',
    'ITCom':'IEEE Trans.Commun.',
    'ITCS':'IEEE Trans.Circuits Theor.',
    'ITEdu':'IEEE Trans.Educ.',
    'ITEI':'IEEE Trans.Electric.Insul.',
    'ITElC':'IEEE Trans.Electromagn.Compat.',
    'ITGRS':'IEEE Trans.Geosci.Remote Sensing',
    'ITIA':'IEEE Trans.Indust.Appl.',
    'ITIM':'IEEE Trans.Instrum.Measur.',
    'ITIT':'IEEE Trans.Info.Theor.',
    'ITM':'IEEE Trans.Magnetics',
    'ITMTT':'IEEE Trans.Microwave Theor.Tech.',
    'ITNN':'IEEE Trans.Neural Networks',
    'ITNS':'IEEE Trans.Nucl.Sci.',
    'ITPAM':'IEEE Trans.Pattern Anal.Machine Intell.',
    'ITPS':'IEEE Trans.Plasma Sci.',
    'ITRA':'IEEE Trans.Robotics Automation',
    'ITSE':'IEEE Trans.Software Eng.',
    'ITSMC':'IEEE Trans.Syst.Man Cybern.',
    'ITSP':'IEEE Trans.Signal Process.',
    'ITUFF':'IEEE Trans.Ultrason.Ferroelectr.Freq.Control',
    'JAChS':'J.Am.Chem.Soc.',
    'JAerS':'J.Aerosol Sci.',
    'JaJAP':'Jap.J.Appl.Phys.',
    'JAllC':'J.Alloys Compounds',
    'JAnSc':'J.Astronaut.Sci.',
    'JAP':'J.Appl.Phys.',
    'JApA':'J.Astrophys.Astron.',
    'JAPh':'J.Appl.Physiol.',
    'JApMa':'Ima J.Appl.Math.',
    'JApMe':'J.Appl.Meteor.',
    'JAtC':'J.Atmos.Chem.',
    'JATP':'J.Atmos.Terr.Phys.',
    'JAtS':'J.Atmos.Sci.',
    'JAVSO':'J.Am.Assoc.Var.Star Obs.',
    'JBIS':'J.Br.Interplanet.Soc.',
    'JCh':'J.Chromatogr.',
    'JChPh':'J.Chem.Phys.',
    'JCIS':'J.Coll.Interface Sci.',
    'JCM':'J.Comput.Appl.Math.',
    'JCoCh':'J.Comput.Chem.',
    'JCoPh':'J.Comput.Phys.',
    'JCrGr':'J.Cryst.Growth',
    'JDE':'J.Diff.Eq.',
    'JEEEA':'J.Electr.Electron.Eng.Aust.',
    'JEMat':'J.Electron.Mater.',
    'JESRP':'J.Electron Spectrosc.Rel.Phenom.',
    'JETP':'J.Exp.Theor.Phys.',
    'JEWA':'J.Electromagn.Waves Appl.',
    'JFM':'J.Fluid Mech.',
    'JG':'J.Geology',
    'JGG':'J.Geomag.Geoelectr.Japan',
    'JGla':'J.Glaciol.',
    'JGP':'J.Geom.Phys.',
    'JGR':'J.Geophys.Res.',
    'JHA':'J.Hist.Astron.',
    'JHyd':'J.Hydronaut.',
    'JIEq':'J.Integ.Eq.',
    'JIMIA':'J.Inst.Math.Appl.',
    'jimo':'WGN',
    'JKAS':'J.Korean Astron.Soc.',
    'JLCM':'J.Less Common Met.',
    'JLTP':'J.Low.Temp.Phys.',
    'JLwT':'J.Lightwave Tech.',
    'JMAA':'J.Math.Anal.Appl.',
    'JMagR':'J.Magn.Resonance',
    'JMatR':'J.Mater.Res.',
    'JMatS':'J.Materials Sci.Lett.',
    'JMec':'J.Mecan.',
    'JMecA':'J.Meca.Theor.Appl.',
    'JMemS':'J.Microelectromech.Syst.',
    'JMet':'J.Metals',
    'JMMM':'J.Magn.Magn.Mater.',
    'JMoEl':'J.Molec.Electron.',
    'JMolE':'J.Molec.Evol.',
    'JMoSp':'J.Molec.Spectrosc.',
    'JMoSt':'J.Molec.Struc.',
    'JMP':'J.Math.Phys.',
    'JMPSo':'J.Mech.Phys.Solids',
    'JNCS':'J.Noncryst.Solids',
    'JNET':'J.Nonequil.Thermo.',
    'JNOPM':'J.Nonlin.Opt.Phys.Mater.',
    'JNS':'J.Nonlin.Sci.',
    'JNuM':'J.Nucl.Mater.',
    'JOpt':'J.Optics',
    'JOTA':'J.Optim.Th.Appl.',
    'JPCM':'J.Phys.Condens.Matter',
    'JPCRD':'J.Phys.Chem.Ref.Data',
    'JPCS':'J.Phys.Chem.Solids',
    'JPDC':'J.Parallel Distrib.Comput.',
    'JPhA':'J.Phys.A',
    'JPhA':'J.Phys.',
    'JPhB':'J.Phys.B',
    'JPhB':'J.Phys.B.At.Mol.Opt.Phys.',
    'JPhC':'J.Phys.C',
    'JPhCh':'J.Phys.Chem.',
    'JPhD':'J.Phys.D',
    'JPhE':'J.Phys.E',
    'JPhF':'J.Phys.F',
    'JPhG':'J.Phys.G',
    'JPhys':'J.Phys.(France)',
    'JPlPh':'J.Plasma Phys.',
    'JPO':'J.Phys.Oceanogr.',
    'JPP':'J.Propulsion Power',
    'JQSRT':'J.Quant.Spectrosc.Radiat.Trans.',
    'JRAC':'J.Radioanal.Chem.',
    'JRASC':'J.Roy.Astron.Soc.Canada',
    'JRNBS':'J.Res.Natl.Bur.Stand.',
    'JSCom':'J.Sci.Comput.',
    'JSLR':'J.Russ.Laser Res.',
    'JSP':'J.Statist.Phys.',
    'JSup':'J.Supercond.',
    'JSV':'J.Sound Vibrat.',
    'JVST':'J.Vac.Sci.Tech.',
    'JWasA':'J.Wash.Acad.Sci.',
    'LaPaB':'Laser Part.Beams',
    'LicOB':'Lick Obs.Bull.',
    'LiCr':'Mol.Cryst.Liq.Cryst.',
    'M&P':'Moon Planets',
    'MaCom':'Math.Comput.',
    'Math':'Mathematika',
    'MatL':'Mater.Lett.',
    'MComM':'Math.Comput.Modelling',
    'Mecc':'Meccanica',
    'MedPh':'Med.Phys.',
    'MeReC':'Mech.Res.Commun.',
    'Metic':'Meteoritics',
    'Metro':'Metrologia',
    'MiOTL':'Microw.Opt.Technol.Lett.',
    'MmARB':'Acad.Roy.Belg.Sci.Mem.',
    'MMAS':'Math.Methods Appl.Sci.',
    'MmRAS':'Mem.Roy.Astron.Soc.',
    'MmSAI':'Mem.Soc.Ast.It.',
    'MNRAS':'Mon.Not.Roy.Astron.Soc.',
    'MolPh':'Mol.Phys.',
    'mpla, mplb':'Mod.Phys.Lett.',
    'MSEng':'Mater.Sci.Eng.',
    'MSRSL':'Mem.Soc.Roy.Sci.Liege',
    'MWRv':'Mon.Weather Rev.',
    'Nanot':'Nanotechnol.',
    'Natur':'Nature',
    'NCimL':'Lett.Nuovo Cim.',
    'NDS':'Nucl.Data Sheets',
    'NewA':'New Astron.',
    'NewSc':'New Sci.',
    'NIMPR':'Nucl.Instrum.Meth.',
    'NInfo':'Nauchnye Inform.Astron.Sov.Akad Nauk SSR',
    'NISTJ':'J.Res.Natl.Inst.Stand.Tech.',
    'NJPh':'New J.Phys.',
    'Nonli':'Nonlinearity',
    'NPhS':'Nature Phys.Sci.',
    'NucFu':'Nucl.Fusion',
    'NucPh':'Nucl.Phys.',
    'NuMat':'Numer.Math.',
    'NuPhS':'Nucl.Phys.Proc.Suppl.',
    'NW':'Naturwiss.',
    'NYASA':'Annals N.Y.Acad.Sci.',
    'Obs':'Observatory',
    'OLEB':'Orig.Life.Evol.Biosph.',
    'OptCo':'Opt.Commun.',
    'OptEn':'Opt.Eng.',
    'OptL':'Opt.Lett.',
    'OptLT':'Opt.Laser Tech.',
    'OptMa':'Opt.Mater.',
    'OptN':'Optics News',
    'OptPN':'Opt.Phontonics News',
    'OptQE':'Opt.Quant.Electron.',
    'OSAJ':'J.Opt.Soc.Am.',
    'P&SS':'Planet.Space Sci.',
    'PAN':'Phys.Atom.Nucl.',
    'ParC':'Parallel Comput.',
    'PaReL':'Pattern Recog.Lett.',
    'PASA':'Publ.Astron.Soc.Austral.',
    'PASAu':'Proc.Astron.Soc.Austral.',
    'PASJ':'Publ.Astron.Soc.Jap.',
    'PASP':'Publ.Astron.Soc.Pac.',
    'PDO':'Publ.Dominion Astrophys.Obs.',
    'PEPI':'Phys.Earth Planet.Interiors',
    'PhB':'Phys.Bull.',
    'PhFl':'Phys.Fluids',
    'PhL':'Phys.Lett.',
    'PhoSp':'Photonics Spectra',
    'PhP':'Phys.Perspect.',
    'PhPl':'Phys.Plasmas',
    'PhR':'Phys.Rept.',
    'PhRv':'Phys.Rev.',
    'PhRvL':'Phys.Rev.Lett.',
    'PhRvS':'Phys.Rev.ST Accel.Beams',
    'PhT':'Phys.Today',
    'PhTea':'Phys.Teacher',
    'Phy':'Physica',
    'PhyEd':'Phys.Educ.India',
    'PhyS':'Phys.Scripta',
    'PlPh':'Plasma Phys.',
    'PlPhR':'Plasma Phys.Rep.',
    'PMB':'Phys.Med.Biol.',
    'PNAS':'Proc.Nat.Acad.Sci.',
    'PPCF':'Comments Plasma Phys.Contr.Fusion',
    'PPN':'Phys.Part.Nucl.',
    'PQE':'Prog.Quant.Electron.',
    'Prama':'Pramana',
    'PrECS':'Prog.Energy Combust.Sci.',
    'PRI':'Phys.Res.Int.',
    'PriTE':'Prib.Tekh.Eksp.',
    'PrPNP':'Prog.Part.Nucl.Phys.',
    'PSci':'Pour La Science',
    'PThPh':'Prog.Theor.Phys.',
    'PThPS':'Prog.Theor.Phys.Suppl.',
    'QApMa':'Q.Appl.Math.',
    'QJMAM':'Q.J.Mech.Appl.Math.',
    'QJRAS':'Q.J.Roy.Astron.Soc.',
    'Quest':'Rev.Quest.Sci.',
    'QuSOp':'Quant.Semiclass.Opt.',
    'R&QE':'Radiophys.Quant.Electron.',
    'RaF':'Izv.Vuz.Radiofiz.',
    'RaPC':'Radiat.Phys.Chem.',
    'RaRe':'Rad.Res.',
    'RaRLJ':'J.Radio Res.Lab.',
    'RaSc':'Radio Sci.',
    'RCARv':'RCA Rev.',
    'Rech':'Recherche',
    'RMxAA':'Rev.Mex.Astron.Astrofis.',
    'RMxAC':'Rev.Mex.Astron.Astrof.Ser.Conf.',
    'RpMP':'Rept.Math.Phys.',
    'RPPh':'Rept.Prog.Phys.',
    'RScI':'Rev.Sci.Instrum.',
    'rspsa':'Proc.Roy.Soc.Lond.A Math.Phys.Eng.Sci.',
    'rspsa, rspsb':'Proc.Roy.Soc.Lond.',
    'RvGSP':'Rev.Geophys.',
    'RvMA':'Rev.Mod.Astron.',
    'RvMaP':'Rev.Math.Phys.',
    'RvMP':'Rev.Mod.Phys.',
    'RvPA':'Rev.Phys.Appl.',
    'RvRP':'Rom.J.Phys.',
    'SAJPh':'South Afr.J.Phys.',
    'SAJSc':'South Afr.J.Sci.',
    'Sci':'Science',
    'SciAm':'Sci.Am.',
    'SciDi':'Sci.Dimens.',
    'SciSn':'Sci.Sin.',
    'SeAc':'Sens.Actuators',
    'SerAJ':'Serb.Astron.J.',
    'SeST':'Semicond.Sci.Tech.',
    'ShWav':'Shock Waves(Germany)',
    'SigPr':'Signal Processing',
    'SJAM':'SIAM J.Appl.Math.',
    'SJCO':'SIAM J.Control Optim.',
    'SJMA':'SIAM J.Math.Anal.',
    'SJNA':'SIAM J.Numer.Anal.',
    'SoCe':'Solar Energy Mater.Solar Cells',
    'SoEn':'Solar Energ.',
    'SoPh':'Solar Phys.',
    'SpFl':'Spaceflight',
    'SPhD':'Sov.Phys.Dokl.',
    'SPIE':'Proc.SPIE Int.Soc.Opt.Eng.',
    'SRL':'Surf. Rev. Lett.',
    'SSCom':'Solid State Commun.',
    'SScT':'Speculations Sci.Tech.',
    'SSEle':'Solid State Electron.',
    'SSI':'Space Sci.Instrum.',
    'SSRv':'Space Sci.Rev.',
    'SSTec':'Solid State Technol.',
    'StAM':'Stud.Appl.Math.',
    'SuMi':'Superlattices Microstruct.',
    'SurSc':'Surf.Sci.',
    'SuScT':'Supercond.Sci.Technol.',
    'SvA':'Sov.Astron.',
    'SvJNP':'Sov.J.Nucl.Phys.',
    'SvJPP':'Sov.J.Plasma Phys.',
    'SvJQE':'Quant.Electron.',
    'SvPhU':'Sov.Phys.Usp.',
    'Tecto':'Tectonophys.',
    'Tell':'Tellus',
    'TePhL':'Sov.Tech.Phys.Lett.',
    'ThCFD':'Theor.Comput.Fluid Dyn.',
    'TJPh':'Turk.J.Phys.',
    'TSF':'Thin Solid Films',
    'UkFiZ':'Ukr.Fiz.Zh.(Russ.Ed.)',
    'UkMaZ':'Ukr.Mat.Zh.',
    'UltIm':'Ultrason. Imag.',
    'Ultmi':'Ultramicroscopy',
    'Ultra':'Ultrasonics',
    'UsFiN':'Usp.Fiz.Nauk',
    'VA':'Vistas Astron.',
    'WaMot':'Wave Motion',
    'WisBT':'Wiss.Ber.AEG Telefunken',
    'WRM':'Waves Random Media',
    'ZaMM':'Z.Angew.Math.Mech.',
    'ZaMP':'Z.Angew.Math.Phys.',
    'ZhPS':'Zh.Prikl.Spektrosk.',
    'ZhTFi':'Zh.Tekh.Fiz.',
    'ZNatA':'Z.Naturforsch., Teil A',
    'zphy':'Z.Phys.'
    }


def journal_fix(journal):
    """
    Puts the journal name into INSPIRE form.
    """
    for key in JOURNAL_DICT:
        if journal == key:
            return JOURNAL_DICT[key]
    journal = re.sub(r'^Acta\.', r'Acta ', journal)
    search = '711__a:"' + journal + '"'
    result = perform_request_search(p=search, cc='Journals')
    if len(result) == 1:
        return journal
    elif re.search(r'\.$', journal):
        journal = re.sub(r'\.$', r'', journal)
        journal_iter = journal_fix(journal)
        return journal_iter
    else:
        if VERBOSE > 0:
            print 'BAD JOURNAL', journal
        return None

def create_xml(input_dict):
    """
    The function create_xml takes an article dictionary from ADS and
    checks to see if it has information that should be added to INSPIRE.
    If so, it builds up that information.
    """

    elements = ['doi', 'preprint_id', 'journal_bibcode', 'journal_ref']
    element_dict = {}
    pubyear = ''
    for element in elements:
        element_dict[element] = ''
        if element in input_dict:
            element_dict[element] = input_dict[element]
        #print element, '=', element_dict[element]
    eprint  = element_dict['preprint_id']
    if eprint:
        eprint  = re.sub(r'arXiv:([a-z])', r'\1', eprint)
    doi     = element_dict['doi']
    bibcode = element_dict['journal_bibcode']
    journal = element_dict['journal_ref']
    volume  = ''
    page    = ''
    if VERBOSE == 2:
        print element_dict
    search  = '035__a:' + bibcode
    result = perform_request_search(p=search, cc='HEP')
    if len(result) == 1:
        return None
    if doi:
        if re.search(r'10.1103/PhysRev[CD]', doi):
            return None
        if re.search(r'10.1016/j.nuclphysb', doi):
            return None
        search  =  '0247_a:' + doi
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1:
            return None
    #Phys.Rev.A.86:013639,2012
    #J.Appl.Phys.100:084104,2006
    match_obj = re.search(r'(.*\w\.)(\d+)\:(\w+)\,(\d{4})', journal)
    if match_obj:
        journal = match_obj.group(1)
        volume  = match_obj.group(2)
        page    = match_obj.group(3)
        pubyear = match_obj.group(4)
        if re.search(r'\.\.\d+L\.', bibcode):
            page = 'L' + page
    if journal and volume:
        match_obj = re.match(r'^(.*\.)(\w)\.$', journal)
        if match_obj:
            letter   = match_obj.group(2)
            if letter in ['A', 'B', 'C', 'D', 'E', 'X']:
                volume   = letter + volume
                journal  = match_obj.group(1)
        journal = journal_fix(journal)
        if not journal:
            match_obj = re.match(r'^\d{4}(\w+)', bibcode)
            if match_obj:
                journal = journal_fix(match_obj.group(1))
    if eprint and journal and volume and page and pubyear:
        search = 'find j "' + journal + ',' + volume + ',' + page + '"'
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1:
            return None
        search = "find eprint " + eprint + " not tc p"
        result = perform_request_search(p=search, cc='HEP')
        if len(result) == 1 :
            recid = result[0]
            for badrec in BADRECS:
                if recid == badrec:
                    return None
            record = {}
            record_add_field(record, '001', controlfield_value=str(recid))
            pubnote = [('p', journal), ('v', volume), ('c', page)]
            pubnote.append(('y', pubyear))
            record_add_field(record, '773', '', '', subfields=pubnote)
            if doi:
                doi  = [('a', doi), ('2', 'DOI'), ('9', 'ADS')]
                record_add_field(record, '024', '7', '', subfields=doi)
            if bibcode:
                bibcode  = [('a', bibcode), ('9', 'ADS')]
                record_add_field(record, '035', '', '', subfields=bibcode)
            return print_rec(record)
        else:
            return None
    else:
        return None

def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    tree = ET.parse(DOCUMENT)
    root = tree.getroot()
    input_counter  = 1
    output_counter = 1
    for child in root:
        if input_counter < INPUT_COUNTER:
            input_counter  += 1
        else:
            if output_counter == OUTPUT_COUNTER: break
            if 'doi' in child.attrib:
                record_update = create_xml(child.attrib)
                if record_update:
                    try:
                        if DEBUG == 1:
                            print record_update
                        else:
                            output.write(record_update)
                            output_counter += 1
                    except:
                        print 'CANNOT print record', child.attrib
    output.write('</collection>')
    output.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'

