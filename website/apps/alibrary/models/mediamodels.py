# python
import datetime
import uuid
import shutil
import sys
import time
import subprocess
import sys
import struct
import json

# django
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.files import File as DjangoFile
from django.core.urlresolvers import reverse

from django.http import HttpResponse # needed for absolute url

# TODO: only import needed settings
from settings import *



# django-extensions (http://packages.python.org/django-extensions/)
from django_extensions.db.fields import AutoSlugField
from lib.fields.uuidfield import UUIDField as RUUIDField

# cms
from cms.models import CMSPlugin, Page
from cms.models.fields import PlaceholderField
from cms.utils.placeholder import get_page_from_placeholder_if_exists

# filer
from filer.models.filemodels import *
from filer.models.foldermodels import *
from filer.models.audiomodels import *
from filer.models.imagemodels import *
from filer.fields.image import FilerImageField
from filer.fields.audio import FilerAudioField
from filer.fields.file import FilerFileField

# private_files
from private_files import PrivateFileField

# modules
#from taggit.managers import TaggableManager
from django_countries import CountryField
from easy_thumbnails.files import get_thumbnailer

# audiotools (for conversion)
from audiotools import AudioFile, MP3Audio, M4AAudio, FlacAudio, WaveAudio, MetaData
import audiotools
import tempfile

# celery / task management
from celery.task import task


# shop
from shop.models import Product
from alibrary.nonconflict import classmaker
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField 

# audio processing / waveform
from lib.audioprocessing.processing import create_wave_images, AudioProcessingException

# hash
from lib.util.sha1 import sha1_by_file

# echoprint
from ep.API import fp

# logging
import logging
log = logging.getLogger(__name__)
    
    
################
from alibrary.models.basemodels import *
from alibrary.models.artistmodels import *
from alibrary.models.releasemodels import *
from alibrary.models.playlistmodels import *

from alibrary.util.signals import library_post_save
from alibrary.util.slug import unique_slugify

import arating







def clean_filename(filename):
    import unicodedata
    import string
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    cleaned = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleaned if c in valid_chars)

def masterpath_by_uuid(instance, filename):
    filename, extension = os.path.splitext(filename)
    folder = "private/%s/" % (instance.uuid.replace('-', '/'))
    #filename = instance.uuid.replace('-', '/') + extension
    filename = u'master'
    return os.path.join(folder, "%s%s" % (clean_filename(filename).lower(), extension.lower()))




