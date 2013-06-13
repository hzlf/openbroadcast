#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime
import re

from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from cms.models import CMSPlugin
from django_extensions.db.fields import *
from django_extensions.db.fields.json import JSONField

from django.core.urlresolvers import reverse

# filer
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField

# 
from lib.fields import extra

class BaseModel(models.Model):
    
    uuid = UUIDField()
    
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    
    class Meta:
        abstract = True




class Station(BaseModel):

    name = models.CharField(max_length=256, null=True, blank=True)
    teaser = models.CharField(max_length=512, null=True, blank=True)
    slug = AutoSlugField(populate_from='name')
    
    TYPE_CHOICES = (
        ('stream', _('Stream')),
        ('djmon', _('DJ-Monitor')),
    )
    type = models.CharField(verbose_name=_('Type'), max_length=12, default='stream', choices=TYPE_CHOICES)
    
    main_image = FilerImageField(null=True, blank=True, related_name="station_main_image", rel='')
    description = extra.MarkdownTextField(blank=True, null=True)

    
    class Meta:
        app_label = 'abcast'
        verbose_name = _('Station')
        verbose_name_plural = _('Stations')
        ordering = ('name', )

    def __unicode__(self):
        return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('abcast-station-detail', [self.pk])
    
    
"""
A bit verbose, as already channel in bcmon - but different type of app f.t.m.
"""
class Channel(BaseModel):

    name = models.CharField(max_length=256, null=True, blank=True)
    teaser = models.CharField(max_length=512, null=True, blank=True)
    slug = AutoSlugField(populate_from='name')
    
    TYPE_CHOICES = (
        ('stream', _('Stream')),
        ('djmon', _('DJ-Monitor')),
    )
    type = models.CharField(verbose_name=_('Type'), max_length=12, default='stream', choices=TYPE_CHOICES)
    
    stream_url = models.CharField(max_length=256, null=True, blank=True)
    description = extra.MarkdownTextField(blank=True, null=True)
    
    station = models.ForeignKey('Station', null=True, blank=True, on_delete=models.SET_NULL)
    
    """
    settings for 'owned' channels
    """
    stream_server = models.ForeignKey('StreamServer', null=True, blank=True, on_delete=models.SET_NULL)
    mount = models.CharField(max_length=64, null=True, blank=True)
    
    
    class Meta:
        app_label = 'abcast'
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')
        ordering = ('name', )

    def __unicode__(self):
        return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('abcast-channel-detail', [self.pk])
    
    def get_api_url(self):
        return reverse('api_dispatch_detail', kwargs={  
            'api_name': 'v1',  
            'resource_name': 'abcast/channel',  
            'pk': self.pk  
        }) + ''


class StreamServer(BaseModel):
    
    name = models.CharField(max_length=256, null=True, blank=False)     
    host = models.URLField(max_length=256, null=True, blank=False) 
    source_pass = models.CharField(max_length=64, null=True, blank=True)
    admin_pass = models.CharField(max_length=64, null=True, blank=True)
    
    active = models.BooleanField(default=True)
    formats = models.ManyToManyField('StreamFormat', null=True, blank=True)
    
    
     
    TYPE_CHOICES = (
        ('icecast2', _('Icecast 2')),
        ('rtmp', _('RTMP / Wowza')),
    )
    type = models.CharField(verbose_name=_('Type'), max_length=12, default='icecast2', choices=TYPE_CHOICES)
    
    
    class Meta:
        app_label = 'abcast'
        verbose_name = _('Streaming server')
        verbose_name_plural = _('Streaming servers')
        ordering = ('name', )

    def __unicode__(self):
        return "%s" % self.name

class StreamFormat(BaseModel):

    TYPE_CHOICES = (
        ('mp3', _('MP3')),
        ('ogg', _('ogg/vorbis')),
        ('aac', _('AAC')),
    )
    type = models.CharField(max_length=12, default='mp3', choices=TYPE_CHOICES)
    BITRATE_CHOICES = (
        (64, _('64 kbps')),
        (96, _('96 kbps')),
        (128, _('128 kbps')),
        (160, _('160 kbps')),
        (192, _('192 kbps')),
        (256, _('256 kbps')),
        (320, _('320 kbps')),
    )
    bitrate = models.PositiveIntegerField(default=256, choices=BITRATE_CHOICES)
    
    
    class Meta:
        app_label = 'abcast'
        verbose_name = _('Streaming format')
        verbose_name_plural = _('Streaming formats')
        ordering = ('type', )

    def __unicode__(self):
        return "%s | %s" % (self.type, self.bitrate)
    
    
    

class OnAirPlugin(CMSPlugin):    
    channel = models.ForeignKey(Channel, related_name='plugins')
    show_channel_info = models.BooleanField(default=True)
    class Meta:
        app_label = 'abcast'

    def __unicode__(self):
        return "%s" % self.channel.name

