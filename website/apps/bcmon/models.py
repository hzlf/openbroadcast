import os
import datetime

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

    title = models.CharField(max_length=256, null=False, blank=True)
    channel = models.ForeignKey('Channel', null=True, blank=True, on_delete=models.SET_NULL)
    
    time_start = models.DateTimeField(null=True, blank=True)
    time_end = models.DateTimeField(null=True, blank=True)
    
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
        ordering = ('-created', )

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
        
        if not self.id:
            self.time_start = datetime.datetime.today()
            

        # set time_end for previous entry
        try:
            lp = Playout.objects.filter(channel=self.channel, time_end=None).order_by('-created')[0]
            lp.time_end = self.time_start
            lp.save()
                
        except Exception, e:
            print e
            pass

        super(Playout, self).save(*args, **kwargs)
   
   
def playout_post_save(sender, **kwargs):
    
    obj = kwargs['instance']
    
    
    
    if obj.sample and obj.status == '2':
        
        print 'ready for fingerprinting...'
        
        try:
            obj.analyzer_data = obj.analyze()
            obj.status = 1
            obj.save()
            
        except Exception, e:
            print e
            pass

    
    
 
post_save.connect(playout_post_save, sender=Playout)    


class Channel(BaseModel):

    name = models.CharField(max_length=256, null=True, blank=True)
    slug = AutoSlugField(populate_from='name')
    
    
    
    stream_url = models.CharField(max_length=256, null=True, blank=True)
    title_format = models.CharField(max_length=256, null=True, blank=True)
    
    exclude_list = models.TextField(blank=True, null=True)
    
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
