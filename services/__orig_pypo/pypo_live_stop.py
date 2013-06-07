#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>


# python defaults (debian default)
import time
import os
import sys
from optparse import *
import time
import datetime
import logging
import logging.config
import string

# additional modules (should be checked)
from configobj import ConfigObj

# custom imports
from util import *
from obp import *



PYPO_VERSION = '0.9'
OBP_MIN_VERSION = 2010040501 # required obp version

LS_HOST = '127.0.0.1'


#set up command-line options
parser = OptionParser()

# help screeen / info
usage = "%prog [options]" + " - archiver"
parser = OptionParser(usage=usage)

parser.add_option("-t", "--time", help="Time to wait until stop", metavar="time")

# parse options
(options, args) = parser.parse_args()

# configure logging
logging.config.fileConfig("logging.cfg")


    
    
class Global:
    def __init__(self):
        print
        
    def selfcheck(self):

        
        if os.geteuid() == 0:
            print '#################################################'
            print "DON'T BE ROOT PLEASE!                            "
            print '#################################################'
            sys.exit(1)
        

class Timer:
    def __init__(self):
        print 
        
    def stop(self, t):
        
        try:
            t = float(t)
            
        except Exception, e:
            print e
            t = False

        if t:
            # sleep as long as neccessary
            while t > 0:
                
                if t < 300:
                    print 'Live input stops in:',
                    print t
                    
                t-=1
                time.sleep(1)
            
            #time.sleep(t)
            
            # fire the telnet commands
            
            print
            print '#########################################'
            print '# Time over - Stop live input           #'
            print '#########################################'
            print
            
            tn = telnetlib.Telnet(LS_HOST, 1234)
            
            print 'live.active 0'
            tn.write("live.active 0")
            tn.write("\n")
            time.sleep(15)
            print 'live_in.stop'
            tn.write("live_in.stop")
            tn.write("\n")
            tn.write("exit\n")
            
            print 'done'
            
            print tn.read_all()
            
        sys.exit()
        
            

if __name__ == '__main__':
  
    print
    print '#########################################'
    print '#           *** pypo  ***               #'
    print '#         pypo stream timer             #'
    print '#########################################'
    print
    
    # initialize
    g = Global()
    g.selfcheck()
    
    t = Timer()


run = True
while run == True:
            
    if options.time:
        try: t.stop(options.time)
        except Exception, e:
            print e
        sys.exit()  
        
    sys.exit()
