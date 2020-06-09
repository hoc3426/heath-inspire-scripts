#!/usr/bin/python

import re
from invenio.search_engine import perform_request_search, get_record, \
                                  get_fieldvalues
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field

experiments = {

'ALICE':'CERN-LHC-ALICE',
'AMANDA':'AMANDA',
'ANNIE':'FNAL-E-1063',
'ANTARES':'ANTARES',
'ArgoNeuT':'FNAL-T-0962',
'ARIANNA':'ARIANNA',
'ATLAS':'CERN-LHC-ATLAS',
'BaBar':'SLAC-PEP2-BABAR',
'Baikal-GVD':'BAIKAL-GVD',
'Belle':'KEK-BF-BELLE',
'BESIII':'BEPC-BES-III',
'Borexino':'BOREXINO',
'BRAHMS':'BNL-RHIC-BRAHMS',
'CDF':'FNAL-E-0830',
'CMS':'CERN-LHC-CMS',
'COSINE-100':'COSINE-100',
'CUORE':'CUORE',
'D0':'FNAL-E-0823',
'DARWIN':'DARWIN',
'Daya Bay':'DAYA-BAY',
#'DAMIC':'FNAL-E-0987',
'Delphes':'Delphes',
'DES':'DES',
'Double Chooz':'DOUBLECHOOZ',
'DUNE':'DUNE',
'EDELWEISS':'EDELWEISS',
'Event Horizon Telescope':'EHT',
'FAMU':'FAMU',
'FAST':'FAST',
'Fermilab Lattice':'LATTICE-FERMILAB',
'GAMBIT':'GAMBIT',
'GAPS':'GAPS',
'Geant4':'Geant4',
'GERDA':'GERDA',
'HAWC':'HAWC',
'IceCube':'ICECUBE',
'LHCb':'CERN-LHC-LHCB',
'LIGO Scientific':'LIGO',
'LUX':'LUX',
'MadGraph5_aMC@NLO':'MadGraph5_aMC@NLO',
'MAGIC':'MAGIC',
'MicroBooNE':'FNAL-E-0974',
'MINERvA':'FNAL-E-0938',
'MiniBooNE':'FNAL-E-0898',
'MINOS':'FNAL-E-0875',
'MINOS+':'FNAL-E-1016',
'MILC':'LATTICE-MILC',
'MIPP':'FNAL-E-0907',
'Mu2e':'FNAL-E-0973',
'Muon g-2':'FNAL-E-0989',
'NA61/SHINE':'CERN-NA-061',
'NEXT':'NEXT',
'NNPDF':'NNPDF',
'NOvA':'FNAL-E-0929',
'NuSTEC':'NuSTEC',
'PHENIX':'BNL-RHIC-PHENIX',
'PHOBOS':'BNL-RHIC-PHOBOS',
'PIENU':'TRIUMF-1072',
'POWHEG':'POWHEG',
'PROSPECT':'PROSPECT',
'PTOLEMY':'PTOLEMY',
'PYTHIA':'PYTHIA',
'SciBooNE':'FNAL-E-0954',
'STAR':'BNL-RHIC-STAR',
'STEREO':'STEREO',
'T2K':'T2K',
'Telescope Array':'TELESCOPE-ARRAY',
'TOTEM':'CERN-LHC-TOTEM',
'UKQCD':'LATTICE-UKQCD',
'USQCD':'LATTICE-USQCD',
'Virgo':'VIRGO'
}

def create_xml(recid, experiment):
    record = get_record(recid)
    correct_record = {}
    common_tags = {}
    experiment_tag = {}
    experiment_tag['693__'] = [('e', experiment)]
    tags = ['693__','710__']
    #for tag in tags:
    #    field_instances = record_get_field_instances(record, tag[0:3], tag[3], tag[4])
    #    for field_instance in field_instances:
    #        correct_subfields = []
    #        for code, value in field_instance[0]:
    #            correct_subfields.append((code, value))
    #        record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
    #            subfields=correct_subfields)
    record_add_field(correct_record, '693', '_', '_', \
                     subfields=experiment_tag['693__'])
    record_add_field(correct_record, '001', controlfield_value=str(recid))
    for key in common_tags:
        tag = key
        record_add_field(correct_record, tag[0:3], tag[3], tag[4], \
            subfields=common_tags[key])
    return print_rec(correct_record)

def main():
    filename = 'tmp_' + __file__
    filename = re.sub('.py', '_append.out', filename)
    output = open(filename,'w')
    output.write('<collection>')
    done_records = []
    for key in experiments:
        search = '710__g:"' + key + '" -693__e:' + experiments[key]
        if re.search('CDF', key): 
            search = search + ' -693__e:FNAL-E-0741'
        if re.search('D0', key):  
            search = search + ' -693__e:FNAL-E-0740'
            search = search + ' -980__a:D0-PRELIMINARY-NOTE'
        x = perform_request_search(p=search,cc='HEP')
        for r in x:
            #if r in done_records:
            #    break
            if 'BNL-E-0821' in get_fieldvalues(r, '693__e'):
                continue
            output.write(create_xml(r, experiments[key]))
            done_records.append(r)
    output.write('</collection>')
    output.close()
    print filename   

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'



