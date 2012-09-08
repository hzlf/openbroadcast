#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>

import sys
import time
import os
import socket
import string
import logging
import logging.config

import atexit

import socket
import threading
import SocketServer

from optparse import *

from configobj import ConfigObj

from util import json


#set up command-line options
parser = OptionParser()

# help screeen / info
usage = "%prog [options]" + " - python playout system | dls proxy"
parser = OptionParser(usage=usage)

#options
parser.add_option("-p", "--proxy", help="Run proxy", default=False, action="store_true", dest="proxy")

# parse options
(options, args) = parser.parse_args()



# configure logging
logging.config.fileConfig("logging.cfg")

HOST, PORT = '127.0.0.1', 4000
TEXT_DEFAULT = 'www.openbroadcast.ch - user generated radio'

str_dls = TEXT_DEFAULT
TIME_SLEEP = 30

# loading config file
try:
    config = ConfigObj('config.cfg')
    TMP_DIR = config['tmp_dir']
    BASE_URL = config['base_url']
    OBP_API_BASE = BASE_URL + 'mod/medialibrary/'
    
    OBP_STATUS_URL = OBP_API_BASE + 'status/version/json'
    OBP_API_KEY = config['obp_api_key']
    
    DLS_HOST = config['dls_host']
    DLS_PORT = int(config['dls_port'])
    DLS_USER = config['dls_user']
    DLS_PASS = config['dls_pass']
    
except Exception, e:
    print 
    print 'ERROR PARSINF CONFIG FILE!'
    print 'error: ', e
    print 'EXITING NOW'
    print 
    
    sys.exit()



    
    

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class DlsProxy(SocketServer.BaseRequestHandler):

    def handle(self):
        global str_dls
        global time_sleep
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "%s wrote:" % self.client_address[0]
        print self.data
        str_dls = self.data
        time_sleep = 1
        # just send back the same data, but upper-cased
        self.request.send(self.data.upper())
        
        
  
class DlsClient():

    def __init__(self, dls_host, dls_port, dls_user, dls_pass):
        self.dls_host = dls_host
        self.dls_port = dls_port
        self.dls_user = dls_user
        self.dls_pass = dls_pass

    def set_txt(self, txt):
        logger = logging.getLogger("DlsClient.set_txt")
        
        global str_dls
        
        try:
            print 'connecting to: %s:%s@%s:%s' % (self.dls_user, self.dls_pass, self.dls_host, self.dls_port)
            print
            
            logger.debug('connecting to: %s:%s@%s:%s', self.dls_user, self.dls_pass, self.dls_host, self.dls_port)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((self.dls_host, self.dls_port))
            
            # Handshake
            print 'Handshake',
            s.send('RS_DLS_CLIENT' + '' + "\r\n")
            data = s.recv(1024)
            print data
            
            # Version
            print 'Version',
            s.send('RS_DLS_VERSION' + ' 1' + "\r\n")
            data = s.recv(1024)
            print data
            
            # Authentication
            print 'Authentication',
            s.send('SERVICE' + ' OPENBRO+' + "\r\n")
            s.send('PASSWORD' + ' OPENBRO+' + "\r\n")
            data = s.recv(1024)
            print data
            
            # Update text
            print 'Clear DLS'
            s.send('CLEAR_DLS' + '' + "\r\n")
            data = s.recv(1024)
            print data
            
            print 'Set DLS'
            s.send('SET_DLS' + ' ' + str(txt) + "\r\n")
            data = s.recv(1024)
            print data
            
            s.close()
            
            print 'OK'   
    
        except Exception, e:
            dls_status = False
            logger.error("Unable to connect to the dls server - %s", e)
    
        return 








if __name__ == '__main__':
  
    print
    print '#########################################'
    print '#              *** pypo ***             #'
    print '#             pypo dls proxy            #'
    print '#########################################'
    print
    
    c = DlsClient(DLS_HOST, DLS_PORT, DLS_USER, DLS_PASS)


    


run = True
while run == True:
    
    logger = logging.getLogger("dls_proxy")
    
    loops = 0
    
    do_exit = False
      
    while options.proxy:

        try: 

            p = ThreadedTCPServer((HOST, PORT), DlsProxy)
            p_thread = threading.Thread(target=p.serve_forever)
            p_thread.setDaemon(True)
            p_thread.start()
            p_thread.setName('ProxyServerThread')
            print "Server loop running in thread:", p_thread.getName()
            
        except Exception, e:
            print 'PROXY ERROR!! WILL EXIT NOW:('
            print e
            sys.exit()
            
            
        while run == True:
            
            try:
                print 'push loop'
                print str_dls
                c.set_txt(str_dls)
                
                time_sleep = TIME_SLEEP
                
                logger.info('push loop %s', loops)
                loops += 1
                while time_sleep > 0:
                    time.sleep(1)
                    time_sleep -= 1
                    print '.',
                    sys.stdout.flush()
                    
                time_sleep = TIME_SLEEP
                

            except KeyboardInterrupt:
                print "Shutdown requested...exiting"
                print p_thread.isAlive()
                p_thread.join(.1)
                do_exit = True
                
            except Exception, e:
                print "An unexpected exception was encountered: %s" % str(e)
                sys.exit(1)
                
            if do_exit == True:
                sys.exit(0)
                
        
        
            

    sys.exit(0)
    
# shutdown on exit
atexit.register(p_thread.stop())
