#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>

"""
Python part of radio playout (pypo)

The main functionas are "fetch" (./pypo_cli.py -f) and "push" (./pypo_cli.py -p)

Also check out the php counterpart that handles the api requests:
https://lab.digris.ch/svn/elgg/trunk/unstable/mod/medialibrary/application/controllers/api/pypo.php

Attention & ToDos
- liquidsoap does not like mono files! So we have to make sure that only files with 
  2 channels are fed to LS
  (solved: current = audio_to_stereo(current) - maybe not with ultimate performance)


made for python version 2.5!!
should work with 2.6 as well with a bit of adaption. for 
sure the json parsing has to be changed
(2.6 has an parser, pypo brigs it's own -> util/json.py)
"""

# python defaults (debian default)
import time
import os
import traceback
from optparse import *
import sys
from datetime import datetime
import time
import datetime
import logging
import logging.config
import shutil
import urllib
import urllib2
import pickle
import telnetlib
import random
import string
import operator

# additional modules (should be checked)
from configobj import ConfigObj

# custom imports
from util import *
from obp import *



PYPO_VERSION = '0.1'
OBP_MIN_VERSION = 2010080401 # required obp version


#set up command-line options
parser = OptionParser()

# help screeen / info
usage = "%prog [options]" + " - python playout system"
parser = OptionParser(usage=usage)

#options
parser.add_option("-f", "--fetch-scheduler", help="Fetch from scheduler - scheduler (loop, interval in config file)", default=False, action="store_true", dest="fetch_scheduler")
parser.add_option("-p", "--push-scheduler", help="Push scheduler to Liquidsoap (loop, interval in config file)", default=False, action="store_true", dest="push_scheduler")

parser.add_option("-F", "--fetch-daypart", help="Fetch from daypart - scheduler (loop, interval in config file)", default=False, action="store_true", dest="fetch_daypart")
parser.add_option("-P", "--push-daypart", help="Push daypart to Liquidsoap (loop, interval in config file)", default=False, action="store_true", dest="push_daypart")

parser.add_option("-b", "--cleanup", help="Faeili Butzae aka cleanup", default=False, action="store_true", dest="cleanup")
parser.add_option("-j", "--jingles", help="Get new jungles from obp, comma separated list if jingle-id's as argument", metavar="LIST")
parser.add_option("-t", "--test", help="Check the cached schedule and exit", default=False, action="store_true", dest="test")


parser.add_option("-c", "--config", help="Use custom config file location. (instead of config.cfg)", default='config.cfg', dest="config_file", metavar="CONFIG_FILE")

# parse options
(options, args) = parser.parse_args()



# configure logging
logging.config.fileConfig("logging.cfg")



# loading config file
try:
    config = ConfigObj(options.config_file)
    CACHE_DIR = config['cache_dir']
    FILE_DIR = config['file_dir']
    TMP_DIR = config['tmp_dir']
    BASE_URL = config['base_url']
    OBP_API_BASE = BASE_URL + 'mod/medialibrary/'
    EXPORT_URL = OBP_API_BASE + config['export_path']
    
    OBP_STATUS_URL = OBP_API_BASE + 'status/version/json'
    OBP_API_KEY = config['obp_api_key']
    
    POLL_INTERVAL = float(config['poll_interval'])
    PUSH_INTERVAL = float(config['push_interval'])
    LS_HOST = config['ls_host']
    LS_PORT = config['ls_port']
    PREPARE_AHEAD = config['prepare_ahead']
    CACHE_FOR = config['cache_for']
    CUE_STYLE = config['cue_style']
    
except Exception, e:
    print 
    print 'ERROR PARSINF CONFIG FILE!'
    print 'error: ', e
    print 'EXITING NOW'
    print 
    
    sys.exit()
    
#TIME = time.localtime(time.time())
TIME = (2010, 6, 26, 15, 33, 23, 2, 322, 0)
    
    
    
    

class Global:
    def __init__(self):
        #print '#   global initialisation'
        print
        
    def selfcheck(self):
        
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

            
        """
        Uncomment the following lines to let pypo check if
        liquidsoap is running. (checks for a telnet server)
        """
