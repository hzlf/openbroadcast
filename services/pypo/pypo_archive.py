#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>


# python defaults (debian default)
import time
import os
import sys
import traceback
from optparse import *
import time
import datetime
import logging
import logging.config
import string
import pickle

#from poster.encode import multipart_encode
#from poster.streaminghttp import register_openers

from util import urllib2_file
import urllib2

from shutil import *

# additional modules (should be checked)
from configobj import ConfigObj

# custom imports
from util import *
from obp import *



PYPO_VERSION = '0.9'
OBP_MIN_VERSION = 2010040501 # required obp version


#set up command-line options
parser = OptionParser()

# help screeen / info
usage = "%prog [options]" + " - archiver"
parser = OptionParser(usage=usage)

parser.add_option("-m", "--move", help="Move the current recording", default=False, action="store_true", dest="move")

parser.add_option("-U", "--user-id", help="The user id", metavar="user_id")
parser.add_option("-P", "--playlist-id", help="The playlist id", metavar="playlist_id")
parser.add_option("-T", "--transmission-id", help="The transmission id", metavar="transmission_id")

# parse options
(options, args) = parser.parse_args()

# configure logging
logging.config.fileConfig("logging.cfg")

# loading config file
try:
    config = ConfigObj('config.cfg')
    TMP_DIR = config['tmp_dir']
    ARCHIVE_DIR = config['archive_dir']
    BASE_URL = config['base_url']
    OBP_API_BASE = BASE_URL + 'mod/medialibrary/'
    
    OBP_STATUS_URL = OBP_API_BASE + 'status/version/json'
    OBP_API_KEY = config['obp_api_key']
    
except Exception, e:
    print 'error: ', e
    sys.exit()
    
    
class Global:
    def __init__(self):
        print
        
    def selfcheck(self):
        
        self.archive_dir = ARCHIVE_DIR
        
        self.api_auth = urllib.urlencode({'api_key': OBP_API_KEY})
        self.api_client = ApiClient(OBP_API_BASE, self.api_auth)
        
        if os.geteuid() == 0:
            print '#################################################'
            print "DON'T BE ROOT PLEASE!                            "
            print '#################################################'
            sys.exit(1)
        
        obp_version = self.api_client.get_obp_version()
        
        if obp_version == 0:
            print '#################################################'
            print 'Unable to get OBP version. Is OBP up and running?'
            print '#################################################'
            print
            sys.exit()
         
        elif obp_version < OBP_MIN_VERSION:
            print 'OBP version: ' + str(obp_version)
            print 'OBP min-version: ' + str(OBP_MIN_VERSION)
            print 'pypo not compatible with this version of OBP'
            print
            sys.exit()
         
        else:
            print 'OBP API: ' + str(OBP_API_BASE)
            print 'OBP version: ' + str(obp_version)
            print 'OBP min-version: ' + str(OBP_MIN_VERSION)
            print 'pypo is compatible with this version of OBP'
            print

class Archive:
    def __init__(self):

        self.tmp_dir = TMP_DIR
        self.archive_dir = ARCHIVE_DIR
        self.archive_file = self.archive_dir + 'archive'
        
        self.api_auth = urllib.urlencode({'api_key': OBP_API_KEY})
        self.api_client = ApiClient(OBP_API_BASE, self.api_auth)


    def load_archive(self):
        
        try:
            archive_file = open(self.archive_file, "r")
            archive = pickle.load(archive_file)
            archive_file.close()
            
        except Exception, e:
            logger.error('%s', e)
            archive = []

        self.archive = archive


    def save_archive(self):
        
        try:
            archive_file = open(self.archive_file, "w")
            pickle.dump(self.archive, archive_file)
            archive_file.close()
            
        except Exception, e:
            logger.error('%s', e)


    
    
    
    
    def move(self, options):
        logger = logging.getLogger("move")

        tnow = time.localtime(time.time())


        print '#################################################'
        print '# move recorded file                            #'
        print '#################################################'      


        src = self.archive_dir + 'couchcaster_recorded.mp3'
        dst = self.archive_dir + '%s_%s_%s.mp3' % (options.user_id, options.playlist_id, options.transmission_id)

        print 'src',
        print src
        print 'dst',
        print dst
        
        
        self.load_archive()
        
        
        if options.transmission_id in self.archive:
            print 'already archived'
        
        else:
        
            fsize = 0
            if os.path.isfile(src): 
                    
                try:
                    #shutil.move(src, dst)
                    shutil.copy2(src, dst)
                    
                except Exception, e:
                    logger.error("%s", e)
                    print e
                    
                try: 
                    fsize = os.path.getsize(dst)
                    
                except Exception, e:
                    logger.warning("%s", e)
                    print e
                
            if fsize > 0:
                
                print 'Size: %s' % fsize
                print 'aight!!'
            
            
                try:
                    self.upload(dst, options)
            
                except Exception, e:
                    logger.error("%s", e)
                    print e
        
        
        sys.exit()  

        

    
    def upload(self, src, options):
        logger = logging.getLogger("upload")
        
        print 'upload recorded file'
        
        data = {"file": open(src), \
                 "user_id" : options.user_id, \
                 "playlist_id" : options.playlist_id, \
                 "transmission_id" : options.transmission_id, \
                 "api_key" : OBP_API_KEY}
        
        # compose api url - should actually be handled by the api client module
        url = OBP_API_BASE + 'api/pypo/put_media'
        
        try:
            response = urllib2.urlopen(url, data).read()
            response_json = json.read(response)
            
            if response_json['status'] == True:
                os.remove(src)
                
                self.archive.append(options.transmission_id)
                self.save_archive()
                
                print 'OK'
        
        except Exception, e:
            logger.error("%s", e)
            print e
            
        
            

if __name__ == '__main__':
  
    print
    print '#########################################'
    print '#           *** pypo  ***               #'
    print '#       pypo archive uploader           #'
    print '#########################################'
    print
    
    # initialize
    g = Global()
    g.selfcheck()
    a = Archive()


run = True
while run == True:
    
    logger = logging.getLogger("pypo archive")
            
    if options.move:
        try: a.move(options)
        except Exception, e:
            print e
        sys.exit()  
        

            

    sys.exit()
