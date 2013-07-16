# python
import datetime
import uuid
import shutil
import sys
import json

# django
from django.db import models
from django import forms
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.files import File as DjangoFile
from django.core.urlresolvers import reverse

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.http import HttpResponse # needed for absolute url

from settings import *

import eav
from eav.models import Attribute

from jsonfield import JSONField

from urlparse import urlparse


# logging
import logging
logger = logging.getLogger(__name__)


################
from alibrary.models import *


class APILookup(models.Model):
    
    PROVIDER_CHOICES = (
        (None, _('Not Set')),
        ('discogs', _('Discogs')),
        ('musicbrainz', _('Musicbrainz')),
    )
    provider = models.CharField(max_length=50, default=None, choices=PROVIDER_CHOICES)
    
    uri = models.URLField(blank=True, null=True)
    ressource_id = models.CharField(max_length=500, null=True, blank=True)
    
    api_data = JSONField(null=True, blank=True);
    

    PROCESSED_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    processed = models.PositiveIntegerField(max_length=2, default=0, choices=PROCESSED_CHOICES)
    
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


    # auto-update
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    
    # manager
    objects = models.Manager()

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('APILookup')
        verbose_name_plural = _('APILookups')
        ordering = ('created', )

    
    def __unicode__(self):
        return "%s - %s" % (self.provider, self.updated)


    def save(self, *args, **kwargs):

        super(APILookup, self).save(*args, **kwargs)
        
        
    """
    Generic Wrapper - distributes to corresponding method
    """
    def get_from_api(self):
        
        log = logging.getLogger('alibrary.lookupmodels.get_from_api')
        log.debug('provider: %s' % self.provider)
        
        if self.provider == 'discogs':
            return self.get_from_discogs()
        









    def get_from_discogs(self):
        
        log = logging.getLogger('alibrary.lookupmodels.get_from_discogs')
        
        log.debug('content_object: %s' % self.content_object)

        self.uri = self.content_object.relations.filter(service='discogs')[0].url
        
        log.info('uri: %s' % self.uri)
            
        try:
            ri = urlparse(self.uri).path
            ri = ri.split('/')
            ri = ri[-1:]
            ri = int(ri[0])
            
            self.ressource_id = ri
            log.info('ressource_id: %s' % self.ressource_id)
            
        except Exception, e:
            self.ressource_id = None
            log.warning('%s' % e)

        if not self.ressource_id:
            log.warning('no resource id for %s' % self.content_object)
        
        
        
        
        """
        Actual API requests
        """
        
        import discogs_client as discogs
        discogs.user_agent = 'ANORGDiscogsAPIClient/0.0.1 +http://anorg.net'
        
        
        #d_release = discogs.Release(self.ressource_id).master
        #d_master = d_release.master
        #d_releasde = d_master.key_release
        
        # get discog's key-release from ressource id
        d_release = discogs.Release(self.ressource_id)
        
        # check if there is a master release
        try:
            d_release = d_release.master.key_release
        except Exception, e:
            print e
            
        
        """ release:
         |  artists
         |  credits
         |  labels
         |  master
         |  title
         |  tracklist
        """
        
        #for k in d_release.data:
        #    print 'k: %s - v:%s' % (k, d_release.data[k])
        #    attribute, created = Attribute.objects.get_or_create(name=k, datatype=Attribute.TYPE_TEXT)
        #    setattr(self.eav, k, d_release.data[k])
            
        #self.save()

        res = {}
        d_tags = [] # needed as merged from different keys

        for k in d_release.data:
            # print 'k: %s - v:%s' % (k, d_release.data[k])
            
            # kind of ugly data mapping
            mk = k
            if k == 'title':
                mk = 'name'

            if k == 'notes':
                mk = 'description'

            if k == 'released_formatted':
                mk = 'releasedate_approx'


            # try to extract format information
            if k == 'formats':
                try:
                    d = d_release.data[k]
                    res['releasetype'] = d[0]['descriptions'][0]
                except:
                    pass


            if k == 'country':
                mk = 'release_country'
                
            if k == 'labels':
                try:
                    d = d_release.data[k][0]
                    res['label_0'] = d['name']
                    res['catalognumber'] = d['catno']
                except:
                    pass


            # tagging
            if k == 'styles':
                try:
                    d = d_release.data[k]
                    for v in d:
                        d_tags.append(v)
                except:
                    pass

            if k == 'genres':
                try:
                    d = d_release.data[k]
                    for v in d:
                        d_tags.append(v)
                except:
                    pass

            # image
            if k == 'images':
                image = None
                try:
                    d = d_release.data[k]
                    for v in d:
                        if v['type'] == 'primary':
                            image = v['resource_url']
                        print v
                except:
                    pass

                # sorry, kind of ugly...
                if not image:
                    try:
                        d = d_release.data[k]
                        for v in d:
                            if v['type'] == 'secondary':
                                image = v['resource_url']
                            print v
                    except:
                        pass

                try:
                    res['remote_image'] = res['main_image'] = image.replace('api.discogs.com', 'dgs.anorg.net') + '?cache=7'
                except:
                    res['remote_image'] = res['main_image'] = None
                #res['remote_image'] = 'http://dgs.anorg.net/image/R-5081-1147456810.jpeg'




            res[mk] = d_release.data[k]

        print 'DTAGS:'
        print d_tags

        res['d_tags'] = ', '.join(d_tags)
        self.api_data = res
        self.save()
        
        return res
    
        

 
#eav.register(APILookup)
        