#        while self.status.check_ls(LS_HOST, LS_PORT) == 0:
#            print 'Unable to connect to liquidsoap. Is it up and running?'
#            time.sleep(2)
            
        
  
"""

"""
class Playout:
    def __init__(self):
        
        self.file_dir = FILE_DIR 
        self.tmp_dir = TMP_DIR 
        self.export_url = EXPORT_URL
        
        self.api_auth = urllib.urlencode({'api_key': OBP_API_KEY})
        self.api_client = ApiClient(OBP_API_BASE, self.api_auth)
        self.cue_file = CueFile('mp3cut')
        
        # set initial state
        self.range_updated = False
        

        
    """
    Fetching part of pypo
    - Reads the scheduled entries of a given range (actual time +/- "prepare_ahead" / "cache_for")
    - Saves a serialized file of the schedule
    - playlists are prepared. (brought to ls format) and, if not mounted via nsf, files are copied
      to the cache dir (Folder-structure: cache/YYYY-MM-DD-hh-mm-ss)
    - runs the cleanup routine, to get rid of unused cashed files
    """  
    def fetch(self, export_source):
        """
        wrapper script for fetching whole shedule (in json)
        """
        logger = logging.getLogger("fetch")
        
        
        self.export_source = export_source
        self.cache_dir = CACHE_DIR + self.export_source + '/'
        self.schedule_file = self.cache_dir + 'schedule'
        
        try: os.mkdir(self.cache_dir)
        except Exception, e: pass
        
        
        """
        Trigger daypart range-generation. (Only if daypart-instance)
        """
        if self.export_source == 'daypart':
            try: 
                self.generate_range_dp()
            except Exception, e: 
                logger.error("%s", e)
                sys.exit()
        
        
        # get shedule
        try:
            while self.get_schedule(self.export_source) != 1:
                logger.warning("failed to read from export url")
                time.sleep(1)
                
        except Exception, e: logger.error("%s", e)

        # prepare the playlists
        if CUE_STYLE == 'pre':
            try: self.prepare_playlists_cue(self.export_source)
            except Exception, e: logger.error("%s", e)
        elif CUE_STYLE == 'otf':
            try: self.prepare_playlists(self.export_source)
            except Exception, e: logger.error("%s", e)

        # cleanup
        try: self.cleanup(self.export_source)
        except Exception, e: logger.error("%s", e)
            
        logger.info("fetch loop completed")

            
            
        
        
    """
    This is actually a bit ugly (again feel free to improve!!)
    The generate_range_dp function should be called once a day, 
    we do this at 18h. The hour before the state is set back to 'False'
    """
    def generate_range_dp(self):
        
        logger = logging.getLogger("generate_range_dp")
        logger.debug("trying to trigger daypart update")
        tnow = time.localtime(time.time())
        
        try:
            print self.last_update
            
        except Exception, e:
            self.last_update = time.time() - (60 * 60 * 24)
            
        if self.last_update <= (time.time() - (60 * 60 * 24)):
            
            self.last_update = time.time()
        
            print '******************************'
            print '*** TRIGGER DAYPART UPDATE ***'
            print '******************************'    
            
            time.sleep(2)
            
            try: 
                print self.api_client.generate_range_dp()
                logger.info("daypart updated")
                print "daypart updated"
                self.range_updated = True
                
            except Exception, e:
                print e

        
        
    def get_schedule(self, export_source):
        
        logger = logging.getLogger("fetch.get_schedule")

        """
        calculate start/end time range (format: YYYY-DD-MM-hh-mm-ss,YYYY-DD-MM-hh-mm-ss)
        (seconds are ignored, just here for consistency)
        """
        
        self.export_source = export_source
        
        tnow = time.localtime(time.time())
        tstart = time.localtime(time.time() - 3600 * int(CACHE_FOR))
        tend = time.localtime(time.time() + 3600 * int(PREPARE_AHEAD))

        range = {}
        range['start'] = "%04d-%02d-%02d-%02d-%02d" % (tstart[0], tstart[1], tstart[2], tstart[3], tstart[4])
        range['end'] = "%04d-%02d-%02d-%02d-%02d" % (tend[0], tend[1], tend[2], tend[3], tend[4])

        
        export_url = self.export_url + range['start'] + ',' + range['end'] + '/' + self.export_source
        
        #print export_url
        
        logger.info("export from %s", export_url)

        try:
            response_json = urllib.urlopen(export_url, self.api_auth).read()
            response = json.read(response_json)
            logger.info("export status %s", response['check'])
            status = response['check']
            schedule = response['playlists']
            
        except Exception, e:
            print e
            status = 0
            
        if status == 1:
            
            logger.info("dump serialized shedule to %s", self.schedule_file)
            
            try:
                schedule_file = open(self.schedule_file, "w")
                pickle.dump(schedule, schedule_file)
                schedule_file.close()
                    
            except Exception, e:
                print e
                status = 0
                
        return status
            
            

    
    """
    Alternative version of playout preparation. Every playlist entry is
    pre-cued if neccessary (cue_in/cue_out != 0) and stored in the 
    playlist folder.
    file is eg 2010-06-23-15-00-00/17_cue_10.132-123.321.mp3
    """
    def prepare_playlists_cue(self, export_source):
        logger = logging.getLogger("fetch.prepare_playlists")
        
        self.export_source =  export_source

        try:
            schedule_file = open(self.schedule_file, "r")
            schedule = pickle.load(schedule_file)
            schedule_file.close()
            
        except Exception, e:
            logger.error("%s", e)
            schedule = None
 
        #for pkey in schedule:
        try:
            for pkey in sorted(schedule.iterkeys()):
                logger.info("found playlist at %s", pkey)
                #print pkey
                playlist = schedule[pkey]
                
                # create playlist directory
                try: os.mkdir(self.cache_dir + str(pkey))
                except Exception, e: pass
                
                ls_playlist = '';
                
                print '*****************************************'
                #print 'pkey:        ' + str(pkey)
                print 'cached at :  ' + self.cache_dir + str(pkey)
                print 'subtype:     ' + str(playlist['subtype'])
                print 'played:      ' + str(playlist['played'])
                #print 'schedule id: ' + str(playlist['schedule_id'])
                #print 'duration:    ' + str(playlist['duration'])
                #print 'source id:   ' + str(playlist['x_ident'])
                print '*****************************************'
                
                # TODO: maybe a bit more modular.. 
                silence_file = self.file_dir + 'basic/silence.mp3'
                
                
                if int(playlist['played']) == 1:
                    logger.info("playlist %s already played / sent to liquidsoap, so will ignore it", pkey)
                
                elif int(playlist['subtype']) == 5:
                    """
                    This is a live session, so silence is scheduled
                    Maybe not the most elegant solution :)
                    It adds 20 time 30min silence to the playlist
                    Silence file has to be in <file_dir>/basic/silence.mp3 
                    """
                    logger.debug("found %s seconds of live/studio session at %s", pkey, playlist['duration'])
                    
                    if os.path.isfile(silence_file):
                        logger.debug('file stored at: %s' + silence_file)
                        
                        for i in range (0, 19):
                            ls_playlist += silence_file + "\n"
        
                    else:
                        print 'Could not find silence file!'
                        print 'file is excpected to be at: ' + silence_file
                        logger.critical('file is excpected to be at: %s', silence_file)
                        sys.exit()
                
                elif int(playlist['subtype']) == 6:
                    """
                    This is a live-cast session
                    create a silence list. (could eg also be a falback list..)
                    """
                    logger.debug("found %s seconds of live-cast session at %s", pkey, playlist['duration'])
                    
                    if os.path.isfile(silence_file):
                        logger.debug('file stored at: %s' + silence_file)
                        
                        for i in range (0, 19):
                            ls_playlist += silence_file + "\n"
    
                    else:
                        print 'Could not find silence file!'
                        print 'file is excpected to be at: ' + silence_file
                        logger.critical('file is excpected to be at: %s', silence_file)
                        sys.exit()
                
                elif int(playlist['subtype']) == 7:
                    """
                    This is a re-broadcast session
                    create a silence list. (could eg also be a falback list..)
                    """
                    logger.debug("found %s seconds of re-broadcast session at %s", pkey, playlist['duration'])
                    
                    if os.path.isfile(silence_file):
                        logger.debug('file stored at: %s' + silence_file)
                        
                        for i in range (0, 19):
                            ls_playlist += silence_file + "\n"
    
                    else:
                        print 'Could not find silence file!'
                        print 'file is excpected to be at: ' + silence_file
                        logger.critical('file is excpected to be at: %s', silence_file)
                        sys.exit()
                    
                
                elif int(playlist['subtype']) > 0 and int(playlist['subtype']) < 5:
                
                    for media in playlist['medias']:
                        logger.debug("found track at %s", media['uri'])
                        
                        try:
                            src = media['uri']
                            
                            if str(media['cue_in']) == '0' and str(media['cue_out']) == '0':
                                dst = "%s%s/%s.mp3" % (self.cache_dir, str(pkey), str(media['id']))
                                do_cue = False
                            else:
                                dst = "%s%s/%s_cue_%s-%s.mp3" % \
                                (self.cache_dir, str(pkey), str(media['id']), str(float(media['cue_in']) / 1000), str(float(media['cue_out']) / 1000))
                                do_cue = True
                                
                            #print "dst_cue: " + dst
                            
                            # check if it is a remote file, if yes download
                            if src[0:4] == 'http' and do_cue == False:
                                
                                if os.path.isfile(dst):
                                    logger.debug("file already in cache: %s", dst)
                                    
                                else:
                                    logger.debug("try to download %s", src)
                                    try:
                                        print '** urllib auth with: ',
                                        print self.api_auth
                                        urllib.urlretrieve (src, dst, False, self.api_auth)
                                        logger.info("downloaded %s to %s", src, dst)
                                    except Exception, e:
                                        logger.error("%s", e)
                                        
                            elif src[0:4] == 'http' and do_cue == True:
                                

                                
                                if os.path.isfile(dst):
                                    logger.debug("file already in cache: %s", dst)
                                    #print 'cached'
                                    
                                else:
                                    logger.debug("try to download and cue %s", src)
                                    
                                    #print '***'
                                    dst_tmp = self.tmp_dir + "".join([random.choice(string.letters) for i in xrange(10)]) + '.mp3'
                                    print dst_tmp
                                    #print '***'
                                    
                                    try:

                                        self.api_client.get_media(src, dst_tmp)
                                        
                                        
                                    except Exception, e:
                                        logger.error("%s", e)
                                        
                                        
                                    # cue
                                    print "STARTIONG CUE"
                                    print self.cue_file.cue(dst_tmp, dst, float(media['cue_in']) / 1000, float(media['cue_out']) / 1000)
                                    print "END CUE"
                                        
                                    if True == os.access(dst, os.R_OK):
                                        
                                        try: fsize = os.path.getsize(dst)
                                        except Exception, e:
                                            logger.error("%s", e)
                                            fsize = 0  
                                            
                                    if fsize > 0:
                                        logger.debug('try to remove temporary file: %s' + dst_tmp)
                                        try: os.remove(dst_tmp)
                                        except Exception, e:
                                            logger.error("%s", e)
                                            
                                    else:
                                        logger.warning('something went wrong cueing: %s - using uncued file' + dst)
                                        try: os.rename(dst_tmp, dst)
                                        except Exception, e:
                                            logger.error("%s", e) 
                                        
                                        
                            else:
                                """
                                Handle files on nas. Pre-cueing not implemented at the moment.
                                (not needed by openbroadcast, feel free to add this)
                                """
     
                                
                            if True == os.access(dst, os.R_OK):
                                # check filesize (avoid zero-byte files)
                                #print 'waiting: ' + dst
                                
                                try: fsize = os.path.getsize(dst)
                                except Exception, e:
                                    logger.error("%s", e)
                                    fsize = 0
                                    
                                if fsize > 0:
                                    
                                    start_next = 0.05
    
                                    pl_entry = 'annotate:export_source="%s",media_id="%s",playlist_id="%s",liq_start_next="%s",liq_fade_in="%s",liq_fade_out="%s":%s' % \
                                    (str(media['export_source']), media['id'], media['playlist_id'], start_next, str(float(media['fade_in']) / 1000), str(float(media['fade_out']) / 1000), dst)
    
                                    #print pl_entry
    
    
                                    """
                                    Tracks are only added to the playlist if they are accessible
                                    on the file system and larger than 0 bytes.
                                    So this can lead to playlists shorter than expectet.
                                    (there is a hardware silence detector for this cases...) 
                                    """
                                    ls_playlist += pl_entry + "\n"
                                    
                                    logger.debug("everything ok, adding %s to playlist", pl_entry)
                                
                                else:
                                    print 'zero-file: ' + dst + ' from ' + src 
                                    logger.warning("zero-size file - skiping %s. will not add it to playlist", dst)
                                
                            else:
                                logger.warning("something went wrong. file %s not available. will not add it to playlist", dst)
                                
    
        
                        except Exception, e: logger.info("%s", e)
                    
                    
                """
                This is kind of hackish. We add a bunch of "silence" tracks to the end of each playlist.
                So we can make sure the list does not get repeated just before a new one is called. 
                (or in case nothing is in the scheduler afterwards)
                20 x silence = 10 hours
                """
                for i in range (0, 1):
                    ls_playlist += silence_file + "\n"
                    print '',
                            
                # write playlist file
                plfile = open(self.cache_dir + str(pkey) + '/list.lsp', "w")
                plfile.write(ls_playlist)
                plfile.close()
                
                # write a file with playlist information
                
                #print playlist
                
                try:
                    plfile = open(self.cache_dir + str(pkey) + '/' + playlist['x_ident'] + '.id', "w")
                    plfile.write('x')
                    plfile.close()
                except Exception, e:
                    print e
                    
                
                
                logger.info('ls playlist file written to %s', self.cache_dir + str(pkey) + '/list.lsp')
            
        except Exception, e: 
            logger.info("%s", e)
                

    def cleanup(self, export_source):
        logger = logging.getLogger("cleanup")
        
        self.export_source = export_source
        self.cache_dir = CACHE_DIR + self.export_source + '/'
        self.schedule_file = self.cache_dir + 'schedule'

        """
        Cleans up folders in cache_dir. Look for modification date older than "now - CACHE_FOR"
        and deletes them. 
        """

        offset = 3600 * int(CACHE_FOR)
        now = time.time()

        for r, d, f in os.walk(self.cache_dir):
            
            for dir in d:
                
                try:
    
                    
                    timestamp = time.mktime(time.strptime(dir, "%Y-%m-%d-%H-%M-%S"))
                    
                    print
                    print 'dir          : %s' % (dir)
                    print 'age          : %s' % (round((now - timestamp),1))
                    print 'delete in    : %ss' % (round((offset - (now - timestamp)),1))
                    print '-'
                    
                    logger.debug('Folder "Age": %s - %s', round((((now - offset) - timestamp) / 60), 2), os.path.join(r, dir))
                
                    if (now - timestamp) > offset:
                        try:
                            logger.debug('trying to remove  %s - timestamp: %s', os.path.join(r, dir), timestamp)
                            shutil.rmtree(os.path.join(r, dir))
                        except Exception, e:
                            logger.error("%s", e)
                            pass
                        else: 
                            logger.info('sucessfully removed %s', os.path.join(r, dir))
                            
                            
                            
                except Exception, e:
                    print e
                    logger.error("%s", e)
                        
                        
                        
    
            
            
    """
    The counterpart - the push loop periodically (minimal 1/2 of the playlist-grid) 
    checks if there is a playlist that should be sheduled at the current time.
    If yes, the temporary liquidsoap playlist gets replaced with the corresponding one,
    then liquid is asked (via telnet) to reload and immediately play it
    """
    def push(self, export_source):
        logger = logging.getLogger("push")

        
        self.export_source = export_source
        self.cache_dir = CACHE_DIR + self.export_source + '/'
        self.schedule_file = self.cache_dir + 'schedule'
        
        self.push_ahead = 15
        
        try:
            dummy = self.schedule
            logger.debug('schedule already loaded')
        except Exception, e:
            self.schedule = self.push_init(self.export_source)
            
        self.schedule = self.push_init(self.export_source)
            

        """
        I'm quite sure that this could be achieved in a much more elegant way in python...
        """

        tcomming = time.localtime(time.time() + self.push_ahead)
        tnow = time.localtime(time.time())
        
        str_tnow = "%04d-%02d-%02d-%02d-%02d" % (tnow[0], tnow[1], tnow[2], tnow[3], tnow[4])
        str_tnow_s = "%04d-%02d-%02d-%02d-%02d-%02d" % (tnow[0], tnow[1], tnow[2], tnow[3], tnow[4], tnow[5])
        
        str_tcomming = "%04d-%02d-%02d-%02d-%02d" % (tcomming[0], tcomming[1], tcomming[2], tcomming[3], tcomming[4])
        str_tcomming_s = "%04d-%02d-%02d-%02d-%02d-%02d" % (tcomming[0], tcomming[1], tcomming[2], tcomming[3], tcomming[4], tcomming[5])


        print '--'
        print str_tnow_s + ' now'
        print str_tcomming_s + ' comming'


        playnow = None
        
        if self.schedule == None:
            print 'unable to loop schedule - maybe write in progress'
            print 'will try in next loop'
        
        else:    
            for pkey in self.schedule:
                logger.debug('found playlist schedulet at: %s', pkey)
                
                #if pkey[0:16] == str_tnow:
                if pkey[0:16] == str_tcomming:
                    playlist = self.schedule[pkey]
                    
                    if int(playlist['played']) != 1:
                        
                        print '!!!!!!!!!!!!!!!!!!!'
                        print 'MATCH'

    
                        """
                        ok we have a match, replace the current playlist and
                        force liquidsoap to refresh
                        Add a 'played' state to the list in schedule, so it is not called again 
                        in the next push loop
                        """
         
                        ptype = playlist['subtype']
                        
                        
                        print playlist
                        
                        try:
                            user_id = playlist['user_id']
                            playlist_id = playlist['id']
                            transmission_id = playlist['schedule_id']
                            duration = playlist['duration']
                        
                        except Exception, e:
                            playlist_id = 0
                            user_id = 0
                            transmission_id = 0
                            duration = False
                            print e
                        
                        
                        print 'Playlist id:',
                        
                        
                        if(self.push_liquidsoap(pkey, ptype, user_id, playlist_id, transmission_id, self.push_ahead, duration) == 1):
                            self.schedule[pkey]['played'] = 1
                            """
                            Call api to update schedule states and
                            write changes back to cache file
                            """
                            self.api_client.update_shedueled_item(int(playlist['schedule_id']), 1)
                            schedule_file = open(self.schedule_file, "w")
                            pickle.dump(self.schedule, schedule_file)
                            schedule_file.close() 

        
    def push_init(self, export_source):
        
        logger = logging.getLogger("push_init")
        
        self.export_source = export_source
        self.cache_dir = CACHE_DIR + self.export_source + '/'
        self.schedule_file = self.cache_dir + 'schedule'
        
        # load the shedule from cache
        logger.debug('load shedule from cache')
        try:
            schedule_file = open(self.schedule_file, "r")
            schedule = pickle.load(schedule_file)
            schedule_file.close()
            
        except Exception, e:
            logger.error('%s', e)
            schedule = None

        return schedule
    
    
    
    def push_liquidsoap(self, pkey, ptype, user_id, playlist_id, transmission_id, push_ahead, duration):
        logger = logging.getLogger("push_liquidsoap")
        
        #self.export_source = export_source
        
        self.push_ahead = push_ahead
        
        self.cache_dir = CACHE_DIR + self.export_source + '/'
        self.schedule_file = self.cache_dir + 'schedule'
        
        src = self.cache_dir + str(pkey) + '/list.lsp'
        
        print src
        
        try:
            if True == os.access(src, os.R_OK):
                print 'OK - Can read'
                
            pl_file = open(src, "r")
    
            """
            i know this could be wrapped, maybe later..
            """
            tn = telnetlib.Telnet(LS_HOST, 1234)
            
            
            if(int(ptype) == 6):
                tn.write("live_in.start")
                tn.write("\n")
            
            
            if(int(ptype) == 7):
                tn.write("live_in.start")
                tn.write("\n")
                
            
            if(int(ptype) < 5):
                for line in pl_file.readlines():
                    print line.strip() 
                    tn.write(self.export_source + '.push %s' % (line.strip()))
                    tn.write("\n")

                
            tn.write("exit\n")
            print tn.read_all()
            
            
            print 'sleeping for %s s' % (self.push_ahead)
            time.sleep(self.push_ahead)
            

            print 'sending "flip"'
            tn = telnetlib.Telnet(LS_HOST, 1234)
            
            """
            Pass some extra information to liquidsoap
            """
            print 'user_id: %s' % user_id
            print 'playlist_id: %s' % playlist_id
            print 'transmission_id: %s' % transmission_id
            print 'ptype: %s' % ptype
            
            tn.write("vars_%s.playlist_type %s\n" % (self.export_source, ptype))
            tn.write("vars_%s.user_id %s\n" % (self.export_source, user_id))
            tn.write("vars_%s.playlist_id %s\n" % (self.export_source, playlist_id))
            tn.write("vars_%s.transmission_id %s\n" % (self.export_source, transmission_id))
            
            
            """
            Only use live-switches for scheduler lists
            """
            if self.export_source == 'scheduler':
                if(int(ptype) == 6):
                    
                    tn.write("vars_cc.user_id %s\n" % user_id)
                    tn.write("vars_cc.playlist_id %s\n" % playlist_id)
                    tn.write("vars_cc.transmission_id %s\n" % transmission_id)
                    tn.write("live.active 1")
                    tn.write("\n")
                    
                    """
                    Trigger the live-stop script (will sleep for the duration of the 
                    transmission, then fires a stop signal to ls)
                    """
                    command = 'python pypo_live_stop.py --time=%s &' % (duration);
                    logger.info("command: %s", command)
                    print "command: %s" % command
                    os.system(command)
                    
                elif(int(ptype) == 7):
                    
                    tn.write("vars_rc.user_id %s\n" % user_id)
                    tn.write("vars_rc.playlist_id %s\n" % playlist_id)
                    tn.write("vars_rc.transmission_id %s\n" % transmission_id)
                    tn.write("live.active 1")
                    tn.write("\n")
                    
                    """
                    Trigger the live-stop script (will sleep for the duration of the 
                    transmission, then fires a stop signal to ls)
                    """
                    command = 'python pypo_live_stop.py --time=%s &' % (duration);
                    logger.info("command: %s", command)
                    print "command: %s" % command
                    os.system(command)
                    
                    
                else:
                    
                    
                    """
                    Kill running 'killer' (if any)
                    """
                    command = "kill $(ps aux | grep '[p]ython pypo_live_stop.py' | awk '{print $2}')"
                    logger.info("command: %s", command)
                    print "command: %s" % command
                    os.system(command)
                    
                    tn.write("live.active 0")
                    tn.write("\n") 
                #tn.write("live_in.stop")
                #tn.write("\n") 
                
            time.sleep(1)
                

            tn.write(self.export_source + '.flip')
            tn.write("\n")
            
            
            """
            Only use live-switches for scheduler lists
            """
            if self.export_source == 'scheduler':
                if int(ptype) != 6 and int(ptype) != 7:
                    print 'sleeping for %s s' % (self.push_ahead)
                    time.sleep(self.push_ahead)
                    tn.write("live_in.stop")
                    tn.write("\n") 
                
            
            
            tn.write("exit\n")
            
            print tn.read_all()
            status = 1
        except Exception, e:
            logger.error('%s', e)
            status = 0
            
        return status
    

    """
    Updates the jinles. Give comma separated list of jingle tracks
    """
    def update_jingles(self, options):
        print 'jingles'
        
        jingle_list = string.split(options, ',')
        print jingle_list
        for media_id in jingle_list:
            # api path maybe should not be hard-coded
            src = OBP_API_BASE + 'api/pypo/get_media/' + str(media_id)
            print src
            # include the hourly jungles for the moment
            dst = "%s%s/%s.mp3" % (self.file_dir, 'jingles/hourly', str(media_id))
            print dst
            
            try:
                print '** urllib auth with: ',
                print self.api_auth
                opener = urllib.URLopener()
                opener.retrieve (src, dst, False, self.api_auth)
                logger.info("downloaded %s to %s", src, dst)
            except Exception, e:
                print e
                logger.error("%s", e)


    
    def check_schedule(self, export_source):
        logger = logging.getLogger("check_schedule")

        self.export_source = export_source
        self.cache_dir = CACHE_DIR + self.export_source + '/'
        self.schedule_file = self.cache_dir + 'schedule'

        try:
            schedule_file = open(self.schedule_file, "r")
            schedule = pickle.load(schedule_file)
            schedule_file.close()
            
        except Exception, e:
            logger.error("%s", e)
            schedule = None


        #for pkey in schedule:
        for pkey in sorted(schedule.iterkeys()):

            playlist = schedule[pkey]
            
            print '*****************************************'
            print '\033[0;32m%s %s\033[m' % ('scheduled at:', str(pkey))
            print 'cached at :   ' + self.cache_dir + str(pkey)
            print 'subtype:      ' + str(playlist['subtype'])
            print 'played:       ' + str(playlist['played'])
            print 'schedule id:  ' + str(playlist['schedule_id'])
            print 'duration:     ' + str(playlist['duration'])
            print 'source id:    ' + str(playlist['x_ident'])
            
            print '-----------------------------------------'
            
            for media in playlist['medias']:
                print media
            
            
            print 
            
            

