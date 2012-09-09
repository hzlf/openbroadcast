#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>

"""
Python part of radio playout (bcmon)

This function acts as a gateway between liquidsoap and the obp-api.
Mainliy used to tell the plattform what bcmon/LS does.

Main case: 
 - whenever LS starts playing a new track, its on_metadata callback calls
   a function in ls (notify(m)) which then calls the pythin script here
   with the currently starting filename as parameter 
 - this python script takes this parameter, tries to extract the actual
   media id from it, and then calls back to obp via api to tell about


"""

# python defaults (debian default)
import time
import os
import traceback
from optparse import OptionParser
import sys
import time
import datetime
import logging
import logging.config
import urllib
import urllib2
import string
import telnetlib

import slumber

# additional modules (should be checked)
from configobj import ConfigObj

# custom imports
from util import *
from api import *
#from dls import *



BCMON_VERSION = '0.1'
API_MIN_VERSION = 20110201 # required obp version

API_ENDPOINT = 'http://openbroadcast.ch.node05.daj.anorg.net/api/v1/'
API_AUTH = ("bcmon", "bcmon")

REC_OFFSET = 10
REC_DURATION = 50


#set up command-line options
parser = OptionParser()

# help screeen / info
usage = "%prog [options]" + " - notification gateway"
parser = OptionParser(usage=usage)

#options

parser.add_option("-m", "--metadata", help="Tell daddy what is playing right now", default=False, action="store_true", dest="metadata")
parser.add_option("-t", "--testing", help="Testing...", default=False, action="store_true", dest="testing")
parser.add_option("-C", "--channel", help="Tell daddy what is playing right now", metavar="channel")
parser.add_option("-T", "--title", help="Tell daddy what is playing right now", metavar="title")

# parse options
(options, args) = parser.parse_args()

# configure logging
logging.config.fileConfig("logging.cfg")

# loading config file
try:
    config = ConfigObj('config.cfg')
    TMP_DIR = config['tmp_dir']
   
    BASE_URL = config['base_url']
    API_BASE = config['api_base']
    API_KEY = config['api_key']
    
    API_URL = BASE_URL + API_BASE 
    
except Exception, e:
    print 'error: ', e
    sys.exit()
    
    
class Global:
    def __init__(self):
        print
        
    def selfcheck(self):
        
        if os.geteuid() == 0:
            print '#################################################'
            print "DON'T BE ROOT PLEASE!                            "
            print '#################################################'
            #sys.exit(1)
        
            
         

class Notify:
    
    def __init__(self):

        self.tmp_dir = TMP_DIR 
        
        self.api_key = API_KEY
        self.api_client = ApiClient(API_URL, self.api_key, None)


    def testing(self, options):
        
        print "testing..."
        
        api = slumber.API(API_ENDPOINT, auth=API_AUTH)  
        
        # initial post
        post = api.playout.post({'title': 'my file'})
        print post
    
        # do some seconds of recording, then
        time.sleep(1)
        
        print 'putting sample...'
        # put recorded sample
        put = api.playout(post["id"]).put({'sample': open('samples/cos.mp3')})    
        print put
        
        
    def metadata(self, options):
        
        # dev
        # API_ENDPOINT = 'http://localhost:8000/api/v1/'
        # API_AUTH = ("root", "root")

        exclude_list = 'jingle,dummy'

        print 'Channel:',
        print options.channel
        print 'String:', 
        print options.title
        print
        
        if not options.title:
            print 'no title set.. exit'
        
            sys.exit()
            
        exclude_list = exclude_list.split(',')
        for e in exclude_list:
            if e.lower() in options.title.lower():
                print 'excluded, as contains: %s' % e
                sys.exit()

        

        # Notify the API
        
        api = slumber.API(API_ENDPOINT, auth=API_AUTH)  
        
        # initial post
        post = api.playout.post({'title': options.title, 'channel': options.channel})
        print post
        
        
        # wait a bit befor recording
        print 'sleeping for %s secs' % REC_OFFSET
        time.sleep(REC_OFFSET)
        
        tn = telnetlib.Telnet('127.0.0.1', 1234)
        tn.write("ml0rec.start")
        tn.write("\n")
        tn.write("exit\n")
        

        print 'recording for %s secs' % REC_DURATION
        for i in range(REC_DURATION):
            time.sleep(1)
            print "%s " % (REC_DURATION - i),
            sys.stdout.flush()
        print 
        
        
        tn = telnetlib.Telnet('127.0.0.1', 1234)        
        tn.write("ml0rec.stop")
        tn.write("\n")
        tn.write("exit\n")
        
        
        print "*** RECORDING DONE ***"
        
        sample_path = 'samples/' + 'l0sample.wav'

        print 'putting sample...'
        # put recorded sample
        put = api.playout(post["id"]).put({'status': 2, 'sample': open(sample_path)})    
        print put
        
        sys.exit()    
    
    def old__metadata(self, options):
        logger = logging.getLogger("monitoring")

        print 'Channel:',
        print options.channel
        print 'String:', 
        print options.title
        print

        # Notify the API
        try:
            api = slumber.API("http://localhost:8000/api/v1/", auth=("root", "root"))        
            created = api.playout.post({"title": options.title})
            print created
        
            # id for later use..
            id = created['id']
        
            print id
        except Exception, e:
            print e
        
        # wait a bit befor recording
        print 'sleeping for 5 secs'
        time.sleep(5)
        
        tn = telnetlib.Telnet('127.0.0.1', 1234)

        tn.write("ml0rec.start")
        tn.write("\n")
        tn.write("exit\n")



        print 'sleeping for 20 secs'
        time.sleep(20)

        tn = telnetlib.Telnet('127.0.0.1', 1234)        
        tn.write("ml0rec.stop")
        tn.write("\n")
        
        
        print 'close telnet'
        tn.write("exit\n")
        
        
        
        
        
        """
        try:
            if len(options.title) > 0:
                logger.info("%s: %s", options.channel, options.title)
                
                try:
                    print 'API CONTACT'

                    self.api_client.metadata_change(options.channel, options.title)
                    
                except Exception, e:
                    print e    
                
            else:
                print 'string to short - metadata error'

        except Exception, e:
            print e
       """
        
        sys.exit()  

        

     
            

if __name__ == '__main__':
  
    # initialize
    g = Global()
    #g.selfcheck()
    n = Notify()


run = True
while run == True:
    
    logger = logging.getLogger("bcmon notify")
            
    if options.testing:
        try: n.testing(options)
        except Exception, e:
            print e
        sys.exit()  
            
    if options.metadata:
        try: n.metadata(options)
        except Exception, e:
            print e
        sys.exit()  


    sys.exit()
