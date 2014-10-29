import os
import re
import time

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_record
from invenio.search_engine import get_fieldvalues
from invenio.mailutils import send_email

def main(region, date):
    search = '043:' + region + ' 270__m:/\@/ +046:2000->' + date
    print search

    x = perform_request_search(p=search,cc='Jobs')
    number = len(x)
    print number
    log = open('jobs.log','a')
    dateTimeStamp = time.strftime('%Y-%m-%d %H:%M:%S')
    dateTimeStamp = dateTimeStamp + ' ' + search + ' : ' + str(len(x)) + '\n'
    log.write(dateTimeStamp)
    log.close()
    icount = 1
    for r in x:
        recid = str(r)
        print icount, '/', number
        print 'recid = ',recid
        title = get_fieldvalues(r,'245__a')[0]
        title = title[:50]
        email = get_fieldvalues(r,'270__m')[0]
        email = email.replace('employ@fnal.gov','kvb@fnal.gov')
        email = email.replace('recruitment.service@cern','Caroline.Dumont@cern')
        #email = 'hoc@fnal.gov'
        deadline = get_fieldvalues(r,'046__i')[0]
        print 'title = ',title
        print 'email = ',email
        print 'dline = ',deadline
        print ' '

        sender  = '"HEPJobs Database Administrator" <jobs@inspirehep.net>'
        subject = 'Your job posting in HEPJobs [' + title + '] ' + recid
        text = "Hello,\n\n"
        text = text + 'HEPJobs listing for your position "' + title + '":'
        text = text + "\nhttp://inspirehep.net/record/" + recid + "\n"
        text = text + "\n"
        text = text + "\nYour job posting has an expired deadline. \n\
Please reply to this email and let us know if this position is:\n\
\n\
a) still vacant [that is, you would be interested in new applications]\n\
or\n\
b) no longer vacant [you do not want any more applications].\n\
\n\
Generally we do not remove jobs simply because the deadline has expired because deadlines\n\
are often extended. You can give us a new deadline or just tell us the position is still\n\
vacant and we will simply extend the deadline 3 months check back with you then.\n\
\n\
The INSPIRE HEPJobs database receives thousands of hits a day from people in the high\n\
energy physics community. Our goal is to make it useful and efficient for people both\n\
advertising and seeking positions. We therefore wish to keep our listings as current as\n\
possible. Your assistance is greatly appreciated.\n\
\n\
Best Wishes,\n\
\n\
The INSPIRE HEPJobs Team\n\
jobs@inspirehep.net\n\
\n\
"
        send_email(sender,email,subject,text,header='', footer='')
        icount += 1


if __name__ == '__main__':
    region = ''
    date = time.strftime('%Y-%m')
    print("""
    Region:
    1 = Asia/Australasia
    2 = Europe
    3 = Africa
    4 = Middle East
    5 = South America
    6 = North America
    """)
    region = int(raw_input("Please choose a region "))
    if region == 1 : region = '/asia/'
    elif region == 2 : region = 'Europe'    
    elif region == 3 : region = 'Africa'
    elif region == 4 : region = 'Middle East'
    elif region == 5 : region = "'South America'"
    elif region == 6 : region = "'North America'"
    else:
        print region, "is not a valid choice."
    print("""
    Chose a date, e.g. 2014, 2014-05, etc.
    """)
    print "    Default value is %s\n" %date
    date_input = raw_input("Your date? ")
    if len(date_input) > 3:
        date = date_input
    try:
        main(region, date)
    except KeyboardInterrupt:
        print 'Exiting'

