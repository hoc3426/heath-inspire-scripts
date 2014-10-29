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
from hep_convert_email_to_id import get_hepnames_recid_from_email
from hep_convert_email_to_id import find_inspire_id_from_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field
#from afftranslator2 import bestmatch

def create_xml(author,email,af,experiment):
    common_fields = {}
    common_tags = {}
    author2 = re.sub(r'(.*)\, (.*)',r'\2 \1', author)
    common_tags['980__'] = [('a', 'HEPNAMES')]
    common_tags['100__'] = [('a', author), ('q', author2), ('g', 'ACTIVE')]
    common_tags['371__'] = [('m', email),('a', af),('z', 'current')]
    common_tags['693__'] = [('e', experiment),('z', 'current')]
    for key in common_tags:
        tag = key
        record_add_field(common_fields, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    #return common_fields
    print print_rec(common_fields)



authors = [["chris.lidman@AAO.GOV.AU", "Chris Lidman"],
["guptar@ANL.GOV", "Ravi Gupta"],
["habib@ANL.GOV", "Salman Habib"],
["heitmann@ANL.GOV", "Katrin Heitmann"],
["kuhlmann@ANL.GOV", "Steve Kuhlmann"],
["fo250@AST.CAM.AC.UK", "Fernanda Ostrovski"],
["gpe@AST.CAM.AC.UK", "George Efstathiou"],
["rgm@AST.CAM.AC.UK", "Richard McMahon"],
["sr525@AST.CAM.AC.UK", "Sophie Reed"],
["wjs@AST.CAM.AC.UK", "Will Sutherland"],
["rb@ASTRO.UIUC.EDU", "Robert J. Brunner"],
["ckochanek@ASTRONOMY.OHIO-STATE.EDU", "Chris Kochanek"],
["dhw@ASTRONOMY.OHIO-STATE.EDU", "David H. Weinberg"],
["martini@ASTRONOMY.OHIO-STATE.EDU", "Paul Martini"],
["whu@BACKGROUND.UCHICAGO.EDU", "(No Name Available)"],
["jcohn@BERKELEY.EDU", "Joanne Cohn"],
["mwhite@BERKELEY.EDU", "Martin White"],
["chbrandt@CBPF.BR", "Carlos Brandt"],
["martin@CBPF.BR", "Martin Makler"],
["eusebio.sanchez@CIEMAT.ES", "Eusebio Sanchez"],
["franciscojavier.sanchez@CIEMAT.ES", "Francisco Javier Sánchez López"],
["juan.vicente@CIEMAT.ES", "Juan De Vicente"],
["Julia.Campa@CIEMAT.ES", "Julia Campa"],
["manuel.garcia-fernandez@CIEMAT.ES", "Manuel Garcia"],
["rafael.ponce@CIEMAT.ES", "Rafael Ponce"],
["Cartert@COD.EDU", "Tom Carter"],
["bgregory@CTIO.NOAO.EDU", "Brooke Gregory"],
["csmith@CTIO.NOAO.EDU", "Chris Smith"],
["djj@CTIO.NOAO.EDU", "David James"],
["rschmidt@CTIO.NOAO.EDU", "Ricardo Schmidt"],
["tabbott@CTIO.NOAO.EDU", "Tim Abbott"],
["walker@CTIO.NOAO.EDU", "Alistair Walker"],
["wayne.barkhouse@EMAIL.UND.EDU", "Wayne Barkhouse"],
["martin.melchior@FHNW.CH", "Martin Melchior"],
["michael.graber@FHNW.CH", "Michael Graber"],
["stefan.mueller@FHNW.CH", "Stefan Müller"],
["annis@FNAL.GOV", "James Annis"],
["aphearin@FNAL.GOV", "Andrew Hearin"],
["boj@FNAL.GOV", "Bo Jayatilaka"],
["brenna@FNAL.GOV", "Brenna Flaugher"],
["bstalder@FNAL.GOV", "Brian Stalder"],
["Buckley@FNAL.GOV", "Liz Buckley-Geer"],
["cease@FNAL.GOV", "Herman Cease"],
["despub@FNAL.GOV", "No Name Available"],
["diehl@FNAL.GOV", "Tom Diehl"],
["dodelson@FNAL.GOV", "Scott Dodelson"],
["dtucker@FNAL.GOV", "Douglas Tucker"],
["estrada@FNAL.GOV", "Juan Cruz Estrada"],
["finley@FNAL.GOV", "David Finley"],
["frieman@FNAL.GOV", "Joshua Frieman"],
["gaston@FNAL.GOV", "Gaston Gutierrez"],
["glass@FNAL.GOV", "Henry Glass"],
["hlin@FNAL.GOV", "Huan Lin"],
["jghao@FNAL.GOV", "Jiangang Hao"],
["kuropat@FNAL.GOV", "Nickolai Kuropatkine"],
["langcm60@FNAL.GOV", "Connie Lang"],
["marcelle@FNAL.GOV", "Marcelle Soares-Santos"],
["marriner@FNAL.GOV", "John Marriner"],
["neilsen@FNAL.GOV", "Eric Neilsen"],
["noreply-despub@FNAL.GOV", "DES PUB Board"],
["peop@FNAL.GOV", "John Peoples, Jr."],
["rkessler@FNAL.GOV", "Rick Kessler"],
["sallam@FNAL.GOV", "Sahar Allam"],
["scarpine@FNAL.GOV", "Vic Scarpine"],
["sein@FNAL.GOV", "Eun-Joo Ahn"],
["skent@FNAL.GOV", "Stephen Kent"],
["stebbins@FNAL.GOV", "Albert Stebbins"],
["stefanik@FNAL.GOV", "Andy Stefanik"],
["stoughto@FNAL.GOV", "Chris Stoughton"],
["wester@FNAL.GOV", "William Wester"],
["wyatt@FNAL.GOV", "Wyatt Merritt"],
["yanny@FNAL.GOV", "Brian Yanny"],
["alocice@GMAIL.COM", "Andreas Lo Cicero"],
["angelofausti@GMAIL.COM", "Angelo Fausti Neto"],
["arnaupv@GMAIL.COM", "Arnau Pujol"],
["c.bonnett@GMAIL.COM", "Christopher Bonnett"],
["carloscunha47@GMAIL.COM", "Carlos Cunha"],
["chihway54@GMAIL.COM", "Chihway Chang"],
["csabiu@GMAIL.COM", "Cristiano Sabiu"],
["donnachakirk@GMAIL.COM", "Donnacha Kirk"],
["drlisekrause@GMAIL.COM", "Elisabeth Krause"],
["eduardo.balbinot@GMAIL.COM", "Eduardo Balbinot"],
["emhuff@GMAIL.COM", "Eric Huff"],
["eric.d.suchyta@GMAIL.COM", "Eric Suchyta"],
["erin.sheldon@GMAIL.COM", "Erin Sheldon"],
["fjcastander@GMAIL.COM", "Francisco Castander"],
["fosalba@GMAIL.COM", "Pablo Fosalbo"],
["GAZTANAGA@GMAIL.COM", "Enrique Gaztanaga"],
["gbcaminha@GMAIL.COM", "Gabriel Caminha"],
["jashugart@GMAIL.COM", "Jessica Shugart"],
["jasorey@GMAIL.COM", "No Name Available"],
["jorgecarreteropalacios@GMAIL.COM", "Jorge Carretero"],
["kadrlica@GMAIL.COM", "Alex Drlica-Wagner"],
["martin.b.eriksen@GMAIL.COM", "No Name Available"],
["matsmith2@GMAIL.COM", "Mathew Smith"],
["mlantonik@GMAIL.COM", "Michelle Antonik"],
["molly.swanson@GMAIL.COM", "Molly Swanson"],
["nsevilla@GMAIL.COM", "Ignacio Sevilla"],
["peter.m.melchior@GMAIL.COM", "Peter Melchior"],
["rbiswas4@GMAIL.COM", "Rahul Biswas"],
["rearmstr@GMAIL.COM", "Bob Armstrong"],
["rkeisler@GMAIL.COM", "Ryan Keisler"],
["rubirah1@GMAIL.COM", "ALL Henrique Rubira"],
["ryanjfoley@GMAIL.COM", "Ryan Foley"],
["sazabi.li@GMAIL.COM", "Ting Li"],
["sb.bonoli@GMAIL.COM", "Silvia Bonoli"],
["shntn05@GMAIL.COM", "Shantanu Desai"],
["timeifler@GMAIL.COM", "Tim Eifler"],
["tommaso.giannantonio@GMAIL.COM", "Tommaso Giannantonio"],
["willliam.hartley@GMAIL.COM", "Will Hartley"],
["ykakazu@GMAIL.COM", "Yuko Kakazu"],
["samuel.farrens@GOOGLEMAIL.COM", "Samuel Farrens"],
["hms@HEP.ANL.GOV", "Hal Spinka"],
["kkuehn@HEP.ANL.GOV", "Kyler Kuehn"],
["kovacs@HEP.ANL.GOV", "Eve Kovacs"],
["rlt@HEP.ANL.GOV", "Rich Talaga"],
["sdeb@HEP.ANL.GOV", "No Name Available"],
["larryg@HEP.UPENN.EDU", "Larry Gladney"],
["rponceaci4@HOTMAIL.COM", "Rafael Ponce"],
["jc@HYDE.UCHICAGO.EDU", "John Carlstrom"],
["bertin@IAP.FR", "Emmanuel Bertin"],
["bauer@IEEC.UAB.ES", "Anne Bauer"],
["crocce@IEEC.UAB.ES", "Martin Crocce"],
["serrano@IEEC.UAB.ES", "Santi Serrano"],
["csanchez@IFAE.ES", "Carles Sanchez"],
["Enrique.Fernandez@IFAE.ES", "Enrique Fernandez"],
["jelena@IFAE.ES", "Jelena Aleksic"],
["laia@IFAE.ES", "Laia Cardiel Sas"],
["rmiquel@IFAE.ES", "Ramon Miquel"],
["fabien@IFT.UNESP.BR", "Fabien Lacasa"],
["bigdog@ILLINOIS.EDU", "Robert J. Brunner"],
["felipe@ILLINOIS.EDU", "Felipe Menanteau"],
["gruendl@ILLINOIS.EDU", "Robert Gruendl"],
["jjt@ILLINOIS.EDU", "Jon Thaler"],
["kindrtnk@ILLINOIS.EDU", "Kindratenko, Volodymyr"],
["mcarras2@ILLINOIS.EDU", "$B!> (BDMUSERS Matias Carrasco Kind"],
["petravic@ILLINOIS.EDU", "Don Petravick"],
["pmricker@ILLINOIS.EDU", "Paul Ricker"],
["riccov@ILLINOIS.EDU", "Ricardo Covarrubias"],
["michael@JARVIS.NET", "Mike Jarvis"],
["bbenson@KICP.UCHICAGO.EDU", "Bradford Benson"],
["bechtol@KICP.UCHICAGO.EDU", "Keith Bechtol"],
["erozo@KICP.UCHICAGO.EDU", "Eduardo Rozo"],
["marilena@KICP.UCHICAGO.EDU", "Marilena LoVerde"],
["rreyes@KICP.UCHICAGO.EDU", "Reina Reyes"],
["agkim@LBL.GOV", "Alex Kim"],
["CJBebek@LBL.GOV", "Chris Bebek"],
["GAldering@LBL.GOV", "Greg Aldering"],
["melevi@LBL.GOV", "Michael Levi"],
["naroe@LBL.GOV", "(No Name Available)"],
["PENugent@LBL.GOV", "Peter Nugent"],
["rcthomas@LBL.GOV", "Rollin Thomas"],
["saul@LBL.GOV", "Saul Perlmutter"],
["carnero@LINEA.GOV.BR", "Aurelio Carnero Rosell"],
["julia@LINEA.GOV.BR", "Julia Gschwend"],
["ldacosta@LINEA.GOV.BR", "Luiz da Costa"],
["maia@LINEA.GOV.BR", "Marcio Antonio Geimba Maia"],
["ogando@LINEA.GOV.BR", "Ricardo Ogando"],
["sobreira@LINEA.GOV.BR", "FlÃ¡via Sobreira"],
["iandavidson@MAC.COM", "Ian Davidson"],
["bender@MPE.MPG.DE", "Ralf Bender"],
["saglia@MPE.MPG.DE", "Roberto Saglia"],
["twalker@MPS.OHIO-STATE.EDU", "Terry Walker"],
["mgelman@NCSA.ILLINOIS.EDU", "Margaret Gelman"],
["mjohns44@NCSA.ILLINOIS.EDU", "Michael Johnson"],
["rplante@NCSA.UIUC.EDU", "Ray Plante"],
["connolly@NEVIS.COLUMBIA.EDU", "Brian Connolly"],
["Meghan.Gray@NOTTINGHAM.AC.UK", "Meghan Gray"],
["ppxlo@NOTTINGHAM.AC.UK", "Lyndsay Old"],
["benoist@OCA.EU", "Christophe Benoist"],
["andrey@ODDJOB.UCHICAGO.EDU", "Andrey Kravtsov"],
["jhelsby@ODDJOB.UCHICAGO.EDU", "Jennifer Helsby"],
["rcawthon@ODDJOB.UCHICAGO.EDU", "Ross Cawthon"],
["Rich@ODDJOB.UCHICAGO.EDU", "Rich Kron"],
["zablocki@ODDJOB.UCHICAGO.EDU", "Alan Zablocki"],
["amores@ON.BR", "Eduardo Amores"],
["pssp@ON.BR", "Paulo Pellegrini"],
["blazek.35@OSU.EDU", "Jonathan Blazek"],
["gill.200@OSU.EDU", "Mandeep S S Gill"],
["tie.5@OSU.EDU", "Suk Sien Tie"],
["young.1205@OSU.EDU", "Julia Young"],
["adam.amara@PHYS.ETHZ.CH", "Adam Amara"],
["alexandre.refregier@PHYS.ETHZ.CH", "Alexandre Refregier"],
["claudio.bruderer@PHYS.ETHZ.CH", "Claudio Bruderer"],
["fiorella.cagnetta@PHYS.ETHZ.CH", "Fiorella Cagnetta"],
["marcella@PHYS.ETHZ.CH", "Marcella Carollo"],
["simon.birrer@PHYS.ETHZ.CH", "Simon Birrer"],
["simon.lilly@PHYS.ETHZ.CH", "Simon Lilly"],
["kh@PHYSICS.OSU.EDU", "Klaus Honscheid"],
["depoy@PHYSICS.TAMU.EDU", "Darren DePoy"],
["lmacri@PHYSICS.TAMU.EDU", "Lucas Macri"],
["marshall@PHYSICS.TAMU.EDU", "Jennifer Marshall"],
["n.mehrtens@PHYSICS.TAMU.EDU", "Nicola Mehrtens"],
["papovich@PHYSICS.TAMU.EDU", "Casey Papovich"],
["suntzeff@PHYSICS.TAMU.EDU", "Nicholas Suntzeff"],
["vy@PHYSICS.TAMU.EDU", "Kim-Vy Tran"],
["bernardm@PHYSICS.UPENN.EDU", "Mariangela Bernardi"],
["bjain@PHYSICS.UPENN.EDU", "Bhuvnesh Jain"],
["devlin@PHYSICS.UPENN.EDU", "Mark Devlin"],
["garyb@PHYSICS.UPENN.EDU", "Gary Bernstein"],
["shethrk@PHYSICS.UPENN.EDU", "Ravi Sheth"],
["vinu@PHYSICS.UPENN.EDU", "Vinu Vikraman"],
["tamarad@PHYSICS.UQ.EDU.AU", "Tamara Davis"],
["mbusha@PHYSIK.UZH.CH", "Michael Busha"],
["andreas.papadopoulos@PORT.AC.UK", "Andreas Papapoulos"],
["Ashley.Ross@PORT.AC.UK", "Ashley Ross"],
["bob.nichol@PORT.AC.UK", "Bob Nichol"],
["chris.dandrea@PORT.AC.UK", "Chris D'Andrea"],
["Claudia.Maraston@PORT.AC.UK", "Claudia Maraston"],
["daniel.thomas@PORT.AC.UK", "Daniel Thomas"],
["David.Bacon@PORT.AC.UK", "David Bacon"],
["diego.capozzi@PORT.AC.UK", "Diego Capozzi"],
["edward.edmondson@PORT.AC.UK", "Edd edmondson"],
["harry.wilcox@PORT.AC.UK", "Harry Wilcox"],
["heather.campbell@PORT.AC.UK", "Heather Campbell"],
["karen.masters@PORT.AC.UK", "Karen Masters"],
["marc.manera@PORT.AC.UK", "Marc Manera"],
["robert.crittenden@PORT.AC.UK", "Robert Crittenden"],
["roy.maartens@PORT.AC.UK", "Roy Maartens"],
["will.percival@PORT.AC.UK", "Will Percival"],
["J.Peacock@ROE.AC.UK", "John Peacock"],
["sarah@SARAHBRIDLE.NET", "Sarah Bridle"],
["ckrawiec@SAS.UPENN.EDU", "Christina Krawiec"],
["clampitt@SAS.UPENN.EDU", "Joseph Clampitt"],
["johnfisc@SAS.UPENN.EDU", "John Fischer"],
["mamarch@SAS.UPENN.EDU", "Marisa March"],
["masao@SAS.UPENN.EDU", "Masao Sako"],
["plazas@SAS.UPENN.EDU", "Andres Plazas"],
["rcane@SAS.UPENN.EDU", "Rachel Cane"],
["daveb@SLAC.STANFORD.EDU", "Dave Burke"],
["erykoff@SLAC.STANFORD.EDU", "Eli Rykoff"],
["marshall@SLAC.STANFORD.EDU", "Stuart Marshall"],
["rafe@SLAC.STANFORD.EDU", "Rafe Schindler"],
["roodman@SLAC.STANFORD.EDU", "Aaron Roodman"],
["tas@SLAC.STANFORD.EDU", "Terry Schalk"],
["cpd@STANFORD.EDU", "Christopher Davis"],
["kadrlica@STANFORD.EDU", "Alex Drlica-Wagner"],
["rmredd@STANFORD.EDU", "Rachel Reddick"],
["rwechsler@STANFORD.EDU", "Risa Wechsler"],
["zz3x7@STANFORD.EDU", "Zhang Zhang"],
["apd@STAR.UCL.AC.UK", "Peter Doel"],
["benoitl@STAR.UCL.AC.UK", "Aurelien Benoit-Lévy"],
["browe@STAR.UCL.AC.UK", "Barnaby Rowe"],
["csabiu@STAR.UCL.AC.UK", "Cristiano Sabiu"],
["db@STAR.UCL.AC.UK", "David Brooks"],
["fba@STAR.UCL.AC.UK", "Filipe B. Abdalla"],
["jaz@STAR.UCL.AC.UK", "Joe Zuntz"],
["lucyc@STAR.UCL.AC.UK", "Lucinda Clerkin"],
["lvoigt@STAR.UCL.AC.UK", "Lisa Voigt"],
["mbanerji@STAR.UCL.AC.UK", "Manda Banerji"],
["mjb@STAR.UCL.AC.UK", "Mike Barlow"],
["mts@STAR.UCL.AC.UK", "maayane Soumagnac"],
["sbalan@STAR.UCL.AC.UK", "Sreekumar Balan"],
["sv@STAR.UCL.AC.UK", "Serena Viti"],
["a.liddle@SUSSEX.AC.UK", "Andrew Liddle"],
["ab615@SUSSEX.AC.UK", "Alberto Bermeo"],
["ik77@SUSSEX.AC.UK", "John Katsaros"],
["l.baruah@SUSSEX.AC.UK", "Leon Baruah"],
["P.Rooney@SUSSEX.AC.UK", "Philip Rooney"],
["romer@SUSSEX.AC.UK", "kathy Romer"],
["kglazebrook@SWIN.EDU.AU", "Karl Glazebrook"],
["juan.garciabellido@UAM.ES", "Juan Garcia-Bellido"],
["beckermr@UCHICAGO.EDU", "Matthew Becker"],
["bleeml@UCHICAGO.EDU", "Lindsey Bleem"],
["gladders@UCHICAGO.EDU", "Michael Gladders"],
["adrienne.leonard@UCL.AC.UK", "Adrienne Leonard"],
["alexander.merson@UCL.AC.UK", "Alex Merson"],
["boris.leistedt.11@UCL.AC.UK", "Boris Leistedt"],
["f.elsner@UCL.AC.UK", "Franz Elsner"],
["h.peiris@UCL.AC.UK", "Hiranya Peiris"],
["i.sadeh@UCL.AC.UK", "Iftach Sadeh"],
["michael.hirsch@UCL.AC.UK", "Michael Hirsch"],
["niall.maccrann.12@UCL.AC.UK", "Niall MacCrann"],
["o.lahav@UCL.AC.UK", "Ofer Lahav"],
["s.jouvel@UCL.AC.UK", "Stephanie Jouvel"],
["tomasz.kacprzak.09@UCL.AC.UK", "Tomasz Kacprzak"],
["rab@UCOLICK.ORG", "Rebecca Bernstein"],
["shansen@UCOLICK.ORG", "Sarah Hansen"],
["tesla@UCSC.EDU", "Tesla Jeltema"],
["basilio.santiago@UFRGS.BR", "Basilio Xavier Santiago"],
["cristina.furlanetto@UFRGS.BR", "Cristina Furlanetto"],
["eduardo.balbinot@UFRGS.BR", "Eduardo Balbinot"],
["karliner@UIUC.EDU", "Inga Karliner"],
["sibert@UIUC.EDU", "(No Name Available)"],
["ajsyp@UMICH.EDU", "Adam Sypniewski"],
["bnord@UMICH.EDU", "Brian Nord"],
["christoq@UMICH.EDU", "Chris Miller"],
["dnidever@UMICH.EDU", "David Nidever"],
["evrard@UMICH.EDU", "Gus Evrard"],
["gerdes@UMICH.EDU", "Dave Gerdes"],
["gtarle@UMICH.EDU", "Greg Tarle"],
["huterer@UMICH.EDU", "Dragan Huterer"],
["jeeseons@UMICH.EDU", "Jeeseon Song"],
["jghao@UMICH.EDU", "Jiangang Hao"],
["lorenzon@UMICH.EDU", "Wolfgang Lorenzon"],
["schubnel@UMICH.EDU", "Michael Schubnell"],
["tamckay@UMICH.EDU", "Timothy McKay"],
["tomaszbi@UMICH.EDU", "Tomasz Biesiadzinski"],
["vsural@UMICH.EDU", "Sinan Ural"],
["ynzhang@UMICH.EDU", "Yuanyuan Zhang"],
["andi@USM.LMU.DE", "Andi Burkert"],
["bocquet@USM.LMU.DE", "Sebastian Bocquet"],
["dgruen@USM.LMU.DE", "Daniel Gruen"],
["dietrich@USM.LMU.DE", "Joerg Dietrich"],
["dolag@USM.LMU.DE", "Klaus Dolag"],
["gangkof@USM.LMU.DE", "Dominik Gangkofner"],
["hoyleb@USM.LMU.DE", "Ben Hoyle"],
["jmohr@USM.LMU.DE", "Joe Mohr"],
["jochen.weller@USM.LMU.DE", "Jochen Weller"],
["mcadolle@USM.LMU.DE", "No Name Available"],
["mkuemmel@USM.LMU.DE", "Martin Kuemmel"],
["paech@USM.LMU.DE", "Kerstin Paech"],
["saro@USM.LMU.DE", "Alex Saro"],
["snigula@USM.LMU.DE", "Jan Snigula"],
["alfredo@USM.UNI-MUENCHEN.DE", "Alfredo Zenteno"],
["gbazin@USM.UNI-MUENCHEN.DE", "Gurvan Bazin"],
["jiayiliu@USM.UNI-MUENCHEN.DE", "Jiayi Liu"],
["stella@USM.UNI-MUENCHEN.DE", "Stella Seitz"],
["JOE@USTW.INFO", "Joe Bernstein"],
["julian@YADA-YADA.NET", "Julian Mayers"]]


search = "371__u:/a/ or 371__u:/e/ or 371__u:/i/ or 371__u:/o/ or 371__u:/u/"



x = perform_request_search(p=search,cc='HepNames')
#x = x[:5]
print len(x)

fileName = 'tmp_junk.out'
output = open(fileName,'w')
for author in authors:
    au = author[1] 
    email = author[0]
    email = email.lower()
    #af = author[2]
    af = ''
    #au = re.sub(r'(.*[A-Z][A-Z]) ([A-Z][a-z].*)',r'\1, \2',au)
    #au = re.sub(r'(.*[a-z]) ([A-Z][A-Z].*)',r'\2, \1',au)
    #au = string.capwords(au)    
    au = re.sub(r'(.*) (\S+)',r'\2, \1', au)
    search = "find a " + au
    x = perform_request_search(p=search,cc='HepNames')
    hepnames_record = get_hepnames_recid_from_email(email)
    #print search,' : ',len(x)
    if len(x) < 1 and not hepnames_record:
        if af:
            bm = bestmatch(af,'ICN')
            aflist = bm[0]
            af = aflist[1]
        create_xml(au,email,af,'DES')
    #output.write(print_record(r,ot=['001','371'],format='xm'))
output.close()


if False:
  authorId = None
  authorName = None
  email = None
  authorId = find_inspire_id_from_record(r)
  authorName = get_fieldvalues(r,'100__a')[0]
  email = get_fieldvalues(r,'371__m')
  if authorName : printLine = authorName
  if email : 
    email = email[0]
    printLine = printLine  + ' | ' + email
  else :
    email = None
  if authorId : printLine = printLine  + ' | ' + authorId
  #print authorName, '|', r, '|', email, '|', authorId
  #printLine = authorName  + ' | ' + email  + ' | ' + authorId
  #print printLine
  search = 'find ea ' + authorName
  y = perform_request_search(p=search,cc='HepNames')
  if len(y) > 1:
    for rr in y:
      print rr,authorName


