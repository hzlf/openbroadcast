#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>

import sys
import time
import os
import socket
import string
import logging

from util import json
  
class DlsClient():

    def __init__(self, dls_host, dls_port, dls_user, dls_pass):
        self.dls_host = dls_host
        self.dls_port = dls_port
        self.dls_user = dls_user
        self.dls_pass = dls_pass

    def set_txt(self, txt):
        logger = logging.getLogger("DlsClient.set_txt")
        
        try:
            print 'connecting to: %s:%s@%s:%s' % (self.dls_user, self.dls_pass, self.dls_host, self.dls_port)
            print
            
            logger.debug('connecting to: %s:%s@%s:%s', self.dls_user, self.dls_pass, self.dls_host, self.dls_port)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((self.dls_host, self.dls_port))
            
            print 'Set STRING'
            s.send('' + '' + str(txt) + "\r\n")
            data = s.recv(1024)
            print data
            
            s.close()
            
            print 'OK'

        except Exception, e:
            dls_status = False
            logger.error("Unable to connect to the dls server - %s", e)
    
        return 

    def set_txt_(self, txt):
        logger = logging.getLogger("DlsClient.set_txt")
        
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
