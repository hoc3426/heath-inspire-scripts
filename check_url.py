import sys
import urllib2

def checkURL(url):
     x = 0
     #print url
     try:
          req = urllib2.urlopen(url)

     except IOError, (errno, strerror):
         print "Error with: ", url
         #print "I/O error(%s): %s" % (errno, strerror)
     except ValueError:
         print "Error with: ", url
         print "Could not convert data to an integer."
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


