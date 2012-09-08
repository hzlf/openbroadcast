#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author Jonas Ohrstrom <jonas@digris.ch>

import sys
import time
import urllib

import logging

from util import json

import os


        
class ApiClient():

    def __init__(self, api_url, api_auth):
        self.api_url = api_url
        self.api_auth = api_auth

    def get_obp_version(self):
        logger = logging.getLogger("ApiClient.get_obp_version")
        # lookup OBP version
        
        url = self.api_url + 'api/pypo/status/json'
        
        
        logger.debug("%s", url)
        
        try:
            
            logger.debug("Trying to contact %s", url)
            
            response = urllib.urlopen(url, self.api_auth)
            response_json = json.read(response.read())
            obp_version = int(response_json['version'])
            logger.debug("OBP Version %s detected", obp_version)

    
        except Exception, e:
            try:
                if e[1] == 401:
                    print '#####################################'
                    print '# YOUR API KEY SEEMS TO BE INVALID'
                    print '# ' + self.api_auth
                    print '#####################################'
                    logger.critical("API Key invalid")
                    sys.exit()
                    
            except Exception, e:
                pass
            
            try:
                if e[1] == 404:
                    print '#####################################'
                    print '# Unable to contact the OBP-API'
                    print '# ' + url
                    print '#####################################'
                    logger.critical("Unable to connect to API at %s", url)
                    sys.exit()
                    
            except Exception, e:
                pass
            
            obp_version = 0
            logger.error("Unable to detect OBP Version - %s", e)

        
        return obp_version
    
    
    def get_media(self, src, dst):
        logger = logging.getLogger("ApiClient.get_media")
        
        try:
            urllib.urlretrieve (src, dst, False, self.api_auth)
            logger.info("downloading %s to %s", src, dst)
    
        except Exception, e:
            print e
            api_status = False
            logger.critical("Unable to download file - %s", e)
    
        if True == os.access(dst, os.R_OK):
            api_status = True
        
        return api_status


    def update_shedueled_item(self, item_id, value):
        logger = logging.getLogger("ApiClient.update_shedueled_item")
        # lookup OBP version
        
        url = self.api_url + 'api/pypo/update_shedueled_item/' + str(item_id) + '?played=' + str(value)
        
        try:
            response = urllib.urlopen(url, self.api_auth)
            response = json.read(response.read())
            logger.info("API-Status %s", response['status'])
            logger.info("API-Message %s", response['message'])
    
        except Exception, e:
            print e
            api_status = False
            logger.critical("Unable to connect to the OBP API - %s", e)
    
        
        return response


    def update_start_playing(self, playlist_type, export_source, media_id, playlist_id, transmission_id, user_id):

        logger = logging.getLogger("ApiClient.update_shedueled_item")
    
        url = self.api_url + 'api/pypo/update_start_playing/' \
        + '?playlist_type=' + str(playlist_type) \
        + '&export_source=' + str(export_source) \
        + '&user_id=' + str(user_id) \
        + '&media_id=' + str(media_id) \
        + '&playlist_id=' + str(playlist_id) \
        + '&transmission_id=' + str(transmission_id)
        
        print url
        
        try:
            response = urllib.urlopen(url, self.api_auth)
            response = json.read(response.read())
            logger.info("API-Status %s", response['status'])
            logger.info("API-Message %s", response['message'])
            logger.info("TXT %s", response['str_dls'])
    
        except Exception, e:
            print e
            api_status = False
            logger.critical("Unable to connect to the OBP API - %s", e)
    
        
        return response
    
    
    def generate_range_dp(self):
        logger = logging.getLogger("ApiClient.generate_range_dp")
    
        url = self.api_url + 'api/pypo/generate_range_dp/force/true'
        
        print '*** calling'
        print url
        print '***********'
        
        try:
            response = urllib.urlopen(url, self.api_auth)
            response = json.read(response.read())
            logger.debug("Trying to contact %s", url)
            logger.info("API-Status %s", response['status'])
            logger.info("API-Message %s", response['message'])
    
        except Exception, e:
            print e
            api_status = False
            logger.critical("Unable to handle the OBP API request - %s", e)
        
        
        return response
    
    
    
    
    