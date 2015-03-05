import time
import sys
import re

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def main(recids):
    icount = 1
    for recid in recids:
        recid = str(recid)
        title = get_fieldvalues(recid, '245__a')[0]
        title = title[:50]
        try:
            contact_email = get_fieldvalues(recid, '270__m')[0]
        except:
            contact_email = 'hoc@fnal.gov'
        try:
            contact_name = get_fieldvalues(recid, '270__p')[0]
            if "," in contact_name:
                contact_name = " ".join(contact_name.split(", ")[::-1])
            #contact_name = contact_name
        except:
            contact_name = 'Sir or Madam'
        if contact_email == 'employ@fnal.gov':
            contact_email = 'kvb@fnal.gov'
            #contact_email = 'cnbrown@fnal.gov'
        elif contact_email == 'recruitment.service@cern':
            contact_email = 'Caroline.Dumont@cern'
        #contact_email = 'hoc@fnal.gov'
        #contact_email = "hoc3426@gmail.com"
        #contact_email = "atkinson@fnal.gov"
        #contact_email = "hepnames@slac.stanford.edu"
        #contact_email = "cleggm1@fnal.gov"
        #contact_email = "cleggm1@gmail.com"
        #contact_email = "bhecker@slac.stanford.edu"
        #contact_email = "thorsten.schwander@gmail.com"


        deadline = get_fieldvalues(recid, '046__i')[0]
        print icount, '/', len(recids)
        print 'recid = ', recid
        print 'title = ', title
        print 'email = ', contact_email
        print 'name  = ', contact_name
        print 'dline = ', deadline
        print ' '
        try:
            send_jobs_mail(recid, contact_email, contact_name, title,
                           deadline)
        except:
            print 'PROBLEM'
            print recid, contact_email, contact_name, title, deadline
        icount += 1


def send_jobs_mail(recid, email, name, title, deadline):
    subject = 'posting in HEPJobs ' + recid + ' [' + title + ']'
    subject_sender = 'Your ' + subject
    subject_retain = 'Retain ' + subject
    subject_remove = 'Remove ' + subject
    link = "http://inspirehep.net/record/" + recid
    html = \
"""<html>
<head></head>
<body>
<p>
Dear %(name)s,
<br /><br />
The HEPJobs listing for your position:<br />
<a href=\"%(link)s\">%(link)s</a><br />
   %(title)s<br />
has an expired deadline: %(deadline)s.
<br /><br />
Please click the appropriate link below to let us know if this position is:
<br /><br />
a) <a href=\"mailto:jobs@inspirehep.net?subject=%(subject_retain)s
&body=Retain %(link)s             The new deadline is:\">still vacant</a>
[you would be interested in new applications]
<br /><br />
OR
<br /><br />
b) <a href=\"mailto:jobs@inspirehep.net?subject=%(subject_remove)s
&body=Remove %(link)s\">no longer vacant</a>
[you do not want any more applications].
<br /><br />
Generally we do not remove jobs simply because the deadline has expired
because deadlines are often extended. You can give us a new deadline or
just tell us the position is still vacant and we will simply extend the
deadline 3 months check back with you then.
<br /><br />
The INSPIRE HEPJobs database receives thousands of hits a day from
people in the high energy physics community. Our goal is to make it
useful and efficient for people both advertising and seeking positions.
We therefore wish to keep our listings as current as possible.
<br /><br />
Your assistance is greatly appreciated.
<br /><br />
Best Wishes,
<br /><br />
The INSPIRE HEPJobs Team<br />
jobs@inspirehep.net<br />
Follow INSPIRE on Twitter: https://twitter.com/inspirehep
</p>
</body>
</html>
"""% {"link":link, "title":title, "deadline":deadline,
      "subject_remove":subject_remove, "subject_retain":subject_retain,
      "name":name}

    text = BeautifulSoup(html).text
    text = re.sub('click the appropriate link below to ', '', text)
    #print html
    #print text

    hepjobs_email = '"HEPJobs Database Administrator" <jobs@inspirehep.net>'

    # Create message container - the correct MIME type is
    # multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject_sender
    msg['From'] = hepjobs_email
    msg['To'] = email

    # Record the MIME types of both parts - text/plain and text/html.
    #part1 = MIMEText(text, 'plain')
    part1 = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
    #part2 = MIMEText(html, 'html')
    part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message,
    # in this case the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    stmp_email = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    stmp_email.sendmail(hepjobs_email, email, msg.as_string())
    stmp_email.quit()

def find_jobs():
    region = ''
    date = time.strftime('%Y-%m')
    print """
    Region:
    1 = Asia/Australasia
    2 = Europe
    3 = Africa
    4 = Middle East
    5 = South America
    6 = North America
    7 = All
    """
    region = int(raw_input("Please choose a region "))
    if region == 1:
        region = '/asia/'
    elif region == 2:
        region = 'Europe'
    elif region == 3:
        region = 'Africa'
    elif region == 4:
        region = 'Middle East'
    elif region == 5:
        region = "'South America'"
    elif region == 6:
        region = "'North America'"
    elif region == 7:
        region = '*'
    else:
        print region, "is not a valid choice."
    print """
    Chose a date, e.g. 2014, 2014-05, etc.
    """
    print "    Default value is %s\n"%date
    date_input = raw_input("Your date? ")
    if len(date_input) > 3:
        date = date_input
    search = '043:' + region + r' 270__m:/\@/ +046:2000->' + date
    print search
    result = perform_request_search(p=search, cc='Jobs')
    log = open('jobs.log', 'a')
    date_time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    date_time_stamp = date_time_stamp + ' ' + search + ' : '\
                    + str(len(result)) + '\n'
    log.write(date_time_stamp)
    log.close()
    return result

if __name__ == '__main__':
    RECIDS = []
    try:
        RECID = int(sys.argv[1:][0])
        RECIDS.append(RECID)
    except:
        RECIDS = find_jobs()
    try:
        main(RECIDS)
    except KeyboardInterrupt:
        print 'Exiting'