if __name__ == '__main__':
  
    print
    print '#########################################'
    print '#           *** pypo  ***               #'
    print '#         obp python playout            #'
    print '#########################################'
    print
    
    # initialize
    g = Global()
    g.selfcheck()
    po = Playout()


run = True
while run == True:
    
    logger = logging.getLogger("pypo")
    
    loops = 0
    
    while options.fetch_scheduler:
        try: po.fetch('scheduler')
        except Exception, e:
            print e
            sys.exit()
        
        print '.... sleeping for ' + str(POLL_INTERVAL) + ' seconds'
        logger.info('fetch loop %s - .... sleeping for %s seconds', loops, POLL_INTERVAL)
        loops += 1
        time.sleep(POLL_INTERVAL)
    
    while options.fetch_daypart:
        try: po.fetch('daypart')
        except Exception, e:
            print e
            sys.exit()
        
        print '.... sleeping for ' + str(POLL_INTERVAL) + ' seconds'
        logger.info('fetch loop %s - .... sleeping for %s seconds', loops, POLL_INTERVAL)
        loops += 1
        time.sleep(POLL_INTERVAL)
        
            
    while options.push_scheduler:
        

        
        try: po.push('scheduler')
        except Exception, e:
            print 'PUSH ERROR!! WILL EXIT NOW:('
            print e
            sys.exit()
            
        logger.info('push loop %s - .... sleeping for %s seconds', loops, PUSH_INTERVAL)
        loops += 1
        time.sleep(PUSH_INTERVAL)
        
            
    while options.push_daypart:
        

        
        try: po.push('daypart')
        except Exception, e:
            print 'PUSH ERROR!! WILL EXIT NOW:('
            print e
            sys.exit()
            
        logger.info('push loop %s - .... sleeping for %s seconds', loops, PUSH_INTERVAL)
        loops += 1
        time.sleep(PUSH_INTERVAL)
        
            
    while options.jingles:
        try: po.update_jingles(options.jingles)
        except Exception, e:
            print e
        sys.exit()  
        
            
    while options.test:
        try: po.check_schedule('scheduler')
        except Exception, e:
            print e
        try: po.check_schedule('daypart')
        except Exception, e:
            print e
        sys.exit()        
            
    while options.cleanup:
        try: po.cleanup('scheduler')
        except Exception, e:
            print e
        sys.exit()
            

    sys.exit()
