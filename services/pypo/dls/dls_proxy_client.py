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
  
class DlsProxyClient():

    def __init__(self, dls_host, dls_port):
        self.dls_host = dls_host
        self.dls_port = dls_port

    def set_txt(self, txt):
        logger = logging.getLogger("DlsProxyClient.set_txt")
        
        try:
            print 'connecting to: %s:%s' % (self.dls_host, self.dls_port)
            print
            
            logger.debug('connecting to: %s:%s', self.dls_host, self.dls_port)
            
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
            logger.error("Unable to connect to the dls proxy - %s", e)

    
        return 
