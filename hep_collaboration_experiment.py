#!/usr/bin/python

import re
from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import print_rec, record_get_field_instances, \
     record_add_field

experiments = {'ALICE':'CERN-LHC-ALICE',
'ATLAS':'CERN-LHC-ATLAS',
'CMS':'CERN-LHC-CMS',
'LHCb':'CERN-LHC-LHCB',
'STAR':'BNL-RHIC-STAR',
'PHENIX':'BNL-RHIC-PHENIX',
'PHOBOS':'BNL-RHIC-PHOBOS',
'BRAHMS':'BNL-RHIC-BRAHMS',
'BESIII':'BEPC-BES-III',
'BaBar':'SLAC-PEP2-BABAR',
'Double Chooz':'DOUBLECHOOZ',
'D0':'FNAL-E-0823',
'CDF':'FNAL-E-0830',
'MINOS':'FNAL-E-0875',
'MiniBooNE':'FNAL-E-0898',
'MIPP':'FNAL-E-0907',
'MINERvA':'FNAL-E-0938',
'SciBooNE':'FNAL-E-0954',
'Mu2e':'FNAL-E-0973',
'MicroBooNE':'FNAL-E-0974',
'DAMIC':'FNAL-E-0987',
'Muon g-2':'FNAL-E-0989',
'ArgoNeuT':'FNAL-T-0962',
'Belle':'KEK-BF-BELLE',
'DES':'DES',
'IceCube':'ICECUBE',
'T2K':'T2K',
'Telescope Array':'TELESCOPE-ARRAY'
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
            if r in done_records:
                break
            output.write(create_xml(r, experiments[key]))
            done_records.append(r)
    output.write('</collection>')
    output.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting'



