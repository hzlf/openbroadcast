import os
import datetime

from django.db import models

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

    title = models.CharField(max_length=256, null=False, blank=True)
    channel = models.ForeignKey('Channel', null=True, blank=True, on_delete=models.SET_NULL)
    
    STATUS_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Ready')),
        (3, _('Error')),
    )
    
    status = models.PositiveIntegerField(default=0, choices=STATUS_CHOICES)
    
    #sample = models.FileField(upload_to="media/samples/", null=True, blank=True)
    sample = models.FileField(upload_to=filename_by_uuid, null=True, blank=True)
    
    analyzer_data = JSONField(blank=True, null=True)
    
    # meta
    class Meta:
        app_label = 'bcmon'
        verbose_name = _('Playout')
        verbose_name_plural = _('Playouts')
        ordering = ('title', )

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('bcmon-playout-detail', [self.pk])
    
    
    def analyze(self):
        
        from lib.analyzer.base import Analyze
        
        a = Analyze()
        
        code, version = a.enmfp_from_path(self.sample.path)
        res = a.get_by_enmfp(code, version)
        
        return res
    
    def save(self, *args, **kwargs):

        if self.sample and self.status == 2:
            
            try:
                self.analyzer_data = self.analyze()
                self.status = 1
                
            except Exception, e:
                print e
                pass

        super(Playout, self).save(*args, **kwargs)


class Channel(BaseModel):

    name = models.CharField(max_length=256, null=False, blank=True)
    slug = AutoSlugField(populate_from='name')
    
    stream_url = models.CharField(max_length=256, null=False, blank=True)
    title_format = models.CharField(max_length=256, null=False, blank=True)
    
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
