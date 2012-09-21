#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import datetime
import re

from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from django.db.models.signals import post_delete, post_save
from django.core.urlresolvers import reverse

from django_extensions.db.fields.json import JSONField

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

from util.process import Process

# extra fields
from django_extensions.db.fields import *

class BaseModel(models.Model):

    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    
    class Meta:
        abstract = True
        
        
class Import(BaseModel):

    class Meta:
        app_label = 'importer'
        verbose_name = _('Import')
        verbose_name_plural = _('Imports')
        ordering = ('-created', )
    
    
    user = models.ForeignKey(User, blank=True, null=True, related_name="import_user", on_delete=models.SET_NULL)
        
    STATUS_CHOICES = (
        (0, _('Init')),
        (1, _('Done')),
        (2, _('Ready')),
        (3, _('Progress')),
        (99, _('Error')),
        (11, _('Other')),
    )
    status = models.PositiveIntegerField(default=0, choices=STATUS_CHOICES)
        
    TYPE_CHOICES = (
        ('web', _('Web Interface')),
        ('api', _('API')),
        ('fs', _('Filesystem')),
    )
    type = models.CharField(max_length="10", default='web', choices=TYPE_CHOICES)
    
    

    def __unicode__(self):
        return "%s" % self.created

    @models.permalink
    def get_absolute_url(self):
        return ('importer-import-update', [str(self.pk)])


    def get_api_url(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'import', 'api_name': 'v1'})
        return url

    
    
class ImportFile(BaseModel):

    class Meta:
        app_label = 'importer'
        verbose_name = _('Import File')
        verbose_name_plural = _('Import Files')
        ordering = ('-created', )
    
    filename = models.CharField(max_length=256, blank=True, null=True)
    file = models.FileField(upload_to='dummy')
    import_session = models.ForeignKey(Import, verbose_name=_('Import'), null=True, related_name='files')
    
    mimetype = models.CharField(max_length=100, blank=True, null=True)
    
    
    """
    Result sets. Not stored in foreign model - as they are rather fix.
    And would imply code changes anyway...
    """
    
    results_tag = JSONField(blank=True, null=True)
    results_tag_status = models.PositiveIntegerField(verbose_name=_('Result Tags (ID3 & co)'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    results_musicbrainz = JSONField(blank=True, null=True)
    results_discogs_status = models.PositiveIntegerField(verbose_name=_('Result Musicbrainz'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    results_acoustid = JSONField(blank=True, null=True)
    results_acoustid_status = models.PositiveIntegerField(verbose_name=_('Result Musicbrainz'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    results_discogs = JSONField(blank=True, null=True)
    results_discogs_status = models.PositiveIntegerField(verbose_name=_('Result Discogs'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    
    
        
    STATUS_CHOICES = (
        (0, _('Init')),
        (1, _('Done')),
        (2, _('Ready')),
        (3, _('Progress')),
        (99, _('Error')),
        (11, _('Other')),
    )
    status = models.PositiveIntegerField(default=0, choices=STATUS_CHOICES)
    
    
    def __unicode__(self):
        return self.filename

    #@models.permalink
    def get_delete_url(self):
        #return ('importer-upload-delete', [str(self.pk)])
        return ''
    
    
    def process(self):
        log = logging.getLogger('importer.models.process')
        log.info('Start processing ImportFile: %s' % (self.pk))
        log.info('Path: %s' % (self.file.path))
        
        if USE_CELERYD:
            self.process_task.delay(self)
        else:
            self.process_task(self)
        

    @task
    def process_task(obj):
        
        processor = Process()
        metadata = processor.extract_metadata(obj.file)


        #time.sleep(1)

        obj.results_tag = metadata
        print "DONE!!!"
        print metadata
        obj.status = 3
        obj.save()
        
        
        obj.results_acoustid = processor.get_aid(obj.file)
        obj.save()

        
        
        
        
        

        
        
        
        
    
    
    def save(self, *args, **kwargs):

        if not self.filename:
            self.filename = self.file.name

        super(ImportFile, self).save(*args, **kwargs) # Call the "real" save() method.

        
def post_save_importfile(sender, **kwargs):
    obj = kwargs['instance']
    if not obj.mimetype:
        mime = magic.Magic(mime=True)
        obj.mimetype = mime.from_file(obj.file.path)
        obj.save()
        
    if obj.status == 0:
        obj.process()
      
post_save.connect(post_save_importfile, sender=ImportFile)      
  
def post_delete_importfile(sender, **kwargs):
    import shutil
    obj = kwargs['instance']
    try:
        os.remove(obj.file.path)
    except:
        pass
      
post_delete.connect(post_delete_importfile, sender=ImportFile)

        
        
        