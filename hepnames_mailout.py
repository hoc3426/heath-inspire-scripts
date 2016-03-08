# -*- coding: utf-8 -*-
"""
This module finds people in HEPNames to send email to
asking them to send us their ORCID ID.
"""

VERBOSE = True
RECIDS = False

#from fermi_theory_inspire_ids import RECIDS
from hep_convert_email_to_id import get_hepnames_anyid_from_recid

import time
import sys
import re

from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LINK_BLOG = "http://blog.inspirehep.net/2015/04/"
LINK_BLOG += "what-is-orcid-and-how-can-it-help-you.html"

def main(recids):
    """
    Gets name and email from each HEPNames record.
    """

    if VERBOSE:
        print recids

    icount = 1
    for recid in recids:
        recid_str = str(recid)
        recid_int = int(recid)
        if re.search(r'INSPIRE-', recid_str):
            search = '035__a:' + recid_str
            result = perform_request_search(p=search, cc='HepNames')
            recid = result[0]
            recid_str = str(recid)
            recid_int = int(recid)
        if get_hepnames_anyid_from_recid(recid_int, 'ORCID'):
            print recid_str, 'already has an ORCID\n'
            icount += 1
            continue
        try:
            contact_email = get_fieldvalues(recid_int, '371__m')[0]
        except:
            contact_email = 'hoc@fnal.gov'
        try:
            contact_name = get_fieldvalues(recid_int, '100__a')[0]
            if "," in contact_name:
                contact_name = " ".join(contact_name.split(", ")[::-1])
        except:
            contact_name = 'Sir or Madam'
        #contact_email = 'hoc@fnal.gov'
        #contact_email = "hoc3426@gmail.com"
        #contact_email = "atkinson@fnal.gov"
        #contact_email = "hepnames@slac.stanford.edu"
        #contact_email = "cleggm1@fnal.gov"
        #contact_email = "cleggm1@gmail.com"
        #contact_email = "bhecker@slac.stanford.edu"
        #contact_email = "thorsten.schwander@gmail.com"

        print icount, '/', len(recids)
        print 'recid = ', recid_str
        print 'email = ', contact_email
        print 'name  = ', contact_name
        print ' '
        try:
            send_jobs_mail(recid_str, contact_email, contact_name)
            time.sleep(1)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            print 'PROBLEM sending mail to:'
            print recid, contact_email, contact_name, '\n'
        icount += 1


def send_jobs_mail(recid, email, name):
    """
    Generates an email message and sends it out.
    """

    subject = 'record in INSPIRE HEPNames ' + recid
    subject_sender = 'Adding an ORCID to your ' + subject
    link = "http://inspirehep.net/record/" + recid
    html = \
"""<html>
<head></head>
<body>
<p>
Dear %(name)s,
<br /><br />
Your HEPNames record:<br />
<a href=\"%(link)s\">%(link)s</a><br />
Does not appear to have an <a href=\"http://orcid.org\">ORCID ID</a>
matched to it.
<br /><br />
If you do not have an ORCID ID you can obtain one at:
<a href=\"http://orcid.org/register\">http://orcid.org/register</a>
<br /><br />
Once you have an ORCID ID please just reply to this email and let us know
what it is so that we can add it to your HEPNames record.
<br /><br />
For more information on ORCID and its importance to INSPIRE, please see
our recent <a href=\"%(link_blog)s\">blog post</a>.
<br /><br />
Your assistance is greatly appreciated.
<br /><br />
Best Wishes,
<br /><br />
The INSPIRE Authors Team<br />
authors@inspirehep.net<br />
Follow INSPIRE on Twitter: https://twitter.com/inspirehep
</p>
</body>
</html>
"""% {"link":link, "link_blog":LINK_BLOG, "name":name}

    text = BeautifulSoup(html).text
    text = re.sub('click the appropriate link below to ', '', text)
    #print html
    #print text

    hepnames_email = '"HEPNames Database Administrator" '
    hepnames_email += '<authors@inspirehep.net>'

    # Create message container - the correct MIME type is
    # multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject_sender
    msg['From'] = hepnames_email
    msg['To'] = email
    msg['X-Auto-Response-Suppress'] = 'OOF, DR, RN, NRN'

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
    stmp_email.sendmail(hepnames_email, email, msg.as_string())
    stmp_email.quit()

def find_records():
    """
    Finds records to send email to.
    """

    print """
    Let's do a HEPNames search in INSPIRE format
    """
    search_input = raw_input("Your search? ")
    if len(search_input) > 3 and re.search(r':', search_input):
        search = search_input
    else:
        print "That's not a search. Game over."
        return None
    search += ' 371__m:/\@/'
    search += ' -035__9:ORCID'
    search += ' -001:1004158'
    print search
    result = perform_request_search(p=search, cc='HepNames')
    if len(result) > 0:
        log = open('hepnames_mailout.log', 'a')
        date_time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        date_time_stamp = date_time_stamp + ' ' + search + ' : '\
                    + str(len(result)) + '\n'
        log.write(date_time_stamp)
        log.close()
        return result
    else:
        print "No results found."
        return None

if __name__ == '__main__':
    if not RECIDS:
        RECIDS = []
        try:
            RECID = int(sys.argv[1:][0])
            RECIDS.append(RECID)
        except:
            RECIDS = find_records()
    try:
        if RECIDS:
            main(RECIDS)
        else:
            print "Nothing to do."
    except KeyboardInterrupt:
        print 'Exiting'


