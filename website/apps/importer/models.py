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

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django_extensions.db.fields.json import JSONField


from alibrary.models import Release, Media, Artist, Relation, Playlist


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

    uuid = UUIDField()
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
        return '%s%s/' % (url, self.pk)
    
    def apply_import_tag(self, importfile, **kwargs):
        print 'apply_import_tag:'
        print importfile.import_tag
        
        
        if 'mb_release_id' in importfile.import_tag:
        
            mb_release_id = importfile.import_tag['mb_release_id']
            
            qs = self.files.exclude(pk=importfile.pk)
            importfiles = qs.filter(status=2)
            for file in importfiles:
                print '*************************'
                print file
                print 'mb results'
                for mb in file.results_musicbrainz:
                    print mb
                    
                    # got a match - try to apply
                    if 'mb_id' in mb and mb['mb_id'] == mb_release_id:
                        print 'GOT A MATCH!!!'
                        # main id
                        file.import_tag['mb_release_id'] = mb_release_id
                        # textual
                        file.import_tag['release'] = mb['name']
                        file.import_tag['artist'] = mb['artist']['name']
                        file.import_tag['name'] = mb['media']['name']
                        # mb ids
                        file.import_tag['mb_artist_id'] = mb['artist']['mb_id']
                        file.import_tag['mb_track_id'] = mb['media']['mb_id']
                        
                        kwargs['skip_apply_import_tag'] = True
                        file.save(**kwargs)
                    
                print
                


    def add_to_playlist(self, item):
        pass
    
    def add_to_collection(self, item):
        pass




    # importitem handling
    def add_importitem(self, item):
        ctype = ContentType.objects.get_for_model(item)
        
        item, created = ImportItem.objects.get_or_create(object_id=item.pk, content_type=ctype, import_session=self)
    
        if created:
            self.add_to_playlist(item)
            self.add_to_collection(item)
    
        return item
    
    def get_importitem_ids(self, ctype):
        ii_ids = ImportItem.objects.filter(content_type=ctype, import_session=self).values_list('object_id', flat=True)
        return ii_ids

        
    
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
        ordering = ('created', )
    
    filename = models.CharField(max_length=256, blank=True, null=True)
    #file = models.FileField(upload_to='dummy')
    file = models.FileField(max_length=256, upload_to=clean_upload_path)

    import_session = models.ForeignKey(Import, verbose_name=_('Import'), null=True, related_name='files')
    
    mimetype = models.CharField(max_length=100, blank=True, null=True)
    
    messages = JSONField(blank=True, null=True, default=None)
    
    """
    Result sets. Not stored in foreign model - as they are rather fix.
    """
    
    settings = JSONField(blank=True, null=True)
    
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
        

    def get_api_url(self):
        url = reverse('api_dispatch_list', kwargs={'resource_name': 'importfile', 'api_name': 'v1'})
        return '%s%s/' % (url, self.pk)
    

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
        
        # to prevent circular import errors
        from util.process import Process
        
        processor = Process()
        
        # duplicate check by sha1
        media_id = processor.id_by_sha1(obj.file)
        
        # duplicate check by echoprint
        if not media_id:
            media_id = processor.id_by_echoprint(obj.file)
        
        metadata = processor.extract_metadata(obj.file)
        
        
        # try to get media by id returned from fingerprinter
        media = None
        if media_id:
            try:
                media = Media.objects.get(pk=media_id)
            except:
                pass
        
        
        if media:
            obj.results_tag = metadata

            obj.media = media
            
            print "DUPLICATE!!!"
            # obj.results_tag_status = True
            # obj.status = 5
            # obj.save()
            
        else:
            
            pass
            
    
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
        
        # requeue if no results yet
        print 'MB YET!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        if len(obj.results_musicbrainz) < 1:
            s = {'skip_tracknumber': True}
            obj.settings = s
            obj.save()
            obj.results_musicbrainz = processor.get_musicbrainz(obj)
            obj.save()
            
        
        obj.status = 2
        
        if media:
            obj.status = 5
            # add to session
            self.import_session.add_importitem(obj)
        
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
        log = logging.getLogger('importer.models.import_task')
        log.info('Starting import task for:  %s' % (obj.pk))
        # to prevent circular import errors
        from util.importer import Importer
        importer = Importer()
        
        media, status = importer.run(obj)

        """   """      
        if media:
            print 'GOT MEDIA - SAVE IT'
            print media
            obj.media = media
            print obj.media
            
            obj.status = 1
            
        else:
            obj.status = 99
        
        log.info('Ending import task for:  %s' % (obj.pk))
        obj.save()
    
    def save(self, skip_apply_import_tag=False, *args, **kwargs):
        
        msg = {'key': 'save', 'content': 'object saved'}
        #self.messages.update(msg);

        if not self.filename:
            self.filename = self.file.name
            
        # check/update import_tag
        if self.status == 2: # ready
            from util.importer import Importer
            importer = Importer()
            
            self.import_tag = importer.complete_import_tag(self)
            

        if self.status == 2: # ready
            # try to apply import_tag to other files of this import session
            if not skip_apply_import_tag:
                self.import_session.apply_import_tag(self)
                
        # check import_tag for completeness
        if self.status == 2 or self.status == 4: # ready
            media = self.import_tag.get('name', None)
            artist = self.import_tag.get('artist', None)
            release = self.import_tag.get('release', None)
            
            print 'media: %s' % media
            print 'artist: %s' % artist
            print 'release: %s' % release
            
            if media and artist and release:
                print 'all ok'
                self.status = 2
            else:
                print 'missing!'
                self.status = 4

            

        super(ImportFile, self).save(*args, **kwargs)

        
def post_save_importfile(sender, **kwargs):
    print 'post_save_importfile - kwargs'

    obj = kwargs['instance']
    if not obj.mimetype:
        mime = magic.Magic(mime=True)
        obj.mimetype = mime.from_file(obj.file.path.encode('ascii', 'ignore'))
        obj.save()
        
    if obj.status == 0:
        obj.process()
        
    
    if obj.status == 6:
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












"""
ImportItem
store relations to objects created/assigned during that specific import
"""

class ImportItem(BaseModel):
        
    # limit to alibrary objects
    ct_limit = models.Q(app_label = 'alibrary', model = 'media') | \
    models.Q(app_label = 'alibrary', model = 'release') | \
    models.Q(app_label = 'alibrary', model = 'artist') | \
    models.Q(app_label = 'alibrary', model = 'label')
    
    import_session = models.ForeignKey(Import, verbose_name=_('Import'), null=True, related_name='importitem_set')
    
    content_type = models.ForeignKey(ContentType, limit_choices_to = ct_limit)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = 'importer'
        verbose_name = _('Import Item')
        verbose_name_plural = _('Import Items')
        #ordering = ('-created', )
        
    def __unicode__(self):
        try:
            return '%s | %s' % (ContentType.objects.get_for_model(self.content_object), self.content_object.name)
        except:
            return '%s' % (self.pk)
            
    
    def save(self, *args, **kwargs):
        super(ImportItem, self).save(*args, **kwargs) 













        
        