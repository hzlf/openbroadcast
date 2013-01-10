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


from alibrary.models import Release, Media, Artist, Relation


from util.process import Process
from util.importer import Importer


import magic
from celery.task import task
import logging
log = logging.getLogger(__name__)

USE_CELERYD = True    
        
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



def clean_upload_path(instance, filename):
    import unicodedata
    import string
    filename, extension = os.path.splitext(filename)
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')    
    folder = "import/%s/" % time.strftime("%Y%m%d%H%M%S", time.gmtime())
    return os.path.join(folder, "%s%s" % (cleaned_filename.lower(), extension.lower()))







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
    
    notes = models.TextField(blank=True, null=True, help_text=_('Optionally, just add some notes to this import if desired.'))
    
    

    def __unicode__(self):
        return "%s" % self.created

    @models.permalink
    def get_absolute_url(self):
        return ('importer-import-update', [str(self.pk)])

    @models.permalink
    def get_delete_url(self):
        return ('importer-import-delete', [str(self.pk)])
    
    
    def get_stats(self):
        stats = {}
        stats['init'] = self.files.filter(status=0)
        stats['done'] = self.files.filter(status=1)
        stats['ready'] = self.files.filter(status=2)
        stats['working'] = self.files.filter(status=3)
        stats['warning'] = self.files.filter(status=4)
        stats['duplicate'] = self.files.filter(status=5)
        stats['queued'] = self.files.filter(status=6)
        stats['importing'] = self.files.filter(status=6)
        stats['error'] = self.files.filter(status=99)
        
        return stats
        

    def get_api_url(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'import', 'api_name': 'v1'})
        return url
    
    def save(self, *args, **kwargs):
        
        """
        stats = self.get_stats()
        
        if stats['done'].count() == self.files.count():
            self.status = 1
        
        if stats['done'].count() + stats['duplicate'].count() == self.files.count():
            self.status = 1
        
        if stats['error'].count() > 0:
            self.status = 99
        """   
        
        super(Import, self).save(*args, **kwargs)
 
    
class ImportFile(BaseModel):

    class Meta:
        app_label = 'importer'
        verbose_name = _('Import File')
        verbose_name_plural = _('Import Files')
        ordering = ('-created', )
    
    filename = models.CharField(max_length=256, blank=True, null=True)
    #file = models.FileField(upload_to='dummy')
    file = models.FileField(upload_to=clean_upload_path)

    import_session = models.ForeignKey(Import, verbose_name=_('Import'), null=True, related_name='files')
    
    mimetype = models.CharField(max_length=100, blank=True, null=True)
    
    messages = JSONField(blank=True, null=True, default=None)
    
    """
    Result sets. Not stored in foreign model - as they are rather fix.
    And would imply code changes anyway...
    """
    
    results_tag = JSONField(blank=True, null=True)
    results_tag_status = models.PositiveIntegerField(verbose_name=_('Result Tags (ID3 & co)'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    results_acoustid = JSONField(blank=True, null=True)
    results_acoustid_status = models.PositiveIntegerField(verbose_name=_('Result Musicbrainz'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    results_musicbrainz = JSONField(blank=True, null=True)
    results_discogs_status = models.PositiveIntegerField(verbose_name=_('Result Musicbrainz'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    results_discogs = JSONField(blank=True, null=True)
    #results_discogs_status = models.PositiveIntegerField(verbose_name=_('Result Discogs'), default=0, choices=GENERIC_STATUS_CHOICES)
    
    import_tag = JSONField(blank=True, null=True)
    
    # actual media!
    media = models.ForeignKey(Media, blank=True, null=True, related_name="importfile_media", on_delete=models.SET_NULL)
    
    imported_api_url = models.CharField(max_length=512, null=True, blank=True)
    
    
        
    STATUS_CHOICES = (
        (0, _('Init')),
        (1, _('Done')),
        (2, _('Ready')),
        (3, _('Working')),
        (4, _('Warning')),
        (5, _('Duplicate')),
        (6, _('Queued')),
        (7, _('Importing')),
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
        
        
        
        media_id = processor.get_echoprint(obj.file)
        metadata = processor.extract_metadata(obj.file)
        
        if media_id:
            obj.results_tag = metadata

            obj.media = Media.objects.get(pk=media_id)
            
            print "DUPLICATE!!!"
            obj.results_tag_status = True
            obj.status = 5
            obj.save()
            
        else:
            
    
            #time.sleep(1)
    
            obj.results_tag = metadata
            print "DONE!!!"
            print metadata
            print 
            obj.status = 3
            obj.results_tag_status = True
            obj.save()
            
            
            obj.results_acoustid = processor.get_aid(obj.file)
            obj.results_acoustid_status = True
            obj.save()
    
            obj.results_musicbrainz = processor.get_musicbrainz(obj)
            obj.results_discogs_status = True
            obj.save()
            
            obj.status = 2
            obj.results_tag_status = True
            obj.save()
    
    
    def do_import(self):
        log = logging.getLogger('importer.models.do_import')
        log.info('Start importing ImportFile: %s' % (self.pk))
        log.info('Path: %s' % (self.file.path))
        
        if USE_CELERYD:
            self.import_task.delay(self)
        else:
            self.import_task(self)
        
    @task
    def import_task(obj):

        importer = Importer()
        
        media, status = importer.run(obj)
        
        if media:
            obj.media = media
            obj.status = 1
            
        else:
            obj.status = 99
            
        obj.save()



    
    def save(self, *args, **kwargs):
        
        msg = {'key': 'save', 'content': 'object saved'}
        #self.messages.update(msg);

        if not self.filename:
            self.filename = self.file.name

        super(ImportFile, self).save(*args, **kwargs) # Call the "real" save() method.

        
def post_save_importfile(sender, **kwargs):
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
      
post_save.connect(post_save_importfile, sender=ImportFile)      
  
def post_delete_importfile(sender, **kwargs):
    import shutil
    obj = kwargs['instance']
    try:
        os.remove(obj.file.path)
    except:
        pass
      
post_delete.connect(post_delete_importfile, sender=ImportFile)

        
        
        