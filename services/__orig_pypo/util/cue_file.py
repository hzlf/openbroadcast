#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>

import sys
import shutil
import random
import string
import time
from datetime import timedelta
import os
import logging

from mutagen.mp3 import MP3

SAFE_MODE = False


class CueFile:

    def __init__(self, type):
        logger = logging.getLogger("cue_file")
        logger.debug("init")
        self.type = type
        
        print 'type:',
        print self.type


    def cue(self, src, dst, cue_in, cue_out):
            
        if self.type == 'cutmp3':
            return self.cue_cutmp3(src, dst, cue_in, cue_out)  
        
        if self.type == 'mp3cut':
            return self.cue_mp3cut(src, dst, cue_in, cue_out)  


    def cue_cutmp3(self, src, dst, cue_in, cue_out):
        
        print 'cue start (using cutmp3)'
        
        logger = logging.getLogger("cue_file.cue")
        logger.debug("cue file: %s %s %s %s", src, dst, cue_in, cue_out)
        
        
        print 'in:  ', str(cue_in)
        print 'out: ', str(cue_out)
        
        
        # mutagen
        audio = MP3(src)
        dur = round(audio.info.length, 3)

        logger.debug("duration by mutagen: %s", dur)
        
        cue_out = round(float(dur) - cue_out, 3) # not needed, as cutmp3 provides negative offsets
        
        str_cue_in = str(timedelta(seconds=cue_in)).replace(".", "+") # hh:mm:ss.ms, eg 00:00:20+00
        str_cue_out = str(timedelta(seconds=cue_out)).replace(".", "+") #
        
        if not '+' in str_cue_in:
            str_cue_in = str_cue_in + '+01'
            
        if not '+' in str_cue_out:
            str_cue_out = str_cue_out + '+01'
        
        
        str_cue_in = str_cue_in[3:]
        str_cue_out = str_cue_out[3:]
        
        print 'settings:  '
        print 'duration : ' + str(dur)
        print 'start:     ' + str_cue_in
        print 'end:       ' + str_cue_out
        print 
        
        """
        now a bit a hackish part, don't know how to do this better...
        need to cut the digits after the "+"
        """
        ts = str_cue_in.split("+")
        try:
            if len(ts[1]) == 6:
                ts[1] = ts[1][0:2]
                str_cue_in = "%s.%s" % (ts[0], ts[1])
            else:
                str_cue_in = "%s.%s" % (ts[0], '00')
                
        except Exception, e:
            pass
        
        ts = str_cue_out.split("+")
        try:
            if len(ts[1]) == 6:
                ts[1] = ts[1][0:2]
                str_cue_out = "%s.%s" % (ts[0], ts[1])
            else:
                str_cue_out = "%s.%s" % (ts[0], '00')
                
        except Exception, e:
            pass
        
        #sys.stderr.write(str(timedelta(seconds=cue_in)).replace(".", "+") + '\n\n')
        logger.debug("in: %s", str_cue_in)
        logger.debug("out: %s", str(str_cue_out) )
        
        command = 'cutmp3 -i %s -O %s -a %s -b %s -e' % (src, dst, str_cue_in, str_cue_out)
        print "command: %s" % command
        try:
            os.system(command)   
        except Exception, e:
            print e
        
        command = 'mp3val %s -f' % (dst)
        print "command: %s" % command
        try:
            os.system(command)   
        except Exception, e:
            print e
            
        """
        Check if dst-file exists, else just copy the src, so we loose cue, 
        but still have something to play 
        """
        if not os.path.isfile(dst):
            print 'FAILURE, DST DOES NOT EXIST'
            try:
                print
                shutil.copy2(src, dst)
            
            except Exception, e:
                print e
                print 'Ok, this went completely wrong. We do not have the file at all :('
            
        return dst



    def cue_mp3cut(self, src, dst, cue_in, cue_out):
        
        self.safe_mode = SAFE_MODE
        
        logger = logging.getLogger("cue_file.cue")
        logger.debug("cue file: %s %s %s %s", src, dst, cue_in, cue_out)
        
        # mutagen
        audio = MP3(src)
        dur = round(audio.info.length, 3)

        logger.debug("duration by mutagen: %s", dur)
        
        cue_out = round(float(dur) - cue_out, 3)
        
        str_cue_in = str(timedelta(seconds=cue_in)).replace(".", "+") # hh:mm:ss+mss, eg 00:00:20+000
        str_cue_out = str(timedelta(seconds=cue_out)).replace(".", "+") #
        
        """
        Now a bit a hackish part, don't know how to do this better...
        need to cut the digits after the "+"
        """
        ts = str_cue_in.split("+")
        try:
            if len(ts[1]) == 6:
                ts[1] = ts[1][0:3]
                str_cue_in = "%s+%s" % (ts[0], ts[1])
        except Exception, e:
            pass
        
        ts = str_cue_out.split("+")
        try:
            if len(ts[1]) == 6:
                ts[1] = ts[1][0:3]
                str_cue_out = "%s+%s" % (ts[0], ts[1])
        except Exception, e:
            pass
        
        logger.debug("in: %s", str_cue_in)
        logger.debug("out: %s", str(str_cue_out) )


        if self.safe_mode == True:

            command = 'mp3cut -o %s -t %s-%s %s' % (dst + '.tmp.mp3', str_cue_in, str_cue_out, src);
            logger.info("command: %s", command)
            print "command: %s" % command
            os.system(command + ' >/dev/null')
    
            command = 'nice -n 19 lame -b 192 %s %s' % (dst + '.tmp.mp3', dst);
            logger.info("command: %s", command)
            print "command: %s" % command
            os.system(command + ' >/dev/null')
            
        else:
            command = 'mp3cut -o %s -t %s-%s %s' % (dst, str_cue_in, str_cue_out, src);
            logger.info("command: %s", command)
            print "command: %s" % command
            os.system(command)
    
            command = 'mp3val %s -f' % (dst);
            logger.info("command: %s", command)
            print "command: %s" % command
            os.system(command)
            
            
        """
        Check if dst-file exists, else just copy the src, so we loose cue, 
        but still have something to play 
        """
        if not os.path.isfile(dst):
            print 'FAILURE, DST DOES NOT EXIST'
            try:
                print
                shutil.copy2(src, dst)
            
            except Exception, e:
                print e
                print 'Ok, this went completely wrong. We do not have the file at all :('

        return dst
