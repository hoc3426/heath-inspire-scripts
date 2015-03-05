from invenio.search_engine import perform_request_search, run_sql

RECID = 345071
RECID = 590673

x=perform_request_search(p='refersto:recid:590673')

print 'Number of citations from refersto search:', len(x)

y=run_sql('select citer from rnkCITATIONDICT where citee="590673"')

print 'Number of citations from CITATIONDICT:   ', len(y)

discrepancy = set([r[0] for r in y])-set(x)
print 'Records causing the discrepancy: ', discrepancy

from invenio.search_engine import get_record

value_970 = get_record(716584)['970']
print 'Records this is linked to:', value_970

