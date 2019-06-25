import sys
import urllib2
import httplib

def checkURL(url):
     x = 0
     #print url
     try:
          req = urllib2.urlopen(url)
     except urllib2.URLError:
         print "Error with getting to: ", url
         return None
     except IOError, (errno, strerror):
         #print "Error with: ", url
         print "I/O error(%s): %s" % (errno, strerror)
         return None
     except ValueError:
         print "Error with: ", url
         print "Could not convert data to an integer."
         return None
     except httplib.BadStatusLine:
         print "BadStatusLine error with: ", url
         return None
     except:
         print "Error with: ", url
         print "Unexpected error:", sys.exc_info()[0]
         raise
#     except urllib2.HTTPError as e:
#          print e.code
         return 0
     s = len(req.read())
     t = req.headers.getsubtype()
     if s > 10000:
       if t == 'pdf' : x = 1
     return x


