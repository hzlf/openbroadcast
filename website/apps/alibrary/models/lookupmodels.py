# python
import datetime
import uuid
import shutil
import sys

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


# logging
import logging
logger = logging.getLogger(__name__)


################
from alibrary.models import *


class APILookup(models.Model):
    
    PROVIDER_CHOICES = (
        (None, _('Not Set')),
        ('discogs', _('Discogs')),
    )
    provider = models.CharField(max_length=50, default=None, choices=PROVIDER_CHOICES)
    
    uri = models.URLField(blank=True, null=True)
    ressource_id = models.CharField(max_length=500, null=True, blank=True)
    

    PROCESSED_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    processed = models.PositiveIntegerField(max_length=2, default=0, choices=PROCESSED_CHOICES)
    
    
    content_type = models.ForeignKey(ContentType)
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
        
    def get_from_api(self):
        
        if self.provider == 'discogs':
            self.get_from_discogs()
        
        
    def get_from_discogs(self):
        
        print 'get from discogs'
        
        import discogs_client as discogs
        discogs.user_agent = 'ANORGDiscogsAPIClient/0.0.1 +http://anorg.net'
        
        
        #d_release = discogs.Release(self.ressource_id).master
        #d_master = d_release.master
        #d_releasde = d_master.key_release
        
        # get discog's key-release from ressource id
        d_release = discogs.Release(self.ressource_id).master.key_release
        
        """ release:
         |  artists
         |  credits
         |  labels
         |  master
         |  title
         |  tracklist
        """
        
        for k in d_release.data:
            print 'k: %s - v:%s' % (k, d_release.data[k])
            attribute, created = Attribute.objects.get_or_create(name=k, datatype=Attribute.TYPE_TEXT)
            setattr(self.eav, k, d_release.data[k])
            
        self.save()

        
        
        pass
    
        

 
eav.register(APILookup)
        