class Media(MigrationMixin):
    
    # core fields
    uuid = RUUIDField(primary_key=False)
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)
    
    
    isrc = models.CharField(verbose_name='ISRC', max_length=12, null=True, blank=True)
    
    # processed & lock flag (needed for models that have maintenance/init/save tasks)
    PROCESSED_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    processed = models.PositiveIntegerField(max_length=2, default=0, choices=PROCESSED_CHOICES)
    
    ECHOPRINT_STATUS_CHOICES = (
        (0, _('Init')),
        (1, _('Assigned')),
        (2, _('Error')),
    )
    echoprint_status = models.PositiveIntegerField(max_length=2, default=0, choices=ECHOPRINT_STATUS_CHOICES)
        
    CONVERSION_STATUS_CHOICES = (
        (0, _('Init')),
        (1, _('Completed')),
        (2, _('Error')),
    )
    conversion_status = models.PositiveIntegerField(max_length=2, default=0, choices=CONVERSION_STATUS_CHOICES)
    
    
    
    lock = models.PositiveIntegerField(max_length=1, default=0, editable=False)
    
    tracknumber = models.PositiveIntegerField(max_length=12, default=0)
    
    MEDIATYPE_CHOICES = (
        ('track', _('Track')),
        ('remix', _('Remix')),
        ('mix', _('DJ-Mix')),
        ('other', _('Other')),
    )
    mediatype = models.CharField(verbose_name=_('Type'), max_length=12, default='track', choices=MEDIATYPE_CHOICES)
    
    description = models.TextField(verbose_name="Extra Description / Tracklist", blank=True, null=True)
    
    duration = models.PositiveIntegerField(verbose_name="Duration (in ms)", max_length=12, blank=True, null=True, editable=False)
    
    # relations
    release = models.ForeignKey('Release', blank=True, null=True, related_name='media_release', on_delete=models.SET_NULL)
    artist = models.ForeignKey('Artist', blank=True, null=True, related_name='media_artist')
    
    # relations a.k.a. links
    relations = generic.GenericRelation(Relation)
    
    # extra-artists
    # TODO: Fix this - guess should relate to Artist instead of Profession
    extra_artists = models.ManyToManyField(Profession, through='MediaExtraartists', blank=True, null=True)
    
    license = models.ForeignKey(License, blank=True, null=True, related_name='media_license')
    
    # File related (old)
    #master = FilerAudioField(blank=True, null=True, related_name='media_master')
    #master_path = models.CharField(max_length=2048, null=True, blank=True, help_text="Master Path", editable=False)
    #folder = models.ForeignKey(Folder, blank=True, null=True, related_name='media_folder', editable=False, on_delete=models.SET_NULL)
    
    # File related (new)
    master = models.FileField(max_length=1024, upload_to=masterpath_by_uuid, blank=True, null=True)
    master_sha1 = models.CharField(max_length=64, db_index=True, blank=True, null=True)
    
    
    folder = models.CharField(max_length=1024, null=True, blank=True, editable=False)
    
    # File Data
    base_format = models.CharField(verbose_name=_('Format'), max_length=12, blank=True, null=True)
    base_filesize = models.PositiveIntegerField(verbose_name=_('Filesize'), blank=True, null=True)
    base_duration = models.FloatField(verbose_name=_('Duration'), blank=True, null=True)
    base_samplerate = models.PositiveIntegerField(verbose_name=_('Samplerate'), blank=True, null=True)
    base_bitrate = models.PositiveIntegerField(verbose_name=_('Bitrate'), blank=True, null=True)
    
    # tagging
    #tags = TaggableManager(blank=True)
    
    # manager
    objects = models.Manager()
    
    # auto-update
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)


    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Track')
        verbose_name_plural = _('Tracks')
        ordering = ('tracknumber', )
    
    
    def __unicode__(self):
        return self.name

    
    @models.permalink
    def get_absolute_url(self):
        return ('alibrary-media-detail', [self.slug])

    @models.permalink
    def get_edit_url(self):
        return ('alibrary-media-edit', [self.pk])
    
    @models.permalink
    def get_stream_url(self):
        return ('alibrary-media-stream_html5', [self.uuid])
    
    @models.permalink
    def get_waveform_url(self):
        return ('alibrary-media-waveform', [self.uuid])
    

    def get_api_url(self):
        return reverse('api_dispatch_detail', kwargs={  
            'api_name': 'v1',  
            'resource_name': 'track',  
            'pk': self.pk  
        }) + ''
    
    def release_link(self):
        if self.release:
            return '<a href="%s">%s</a>' % (reverse("admin:alibrary_release_change", args=(self.release.id,)), self.release.name)
        return None
    
    release_link.allow_tags = True
    release_link.short_description = "Edit" 
    
    def get_playlink(self):
        return '/api/tracks/%s/#0#replace' % self.uuid
    
    
    def get_download_permissions(self):
        pass
    


    def generate_sha1(self):
        return sha1_by_file(self.master)
    
    
    
    
    def get_products(self):
        return self.mediaproduct.all()
    
    
    
    def get_download_url(self, format, version):
        
        return '%sdownload/%s/%s/' % (self.get_absolute_url(), format, version)
    
    
    def get_master_path(self):
        return self.master.path
    
    # full absolute path
    def get_folder_path(self, subfolder=None):
        
        if not self.folder:
            return None
        
        if subfolder:
            folder = "%s/%s%s/" % (MEDIA_ROOT, self.folder, subfolder)
            if not os.path.isdir(folder):
                os.mkdir(folder, 0755)
                
            return folder
                    
        return "%s/%s" % (MEDIA_ROOT, self.folder)
    
    """
    gets the 'real' file, eg flac-master, stream-preview etc.
    """
    def get_file(self, source, version):
        # TODO: implement...
        return self.master
    
    def get_stream_file(self, format, version):
        # TODO: improve...
        
        if format == 'mp3' and version == 'base':
            ext = os.path.splitext(self.master.path)[1][1:].strip() 
            if ext == 'mp3':
                return self.master
        
        filename = str(version) + '.' + str(format)
        file = File.objects.get(original_filename=filename, folder=self.folder)
        
        return file.file
    
    
    def get_default_stream_file(self):
        return self.get_stream_file('mp3', 'base')
    
    def get_cache_file(self, format, version):
        
        filename = str(version) + '.' + str(format)
        
        full_path = "%s%s" % (self.get_folder_path('cache'), filename)
        
        if not os.path.isfile(full_path):
            return None
        
        return full_path
    
    def get_waveform_image(self):
        
        waveform_image = self.get_cache_file('png', 'waveform')
        
        if not waveform_image:
            try:
                self.create_waveform_image()
                waveform_image = self.get_cache_file('png', 'waveform')
            except:
                waveform_image = None
            
        return waveform_image
        

        
    def get_duration(self):
    
        if self.duration:
            print 'from cache:'
            return self.duration
        else:
            try:
                self.duration = int(self.get_audiofile().seconds_length() * 1000)
                #self.save()
                return self.duration
            except Exception, e:
                return None
    
    """
    shortcut to audiotools api
    """
    def get_audiofile(self):
        try:
            return audiotools.open(self.get_master_path())
        except Exception, e:
            print e
            return None
        
    
    """
    Conversion flow:
     - create target folder
       ***/cache/<media uuid>/
    
     - src -> temp-file in destination format (eg /tmp/xyz-tempfile.mp3)
     - add file to filer-folder (think about creating filermodel for cache-file)
     
    """
    # send task to celeryd
    # @task
    def convert(self, format, version):
        
        log = logging.getLogger('alibrary.mediamodels.convert')
        
        log.info('Media id: %s - Encoder: %s/%s' % (self.pk, format, version))
        
        status = 0
        
        dst_file = str(version) + '.' + str(format)
        #src_path = self.master.path
        src_path = self.get_master_path()
    
        tmp_directory = tempfile.mkdtemp()
        tmp_path = tmp_directory + '/' + dst_file
        
        log.info('Media id: %s - dst_file: %s' % (self.pk, dst_file))
        log.info('Media id: %s - src_path: %s' % (self.pk, src_path))
        log.info('Media id: %s - tmp_path: %s' % (self.pk, tmp_path))
        
        
        """
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        print 'Media id: %s - dst_file: %s' % (self.pk, dst_file)
        print 'Media id: %s - src_path: %s' % (self.pk, src_path)
        print 'Media id: %s - tmp_path: %s' % (self.pk, tmp_path)
        """

    
        """
        get duration
        """
        if not self.duration:
            try:
                self.duration = int(self.get_audiofile().seconds_length() * 1000)
            except Exception, e:
                print e
                self.duration = 0
        
        
        """
        create a converted version of the master, stored in temp location
        """
        #try:
        print '*******************************************************'
        print 'Tmp file at: %s' % tmp_path
        print 'Source file at: %s' % src_path
        print 'Destination file at: %s' % dst_file
        print '*******************************************************'


        if format == 'mp3':
            # TODO: make compression variable / configuration dependant
            
            compression = '2'
            skip_conversion = False
            
            print 'Version: %s' % version

            if version == 'base':
                
                # skip conversino in case of mp3 - just use the original file
                ext = os.path.splitext(src_path)[1][1:].strip() 
                if ext == 'mp3':
                    print 'skip conversion - mp3 > mp3'
                    tmp_path = src_path
                    skip_conversion = True
                
                compression = '0'
                
            if version == 'low':
                compression = '6'
            
            
            
            if not skip_conversion:
                print '> AUDIOTOOLS: conversion to mp3'
                audiotools.open(src_path).convert(tmp_path, audiotools.MP3Audio, compression=compression, progress=self.convert_progress)

        
        if format == 'flac':
            # TODO: make compression variable / configuration dependant
            print '> AUDIOTOOLS: conversion to flac'
            audiotools.open(src_path).convert(tmp_path, audiotools.FlacAudio, progress=self.convert_progress)

        
        converted = True
        
        print '* END OF CONVERSION *******************************************'
        
        """
        finaly create a django file object and attach it to the medias cache folder
        """
        try:
            
            dst_final = self.get_folder_path('cache')
            
            print "Final Source: %s" % tmp_path
            print "Final Destination: %s" % dst_final + dst_file
            

            shutil.copy2(tmp_path, dst_final + dst_file)
            
            #tmp_file = DjangoFile(open(tmp_path), name=dst_file)


            status = 1
        
        except Exception, e:
            print "error adding file to the cache :( "
            status = 2
            print e
        
        
        """
        cleanup temp-files
        """
        try:
            shutil.rmtree(tmp_directory)
            pass
        except Exception, e:
            print e

        
        return status
        
        

    @task
    def grappher(self, width, height):
        """
        
        """
        pass
    
    

    def create_waveform_image(self):

        tmp_directory = tempfile.mkdtemp()

        src_path = self.master.path;
        tmp_path = os.path.join(tmp_directory, 'tmp.wav')
        dst_path = os.path.join(self.get_folder_path('cache'), 'waveform.png')
        
        print 'create waveform'
        print 'src_path: %s' % src_path
        print 'tmp_path: %s' % tmp_path
        print 'dst_path: %s' % dst_path
        
        audiotools.open(src_path).convert(tmp_path, audiotools.WaveAudio)
        
        args = (tmp_path, dst_path, None, 1800, 301, 2048)
        create_wave_images(*args)
        
        try:
            shutil.rmtree(tmp_directory)
        except Exception, e:
            print e
            
        return

 
       
    #@task
    def build_cache(self):
        
        # get settings
        formats_download = FORMATS_DOWNLOAD 
        waveform_sizes = WAVEFORM_SIZES
        
        
        # cleanup:
        # delete everything that 'could' be in the cache so far...
        print '# formats_download:'

        for format, variations in formats_download.iteritems():
            for variation in variations:
                
                filename = '%s_%s.%s' % ('download', variation, format)
                tmp_directory = self.convert_(filename, self.folder, format, variation)
                
                
                """
                if sucessfully converted, create a django/filer file from temp_file
                """
                if tmp_directory:
                    tmp_path =  tmp_directory + '/' + filename
                    try:
                        tmp_file = DjangoFile(open(tmp_path),name=filename)            
                        file, created = File.objects.get_or_create(
                                                        original_filename=tmp_file.name,
                                                        file=tmp_file,
                                                        folder=self.folder,
                                                        is_public=False)
                        self.status = 1
                    
                    except Exception, e:
                        self.status = 2
                        print e
                        
                        

                try:
                    shutil.rmtree(tmp_directory)
                except Exception, e:
                    print e
                    
                    
                self.save()
            
            

        
        
        # convert:
        # get needed output-formats
        
        
        # grappher:
        # get needed output-formats
        
        
        
        pass
       
       
       
       
       
            
    """
    progress/callback functions
    TODO: unify calls
    """
    def convert_progress(self, x, y):
        p = (x * 100 / y)
        if (p%10) == 0:
            print p

        
    def progress_callback(self, percentage):
        pass
        #print 'waveform:',
        #print str(percentage)
        
        
    
    def dummy(self):
        
        formats_media = FORMATS_MEDIA
        
        for source, versions in formats_media.iteritems():
            for version in versions:
                print "%s/%s" % (source, version)
    
    
    def generate_media_versions(self):
        time.sleep(2)
        log = logging.getLogger('alibrary.mediamodels.generate_media_versions')
        self.generate_media_versions_task.delay(self)
        
    """
    format conversion & co. takes the master and processes versions as configured
    """
    @task
    def generate_media_versions_task(obj):
        
        log = logging.getLogger('alibrary.mediamodels.generate_media_versions_task')
        
        log.info('Start conversion for Media: %s' % (obj.pk))
        print 'Start conversion for Media: %s' % (obj.pk)
        
        print 
        print '************************************************************'
        print 'Delete files from cache folder'
        folder = obj.get_folder_path('cache')
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                print 'Unlinking: %s' % file_path
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e
        
        
        
        print 'Sleeping 2 secs.. To be sure the transaction is completed.'
        time.sleep(2)
        print
        

        formats_media = FORMATS_MEDIA
        
        for source, versions in formats_media.iteritems():
            for version in versions:
                print 'Media id: %s - Sending to Encoder: %s/%s' % (obj.pk, source, version)
                log.info('Media id: %s - Sending to Encoder: %s/%s' % (obj.pk, source, version))
                try:
                    obj.convert(source, version)
                except Exception, e:
                    print e
                    pass

        
        # check if everything went fine (= if cache files available)

        c = obj.get_cache_file('mp3', 'base')
        if c:
            print c            
            obj.conversion_status = 1;
            obj.save();
        else:
            obj.conversion_status = 2;
            obj.save();

        
        print "* EOL"
            
            




    def inject_metadata(self, format, version):
        
        """
        audiotools.MetaData
        """
        meta = MetaData()
        
        
        """
        prepare metadata object
        """
        # track-level metadata
        meta.track_name = self.name
        meta.track_number = self.tracknumber
        meta.media = 'DIGITAL'
        meta.isrc = self.isrc
        

            
        """ Needs fixing...
        for extra_artist in self.extra_artists.all():
            print extra_artist
        meta.performer_name =
        meta.composer_name =
        meta.conductor_name =
        """
        
        # release-level metadata
        if self.release:
            meta.album_name = self.release.name
            meta.catalog = self.release.catalognumber
            meta.track_total = len(self.release.media_release.all())
            
            if self.release.releasedate:
                try:
                    meta.year = str(self.release.releasedate.year)
                    meta.date = str(self.release.releasedate)
                    
                except Exception, e:
                    print e
            
            try:
                
                cover_image = self.release.cover_image if self.release.cover_image else self.release.main_image
                
                if meta.supports_images() and cover_image:
                    for i in meta.images():
                        meta.delete_image(i)
                        
                    opt = dict(size=(200, 200), crop=True, bw=False, quality=80)
                    image = get_thumbnailer(cover_image).get_thumbnail(opt)
                    meta.add_image(get_raw_image(image.path, 0))
                    
            except Exception, e:
                print e
                
            
        # artist-level metadata
        if self.artist:
            meta.artist_name = self.artist.name
                    
        # label-level metadata
        if self.release.label:
            pass
            # meta.artist_name = self.artist.name

        """
        get corresponding file and apply the metadata
        """
        cache_file = self.get_cache_file(format, version)
        try:
            audiotools.open(cache_file.path).set_metadata(meta)
        except Exception, e:
            print e
        return cache_file
    
    
    """
    creates an echoprint fp and post it to the 
    identification server
    """
    def update_echoprint(self):
        #self.update_echoprint_task.delay(self)
        self.update_echoprint_task(self)
        
    @task()
    def update_echoprint_task(obj):
        
        from settings import ECHOPRINT_CODEGEN_BIN
        
        
        ecb = ECHOPRINT_CODEGEN_BIN
        ecb = 'echoprint-codegen'
        
        path = obj.get_master_path()
        
        #path = obj.master_path
        
        print 'path: %s' % path
        
        p = subprocess.Popen([
            ecb, path,
        ], stdout=subprocess.PIPE)
        stdout = p.communicate()        
        d = json.loads(stdout[0])
        
        # print d
        
        try:
            code = d[0]['code']
            version = d[0]['metadata']['version']
            duration = d[0]['metadata']['duration']
        except Exception, e:
            print e
            code = None
            version = None
            duration = None
            status = 2
            
            
        if code:
            
            try:
            
                print 'delete fingerprint on server id: %s' % obj.id 
                fp.delete("%s" % obj.id)
                
                print 'post new fingerprint:'
                code_pre = code
                id = obj.updated.isoformat('T')[:-7]
                code = fp.decode_code_string(code)
                
                nfp = {
                        "track_id": "%s" % obj.id,
                        "fp": code,
                        #"artist": "%s" % obj.artist.id,
                        #"release": "%s" % obj.artist.id,
                        "track": "%s" % obj.uuid,
                        "length": duration,
                        "codever": "%s" % version,
                        "source": "%s" % "NRGFP",
                        "import_date": "%sZ" % id
                        }
                
                print nfp
                
                
                res = fp.ingest(nfp, split=False, do_commit=True)
    
                print 'getting code by id (check)'
    
                
                if fp.fp_code_for_track_id("%s" % obj.id):
                    print "ALL RIGHT!!! FP INSERTED!!"
                    status = 1
                    
                else:
                    status = 2
                    
                    
                    
                res = fp.best_match_for_query(code_string=code_pre)
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                print res.score
                print res.match()
                print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                    
                
                    
                    
                    
            except Exception, e:
                print e
                status = 2
                
        obj.echoprint_status = status
        obj.save()

        
    def save(self, *args, **kwargs):
        
        log = logging.getLogger('alibrary.mediamodels.save')
        log.info('Media id: %s - Save' % (self.pk))


        """
        Assign a default license
        """
        if not self.license:
            try:
                license = License.objects.filter(is_default=True)[0]
                self.license = license
            except:
                print 'no default license available'
        
    
        """
        check if master changed. if yes we need to reprocess the cached files
        """

        if self.uuid is not None:
            
            print 'UUID: %s' % self.uuid

            try:
                #orig = Media.objects.get(uuid=self.uuid)
                orig = Media.objects.filter(uuid=self.uuid)[0]
                if orig.master != self.master:
                    log.info('Media id: %s - Master changed from "%s" to "%s"' % (self.uuid, orig.master, self.master))
                    self.processed = 0
                    self.conversion_status = 0
                    self.echoprint_status = 0

            except Exception, e:
                print 'ERR'
                print e
                print 'ERR'
                pass
            
        
        try:
            cache_folder = self.folder
        except Exception, e:
            print e
            log.info('Media id: %s - cache folder does not exist' % (self.pk))
            cache_folder = None

            
        if self.master and self.processed != 1:
            log.info('Media id: %s - set master path to: %s' % (self.pk, self.master.path))
            iext = None
            try:
                iext = os.path.splitext(self.master.path)[1].lower()
                iext = iext[1:]
                audiofile = audiotools.open(self.master.path)
                
                base_format = iext
                base_bitrate = audiofile.bits_per_sample()
                base_samplerate = audiofile.sample_rate()
                base_filesize = os.path.getsize(self.master.path)
                base_duration = audiofile.seconds_length()
                
                self.processed = 1
            except Exception, e:
                print e
                base_bitrate = None
                base_samplerate = None
                base_filesize = None
                base_duration = None
                self.processed = 2
                
            self.base_format = iext
            self.base_bitrate = base_bitrate
            self.base_samplerate = base_samplerate
            self.base_filesize = base_filesize
            self.base_duration = base_duration
            
        
        
        if self.master:
            self.master_sha1 = self.generate_sha1()
        else:
            self.master_sha1 = None
                
                
        unique_slugify(self, self.name)
        super(Media, self).save(*args, **kwargs)

