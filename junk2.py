#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unicodedata
import re
import os
import string

from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field

def create_xml(experiment,spks,title):
    common_fields = {}
    common_tags = {}
   
    common_tags['980__'] = [('a', 'EXPERIMENT')]
    common_tags['702__'] = [('a', spks), ('z', 'current')]
    common_tags['245__'] = [('a', title)]
    common_tags['119__'] = [('a', experiment),('u', 'J-PARC')]
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

fileName = 'tmp_junk.out'
output = open(fileName,'w')
for author in authors:
    ex = author[0]
    au = author[1] 
    af = author[2]
    ti = author[3]
    if not re.search("\,", au) : au = re.sub(r'(.*\.)(.*)',r'\2, \1',au)
    ex = re.sub(r'E(.*)',r'JPARC-E-0\1',ex)
    create_xml(ex,au,ti)
output.close()


