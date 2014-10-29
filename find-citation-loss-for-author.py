#!/usr/bin/python

from invenio.search_engine import run_sql, search_unit
from invenio.intbitset import intbitset
from datetime import datetime, timedelta
import sys

def main(exactauthor, days):

    if days.isdigit():
        days = int(days)
    else:
        print "WARNING: number of days not recognized as integer, using 1 instead"
        days = 1
    startdate = datetime.today() - timedelta(days=days)

    print "\n* Looking at citation loss for %s since %s *\n" % (exactauthor, startdate)

    result = citationloss(exactauthor, startdate)
    if result:
        create_report(result)
    else:
        print "nothing lost in the past %d days" % days
    print "\n* ALL DONE *\n"

def citationloss(exactauthor, startdate):

    recordsofauthor = search_unit(exactauthor, f='exactauthor')
    removedcitations = intbitset([i[0] for i in \
                                  run_sql('select citee from rnkCITATIONLOG where action_date>"%s"' % startdate)])

    lossoverlap = recordsofauthor & removedcitations
    if lossoverlap:
        recsaffected = run_sql('select citer,citee,action_date from rnkCITATIONLOG where citee in (' \
                        + ', '.join([str(i) for i in lossoverlap]) \
                           + ') and action_date>"%s"' % (startdate))
        return recsaffected
    return None

def create_report(recsaffected):
    for r in recsaffected:
        print "%d\t%d\t%s" % r


if __name__ == "__main__":
    if len(sys.argv) > 2:
        try:
            main(str(sys.argv[1]), str(sys.argv[2]))
        except KeyboardInterrupt:
            print 'Exiting on keyboard interrupt'
    else:
        print """
        not enough arguments to work with, use as:

        \t %s "<exactauthor> <number of days to look back>"

        """ % sys.argv[0]