# register
# post_save.connect(library_post_save, sender=Media)   
        
        
arating.enable_voting_on(Media)
        
# media post save
def media_post_save(sender, **kwargs):
    
    log = logging.getLogger('alibrary.mediamodels.media_post_save')
    obj = kwargs['instance']

    # save the folder path
    if not obj.folder and obj.master:
        folder = "private/%s/" % (obj.uuid.replace('-', '/'))
        log.info('Adding folder: %s' % (folder))
        obj.folder = folder
        obj.save()

    
    log.info('Media id: %s - Processed state: %s' % (obj.pk, obj.processed))
    

    
    
    
    if obj.master and obj.echoprint_status == 0:
        log.info('Media id: %s - Echoprint' % (obj.pk))
        obj.update_echoprint()
    
    if obj.master and obj.conversion_status == 0 and obj.echoprint_status != 0:
        log.info('Media id: %s - Re-Process' % (obj.pk))
        obj.generate_media_versions()
        
        

# register
post_save.connect(media_post_save, sender=Media)    

class MediaExtraartists(models.Model):
    artist = models.ForeignKey('Artist', related_name='extraartist_artist')
    media = models.ForeignKey('Media', related_name='extraartist_media')
    # function = models.CharField(max_length=128, blank=True, null=True)
    profession = models.ForeignKey(Profession, verbose_name='Role/Profession', related_name='media_extraartist_profession', blank=True, null=True)   
    class Meta:
        app_label = 'alibrary'
    
    


"""
CMS-Plugins
"""
class MediaPlugin(CMSPlugin):
    
    media = models.ForeignKey(Media)
    
    headline = models.BooleanField(verbose_name=_('Show headline (Track/Artist)'), default=False)
    
    def __unicode__(self):
        return self.media.name

    # meta
    class Meta:
        app_label = 'alibrary'































    
def get_raw_image(filename, type):
    try:
        f = open(filename, 'rb')
        data = f.read()
        f.close()

        return audiotools.Image.new(data, u'', type)
    except IOError:
        raise audiotools.InvalidImage(_(u"Unable to open file"))