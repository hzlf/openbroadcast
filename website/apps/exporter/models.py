#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import datetime
import re
import shutil
import urllib

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

from django.utils.hashcompat import sha_constructor

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
    (4, _('Downloaded')),
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
    folder = "export/processed/%s-%s/" % (time.strftime("%Y%m%d%H%M%S", time.gmtime()) ,instance.uuid)
    return os.path.join(folder, "%s%s" % (cleaned_filename.lower(), extension.lower()))


def create_export_path():
    import unicodedata
    import string
    filename, extension = os.path.splitext(filename)
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')    
    folder = "export/%s/" % time.strftime("%Y%m%d%H%M%S", time.gmtime())
    return os.path.join(folder, "%s%s" % (cleaned_filename.lower(), extension.lower()))


def create_archive_dir(instance): 
    path = "export/cache/%s-%s/" % (time.strftime("%Y%m%d%H%M%S", time.gmtime()), instance.uuid)
    path_full = os.path.join(PROJECT_DIR, 'media',path)
    
    # debug:
    path_full = os.path.join(PROJECT_DIR, 'media' , 'export/debug/')
    try:
        os.makedirs(os.path.join(path_full, 'cache/'))
    except OSError, e:
        pass # file exists
    
    print 'archive dir: %s' % path_full
    
    return path_full




class BaseModel(models.Model):

    created = CreationDateTimeField()
    updated = ModificationDateTimeField()

    uuid = UUIDField()
    
    class Meta:
        abstract = True
        
        
class Export(BaseModel):

    FORMAT_CHOICES = (
        ('mp3', _('MP3')),
        ('flac', _('Flac')),
    )

    class Meta:
        app_label = 'exporter'
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')
        ordering = ('created', )
    
    user = models.ForeignKey(User, blank=True, null=True, related_name="exports", on_delete=models.SET_NULL)
    status = models.PositiveIntegerField(default=0, choices=GENERIC_STATUS_CHOICES)
        

    filesize = models.IntegerField(default=0,blank=True, null=True)

    filename = models.CharField(max_length=256, blank=True, null=True)
    file = models.FileField(upload_to=create_download_path, blank=True, null=True)
    fileformat = models.CharField(max_length=4, default='mp3', choices=FORMAT_CHOICES)
    
    token = models.CharField(max_length=256, blank=True, null=True)
    
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

    
    @models.permalink
    def get_download_url(self):

        return ('exporter-export-download', (), {'uuid': self.uuid, 'token': self.token})
        #return ('exporter-export-download', [self.uuid])

    def get_api_url(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'export', 'api_name': 'v1'})
        return url
    
    def save(self, *args, **kwargs):
        
        if not self.token:
            self.token = sha_constructor('asd' + self.uuid).hexdigest()
        
        super(Export, self).save(*args, **kwargs)
        

    #@models.permalink
    def get_delete_url(self):
        #return ('exporter-upload-delete', [str(self.pk)])
        return ''
    
    def set_downloaded(self):
        self.downloaded = datetime.datetime.now()
        self.status = 4
        self.save()
        
        return None
        
    
    
    def process(self):
        log = logging.getLogger('exporter.models.process')
        log.info('Start process Export: %s' % (self.pk))

        if USE_CELERYD:
            self.process_task.delay(self)
        else:
            self.process_task(self)
        
    @task
    def process_task(obj):
        
        from atracker.util import create_event
        
        process = Process()
        
        log = logging.getLogger('exporter.models.process_task')
        
        archive_dir = create_archive_dir(obj)
        archive_cache_dir = os.path.join(archive_dir, 'cache/')
        archive_path = os.path.join(archive_dir, 'archive') # .zip appended by 'make_archive'
        #archive_file = ZipFile(archive_path, "w")
        
        log.debug('archive_dir: %s' % (archive_dir))
        log.debug('archive_cache_dir: %s' % (archive_cache_dir))
        log.debug('archive_path: %s' % (archive_path))
        
        # do shizzle
        for item in obj.export_items.all():
            print
            print 'item: %s' % item.content_type
            print 'pk: %s' % item.object_id
            
            # maybe not too elegant.. switching processing for different types
            if item.content_type.name.lower() == 'release':
                
                t_item = item.content_object
                
                filename_format = '%s - %s - %s.%s'
                
                print 'GOT RELEAZE!'
                
                for media in t_item.media_release.all():
                    print 'Media: %s' % media.name
                
                    if obj.fileformat == 'mp3':
                
                        filename = filename_format % (media.tracknumber, media.name, media.artist.name, 'mp3')
                        filepath = os.path.join(archive_cache_dir, filename)
                        
                        shutil.copyfile(media.get_cache_file('mp3', 'base'), filepath)
                        process.incect_metadata(filepath, media)
                
                    # just dummy - not possible...
                    if obj.fileformat == 'flac':
                
                        filename = filename_format % (media.tracknumber, media.name, media.artist.name, 'mp3')
                        filepath = os.path.join(archive_cache_dir, filename)
                        
                        shutil.copyfile(media.get_cache_file('mp3', 'base'), filepath)
                        process.incect_metadata(filepath, media)
                        
                    create_event(obj.user, media, None, 'download')
                    
                if t_item.main_image:
                    pass
                    #archive_file.write(t_item.main_image.path, 'cover.jpg')
                    
                    
                
            
            print
            
        shutil.make_archive(archive_path, 'zip', archive_cache_dir)
            
        
        obj.file = DjangoFile(open(archive_path + '.zip'), u'archive.zip')
        obj.filesize = os.path.getsize(archive_path + '.zip')

            
        # get filesize
        obj.filename = generate_export_filename(obj.export_items)
        #obj.filename = 'asdasdas'
        
        # update status
        obj.status = 1;
        obj.save()
        
        # clean archive dir
        #shutil.rmtree(archive_dir)
    

        
def generate_export_filename(qs_export_items):
    
    filename = _('unknown')
    if qs_export_items.count() == 1:
        item = qs_export_items.all()[0]
        if item.content_type.name.lower() == 'release':
            filename = item.content_object.name.encode('ascii', 'ignore')
        
    if qs_export_items.count() > 1:
        filename = _('multiple-items')
        
    return filename


        
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
    
    #filename = models.CharField(max_length=256, blank=True, null=True)
    #file = models.FileField(upload_to=create_download_path, blank=True, null=True)

    export_session = models.ForeignKey(Export, verbose_name=_('Export'), null=True, related_name='export_items')
    status = models.PositiveIntegerField(default=0, choices=GENERIC_STATUS_CHOICES)
    
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    
    def __unicode__(self):
        return '%s - %s' % (self.pk, self.status)

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

        #if not self.filename:
        #    self.filename = self.file.name

        super(ExportItem, self).save(*args, **kwargs)

        
def post_save_exportitem(sender, **kwargs):
    obj = kwargs['instance']


    """        
    if obj.status == 0:
        obj.process()
    """
      
#post_save.connect(post_save_exportitem, sender=ExportItem)      
  
def post_delete_exportitem(sender, **kwargs):
    import shutil
    obj = kwargs['instance']
    try:
        os.remove(obj.file.path)
    except:
        pass
      
#post_delete.connect(post_delete_exportitem, sender=ExportItem)

        
        
        