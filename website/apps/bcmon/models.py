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

def filename_by_uuid(instance, filename):
    filename, extension = os.path.splitext(filename)
    path = "media/samples/"
    
    # plain
    filename = instance.uuid + extension
    
    # splitted
    #filename = instance.uuid.replace('-', '/') + extension
    
    # timestamped
    filename = datetime.datetime.now().strftime("%Y/%m/%d/") + filename
    
    return os.path.join(path, filename)



class BaseModel(models.Model):
    
    uuid = UUIDField()
    
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    
    class Meta:
        abstract = True


class Playout(BaseModel):

    title = models.CharField(max_length=512, null=False, blank=True)
    channel = models.ForeignKey('Channel', null=True, blank=True, on_delete=models.SET_NULL)
    
    meta_name = models.CharField(max_length=512, null=False, blank=True)
    meta_artist = models.CharField(max_length=512, null=False, blank=True)
    
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Ready')),
        (3, _('Error')),
    )
    
    status = models.PositiveIntegerField(default=0, choices=STATUS_CHOICES)
    
    score = models.PositiveIntegerField(default=0)
    
    #sample = models.FileField(upload_to="media/samples/", null=True, blank=True)
    sample = models.FileField(upload_to=filename_by_uuid, null=True, blank=True)
    
    analyzer_data = JSONField(blank=True, null=True)
    enmfp = JSONField(blank=True, null=True)
    echoprint_data = JSONField(blank=True, null=True)
    echoprintfp = JSONField(blank=True, null=True)
    
    # meta
    class Meta:
        app_label = 'bcmon'
        verbose_name = _('Playout')
        verbose_name_plural = _('Playouts')
        ordering = ('-created', )

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('bcmon-playout-detail', [self.pk])
    
    def extract_meta(self):
        title_format = self.channel.title_format
        title_format = r"%s" % title_format

        try:
            pattern = re.compile(title_format, re.UNICODE)
            s = self.title
            m = pattern.search(s)
            self.meta_name = m.group('track').strip()
            self.meta_artist = m.group('artist').strip()
            
            
        except Exception, e:
            print e
            pass
    
    def analyze(self):
        
        from lib.analyzer.base import Analyze
        
        a = Analyze()
        
        code, version, enmfp = a.enmfp_from_path(self.sample.path)
        res = a.get_by_enmfp(code, version)
        
        self.enmfp = enmfp
        
        return res
    
    def echoprint(self):
        
        from lib.analyzer.echoprint import Echoprint
        e = Echoprint()
        code, version, duration, echoprint = e.echoprint_from_path(self.sample.path)
        res = e.get_by_echoprintfp(code, version)
        
        self.echoprintfp = echoprint
        return res
    
    def save(self, *args, **kwargs):
        
        if not self.id:
            self.time_start = datetime.datetime.today()
            

        # set time_end for previous entry


        self.extract_meta()
        super(Playout, self).save(*args, **kwargs)
   
   
def playout_post_save(sender, **kwargs):
    
    obj = kwargs['instance']
    
    
    try:
        lps = Playout.objects.filter(channel=obj.channel, time_end=None, status=1).order_by('-created')[1:]
        for lp in lps:
            if lp != obj:
                print lp
                lp.time_end = obj.time_start
                lp.save()
    except Exception, e:
        print e
        pass
    
    
    if (obj.sample and obj.status == '2') or (obj.sample and obj.status == 2):
        
        print 'ready for fingerprinting...'
        
        try:
            obj.analyzer_data = obj.analyze()
            obj.status = 1
            obj.save()
            
        except Exception, e:
            print e
            pass
        
        try:
            res = obj.echoprint()
            
            obj.echoprint_data = {'track_id': res['track_id'], 'score': res['score']}
            
            obj.save()
            
        except Exception, e:
            print e
            pass

    
    
 
post_save.connect(playout_post_save, sender=Playout)    


class Channel(BaseModel):

    name = models.CharField(max_length=256, null=True, blank=True)
    slug = AutoSlugField(populate_from='name')
    
    
    
    stream_url = models.CharField(max_length=256, null=True, blank=True)
    title_format = models.CharField(max_length=256, null=True, blank=True, help_text='Regex to match title against. eg "(?P<artist>[\w\s\d +"*ç%&/(),.-;:_]+?)-(?P<track>[\w\s\d +"*ç%&/(),.-;:_]+?)$" to recognize formats like "The Prodigy  (feat. Whomever) - Remix 3000" - (incl. unicode)')
    
    exclude_list = models.TextField(blank=True, null=True, help_text=_('Comma separated, keywords that should completely be ignored.'))
    title_only_list = models.TextField(blank=True, null=True, help_text=_('Comma separated, only track titles but don\' analyze.'))
    
    enable_monitoring = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'bcmon'
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')
        ordering = ('name', )

    def __unicode__(self):
        return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('bcbon-channel-detail', [self.pk])
    
    
    
class ChannelPlugin(CMSPlugin):    
    channel = models.ForeignKey(Channel, related_name='plugins')
    def __unicode__(self):
        return "%s" % self.channel.name
