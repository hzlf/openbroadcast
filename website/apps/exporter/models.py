#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import datetime
import re

from django.db import models
from django.db.models.signals import post_save
from django.core.files import File as DjangoFile

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from django.db.models.signals import post_delete, post_save


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.core.urlresolvers import reverse

from django_extensions.db.fields.json import JSONField

from zipfile import ZipFile

from alibrary.models import Release, Media, Artist, Relation


from util.process import Process

import magic
from celery.task import task
import logging
log = logging.getLogger(__name__)

USE_CELERYD = False    
        
GENERIC_STATUS_CHOICES = (
    (0, _('Init')),
    (1, _('Done')),
    (2, _('Ready')),
    (3, _('Progress')),
    (99, _('Error')),
    (11, _('Other')),
)



# extra fields
from django_extensions.db.fields import *

from settings import PROJECT_DIR
        
        
def create_download_path(instance, filename):
    import unicodedata
    import string
    filename, extension = os.path.splitext(filename)
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')    
    folder = "export/%s/" % time.strftime("%Y%m%d%H%M%S", time.gmtime())
    return os.path.join(folder, "%s%s" % (cleaned_filename.lower(), extension.lower()))


def create_export_path():
    import unicodedata
    import string
    filename, extension = os.path.splitext(filename)
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')    
    folder = "export/%s/" % time.strftime("%Y%m%d%H%M%S", time.gmtime())
    return os.path.join(folder, "%s%s" % (cleaned_filename.lower(), extension.lower()))


def create_archive_path(instance): 
    path = "export/%s/%s/" % (time.strftime("%Y%m%d%H%M%S", time.gmtime()), instance.uuid)
    path_full = os.path.join(PROJECT_DIR, 'media' ,path)
    
    os.makedirs(path_full)
    
    print 'path_full: %s' % path_full
    
    return path_full




class BaseModel(models.Model):

    created = CreationDateTimeField()
    updated = ModificationDateTimeField()

    uuid = UUIDField()
    
    class Meta:
        abstract = True
        
        
class Export(BaseModel):

    class Meta:
        app_label = 'exporter'
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')
        ordering = ('-created', )
    
    user = models.ForeignKey(User, blank=True, null=True, related_name="exports", on_delete=models.SET_NULL)
    status = models.PositiveIntegerField(default=0, choices=GENERIC_STATUS_CHOICES)
        
    size = models.IntegerField(default=0,blank=True, null=True)

    filename = models.CharField(max_length=256, blank=True, null=True)
    file = models.FileField(upload_to=create_download_path, blank=True, null=True)
    
    
    downloaded = models.DateTimeField(blank=True, null=True)
        
    TYPE_CHOICES = (
        ('web', _('Web Interface')),
        ('api', _('API')),
        ('fs', _('Filesystem')),
    )
    type = models.CharField(max_length="10", default='web', choices=TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True, help_text=_('Optionally, just add some notes to this export if desired.'))


    def __unicode__(self):
        return "%s" % self.created

    @models.permalink
    def get_absolute_url(self):
        return ('exporter-export-update', [str(self.pk)])

    @models.permalink
    def get_delete_url(self):
        return ('exporter-export-delete', [str(self.pk)])
    
    def get_api_url(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'export', 'api_name': 'v1'})
        return url
    
    def save(self, *args, **kwargs):
        super(Export, self).save(*args, **kwargs)
        

    #@models.permalink
    def get_delete_url(self):
        #return ('exporter-upload-delete', [str(self.pk)])
        return ''
    
    
    def process(self):
        log = logging.getLogger('exporter.models.process')
        log.info('Start process Export: %s' % (self.pk))

        if USE_CELERYD:
            self.process_task.delay(self)
        else:
            self.process_task(self)
        
    @task
    def process_task(obj):
        
        from settings import PROJECT_DIR
        
        archive_dir = create_archive_path(obj)
        
        archive_path = os.path.join(archive_dir, 'archive.zip')
        
        archive_file = ZipFile(archive_path, "w")
        
        # do shizzle
        for item in obj.export_items.all():
            print
            print 'item: %s' % item.content_type
            print 'pk: %s' % item.object_id
            
            # maybe not too elegant.. switching processing for different types
            if item.content_type.name.lower() == 'release':
                
                t_item = item.content_object
                
                print 'GOT RELEAZE!'
                
                for media in t_item.media_release.all():
                    print 'Media: %s' % media.name
                
                    archive_file.write(media.master.path, '%s.mp3' % media.name )
                    
                if t_item.main_image:
                    archive_file.write(t_item.main_image.path, 'cover.jpg')
                    
                    
                
            
            print
            
        
        #obj.file = DjangoFile(open(archive_path), u'archive.zip')
        obj.file = archive_file

            
        
        # update status
        obj.status = 1;
        obj.save()
        
    

        
 


        
def post_save_export(sender, **kwargs):
    
    obj = kwargs['instance']  
    # if status is 'rady' > run exporter
    if obj.status == 2:
        obj.process()
      
post_save.connect(post_save_export, sender=Export)  
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
    
class ExportItem(BaseModel):

    class Meta:
        app_label = 'exporter'
        verbose_name = _('Export Item')
        verbose_name_plural = _('Export Items')
        ordering = ('-created', )
    
    filename = models.CharField(max_length=256, blank=True, null=True)
    file = models.FileField(upload_to=create_download_path, blank=True, null=True)

    export_session = models.ForeignKey(Export, verbose_name=_('Export'), null=True, related_name='export_items')
    status = models.PositiveIntegerField(default=0, choices=GENERIC_STATUS_CHOICES)
    
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    
    def __unicode__(self):
        return self.filename

    #@models.permalink
    def get_delete_url(self):
        #return ('exporter-upload-delete', [str(self.pk)])
        return ''
    
    
    def process(self):
        log = logging.getLogger('exporter.models.process')
        log.info('Start processing ExportItem: %s' % (self.pk))
        log.info('Path: %s' % (self.file.path))
        
        if USE_CELERYD:
            self.process_task.delay(self)
        else:
            self.process_task(self)
        
    @task
    def process_task(obj):
        pass
    
    

    
    def save(self, *args, **kwargs):
        
        msg = {'key': 'save', 'content': 'object saved'}
        #self.messages.update(msg);

        if not self.filename:
            self.filename = self.file.name

        super(ExportItem, self).save(*args, **kwargs) # Call the "real" save() method.

        
def post_save_exportitem(sender, **kwargs):
    obj = kwargs['instance']
    if not obj.mimetype:
        mime = magic.Magic(mime=True)
        obj.mimetype = mime.from_file(obj.file.path.encode('ascii', 'ignore'))
        obj.save()
        
    if obj.status == 0:
        obj.process()
        
    if obj.status == 6:
        #pass
        obj.do_import()
      
#post_save.connect(post_save_exportitem, sender=ExportItem)      
  
def post_delete_exportitem(sender, **kwargs):
    import shutil
    obj = kwargs['instance']
    try:
        os.remove(obj.file.path)
    except:
        pass
      
#post_delete.connect(post_delete_exportitem, sender=ExportItem)

        
        
        