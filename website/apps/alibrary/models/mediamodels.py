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

from settings import *

# django-extensions (http://packages.python.org/django-extensions/)
from django_extensions.db.fields import UUIDField, AutoSlugField

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

# echoprint
from echoprint.API import fp

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

class Media(MigrationMixin):
    
    # core fields
    uuid = UUIDField(primary_key=False)
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)
    
    
    isrc = models.CharField(max_length=12, null=True, blank=True, help_text="International Standard Recording Code")
    master_path = models.CharField(max_length=2048, null=True, blank=True, help_text="Master Path", editable=False)
    
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
    folder = models.ForeignKey(Folder, blank=True, null=True, related_name='media_folder', editable=False, on_delete=models.SET_NULL)
    
    # extra-artists
    # TODO: Fix this - guess should relate to Artist instead of Profession
    extra_artists = models.ManyToManyField(Profession, through='MediaExtraartists', blank=True, null=True)
    
    license = models.ForeignKey(License, blank=True, null=True, related_name='media_license')
    
    # link to 'real' file
    master = FilerAudioField(blank=True, null=True, related_name='media_master')
    
    # tagging
    #tags = TaggableManager(blank=True)
    
    # manager
    objects = models.Manager()
    
    # auto-update
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Track')
        verbose_name_plural = _('Tracks')
        ordering = ('tracknumber', )
    
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        # TODO: Make right
        return '/tracks/' + self.slug + '/'
    
    def get_playlink(self):
        return '/api/tracks/%s/#0#replace' % self.uuid
    
    
    def get_download_permissions(self):
        pass
    
    
    
    def get_products(self):
        return self.mediaproduct.all()
    
    
    
    def get_download_url(self, format, version):
        
        return '%sdownload/%s/%s/' % (self.get_absolute_url(), format, version)
    
    
    def get_master_path(self):
        
        return self.master.path
    
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
        # TODO: improve...
        
        filename = str(version) + '.' + str(format)
        try:
            file = File.objects.filter(original_filename=filename, folder=self.folder)[0]
            return file
        except Exception, e:
            print e
            return None
    
    def get_waveform_image(self):
        # TODO: improve...
        try:
            file = Image.objects.filter(original_filename='waveform.png', folder=self.folder).order_by('-uploaded_at')[0]
            return file
        except Exception, e:
            return None
        
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
            return audiotools.open(self.master_path)
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
        src_path = self.master_path
    
        tmp_directory = tempfile.mkdtemp()
        tmp_path = tmp_directory + '/' + dst_file
        
        log.info('Media id: %s - dst_file: %s' % (self.pk, dst_file))
        log.info('Media id: %s - src_path: %s' % (self.pk, src_path))
        log.info('Media id: %s - tmp_path: %s' % (self.pk, tmp_path))
        
        
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        print 'Media id: %s - dst_file: %s' % (self.pk, dst_file)
        print 'Media id: %s - src_path: %s' % (self.pk, src_path)
        print 'Media id: %s - tmp_path: %s' % (self.pk, tmp_path)
        
        print
        print
        print
        print '##########################################################'
        time.sleep(0.5)
        print 'self',
        print self
        
        print 'self.master',
        print self.master
        
        print 'self.master_path',
        print self.master_path
        time.sleep(0.5)
        print '##########################################################'
        print
        print
        print
    
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
        try:
            print '*******************************************************'
            print 'create %s-version from %s' % (format, self.master.path)
            print 'Tmp file at:',
            print tmp_path
            print 'Source file at:',
            print src_path
            print 'Destination file at:',
            print dst_file
            print '-'
            
            print 'sleeping 0.5 secs...'
            
            time.sleep(0.5)
            

            
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
                    print 'conversion to mp3'
                    audiotools.open(src_path).convert(tmp_path, audiotools.MP3Audio, compression=compression, progress=self.convert_progress)

            
            if format == 'flac':
                # TODO: make compression variable / configuration dependant
                print 'conversion to flac'
                audiotools.open(src_path).convert(tmp_path, audiotools.FlacAudio, progress=self.convert_progress)
            
            if format == 'wav':
                print 'conversion to wav'
                
                print 'pre audiotools'
                try:
                    print 'audiotools.open',
                    print 'src_path:',
                    print src_path
                    print 'tmp_path:',
                    print tmp_path
                    
                    audiotools.open(src_path).convert(tmp_path, audiotools.WaveAudio, progress=self.convert_progress)
                except Exception, e:
                    print 'error converting to WAV: ', 
                    print e
                print 'post audiotools'
            
                # waveform
                wav_path = str(tmp_path)
                img_w = str(tmp_path) + '_w' + '.png' 
                img_s = str(tmp_path) + '_s' +'.png' 
        
                args = (wav_path, img_w, img_s, 1800, 301, 2048, self.progress_callback)
                
                print '----------------------------------'
                print 'WAVEGRAPHER!!!'
                print '----------------------------------'
                try:
                    print 'trying to create waveform image:',
                    print img_w
                    create_wave_images(*args)
                    print 'create_wave_images - done'
                except Exception, e:
                    print "Error running wav2png: ", e
                    
                try: 
                    # file.Image.objects.get(original_filename='waveform.png', folder=self.folder)
                    # os.remove(file.path)
                    # file.delete()
                    # delete all images in cache folder
                    for img in self.folder.files.instance_of(Image):
                        os.remove(img.path)
                        img.delete()
                                  
                except Exception, e:
                    print 'unable to delete:',
                    print e
                    
                try:
                    print 'trying to attach:',
                    print img_w
                    wav_file = DjangoFile(open(img_w),name='waveform.png')            
                    file, created = Image.objects.get_or_create(
                                                    original_filename='waveform.png',
                                                    file=wav_file,
                                                    folder=self.folder,
                                                    is_public=True)
                except Exception, e:
                    print 'error creating waveform image :( - ', 
                    print e

            
            
            converted = True
            
            print '*******************************************************'
            
        except Exception, e:
            print 'conversion issue:',
            print e
            
            
        """
        finaly create a django file object and attach it to the medias cache folder
        """
        try:
            
            print "** tmp_path"
            print tmp_path
            
            tmp_file = DjangoFile(open(tmp_path),name=dst_file)            
            file, created = File.objects.get_or_create(
                                            original_filename=tmp_file.name,
                                            file=tmp_file,
                                            folder=self.folder,
                                            is_public=False)
            status = 1
        
        except Exception, e:
            print "error adding file to the cache :( "
            status = 2
            print e
        
        
        """
        cleanup temp-files
        """
        try:
            #shutil.rmtree(tmp_directory)
            pass
        except Exception, e:
            print e
        
        # self.save()
        
        return status
        
        

    @task
    def grappher(self, width, height):
        """
        
        """
        pass
    
    



 
       
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
        # pass
        print 'conversion: %s' % (x * 100 / y)
        
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
        
        print '-'
        print "!!!! generate_media_versions:",
        print "SELF.PROCESSED:",
        print self.processed
        print '-'
        
        if self.processed == 0:
            self.generate_media_versions_task.delay(self)
        else:
            print 'processed not 0'
            pass
    
    """
    format conversion & co. takes the master and processes versions as configured
    """
    @task
    def generate_media_versions_task(obj):
        
        print '-'
        print '-'
        print "!!!! generate_media_versions_task:",
        print "OBJ.PROCESSED:",
        print obj.processed
        print '-'
        print '-'

        log = logging.getLogger('alibrary.mediamodels.generate_media_versions_task')
        
        log.info('Media id: %s - Generate Versions' % (obj.pk))
        log.debug('sleeping some secs... waiting for db transaction to be complete')
        
        print 
        print '**********************************************************'
    
        print 'sleeping some secs.. waiting for db transaction to be complete'
    
        time.sleep(4)
    
        try:
            old_files = File.objects.filter(folder=obj.folder).all()
            for old_file in old_files:
                print 'cache-folder: %s' % obj.folder 
                print 'delete: %s | %s' % (old_file, old_file.path)
                os.remove(old_file.path)
                log.info('Delete from cache: %s' % (old_file.path))
                old_file.delete()
                
        except Exception, e:
            log.warning('Delete from cache: %s' % (e))
            print e
    
        """
        Skip errors # TODO: find a way to retry/reprocess
        ignored a.t.m.
        """
        #if not obj.processed == 2: 
        #    pass
        
        print '**********************************************************'
        
        print
        print 'sending jobs to encoder-queue'
        print
        
        # call without '.delay' for straight developing 

        formats_media = FORMATS_MEDIA
        for source, versions in formats_media.iteritems():
            for version in versions:
                log.info('Media id: %s - Sending to Encoder: %s/%s' % (obj.pk, source, version))
                obj.convert(source, version)
        
        
        # check if everything went fine (= if cache files available)
        
        print "Theoretically done... Let's check the result."
        
        try:
            c = obj.get_cache_file('mp3', 'base')
            print c
            
            print 'PROCESSING DONE'
            
            obj.processed = 1;
            obj.save();
            
            
        except Exception, e:
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print e
            obj.processed = 2;
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
        
        from settings import ECHOPRINT_CODEGEN_BIN
        
        
        ecb = ECHOPRINT_CODEGEN_BIN
        ecb = 'echoprint-codegen'
        
        path = self.get_master_path()
        
        #path = self.master_path
        
        print 'path: %s' % path
        
        p = subprocess.Popen([
            ecb, path,
        ], stdout=subprocess.PIPE)
        stdout = p.communicate()        
        d = json.loads(stdout[0])
        
        print d
        
        try:
            code = d[0]['code']
            version = d[0]['metadata']['version']
            duration = d[0]['metadata']['duration']
        except Exception, e:
            print e
            code = None
            version = None
            duration = None
            
            
        if code:
            print 'delete fingerprint on server id: %s' % self.id 
            fp.delete("%s" % self.id)
            
            print 'post new fingerprint:'
            
            
            id = self.updated.isoformat('T')[:-7]
            
            
            code = fp.decode_code_string(code)
            
            nfp = {
                    "track_id": "%s" % self.id,
                    "fp": code,
                    #"artist": "%s" % self.artist.id,
                    #"release": "%s" % self.artist.id,
                    "track": "%s" % self.uuid,
                    "length": duration,
                    "codever": "%s" % version,
                    "source": "%s" % "NRGFP",
                    "import_date": "%sZ" % id
                    }
            
            
            res = fp.ingest(nfp, split=False)

            print 'getting code by id (check)'
            
            if fp.fp_code_for_track_id("%s" % self.id):
                print "ALL RIGHT!!! FP INSERTED!!"
                self.echoprint_status = 1
                
            else:
                self.echoprint_status = 2
                
            self.save()
                


            #print code
        
        
        
        
    def save(self, *args, **kwargs):
        
        log = logging.getLogger('alibrary.mediamodels.save')
        log.info('Media id: %s - Save' % (self.pk))

        
        """
        check if master changed. if yes we need to reprocess the cached files
        """

        if self.uuid is not None:
            
            try:
                orig = Media.objects.get(uuid=self.uuid)
                if orig.master != self.master:
                    log.info('Media id: %s - Master changed from "%s" to "%s"' % (self.uuid, orig.master, self.master))
                    self.processed = 0
            except Exception, e:
                print e
                pass
            
        
        try:
            cache_folder = self.folder
        except Exception, e:
            print e
            log.info('Media id: %s - cache folder does not exist' % (self.pk))
            cache_folder = None

            
        if self.master:
            log.info('Media id: %s - set master path to: %s' % (self.pk, self.master.path))
            self.master_path = self.master.path
                
        unique_slugify(self, self.name)
        super(Media, self).save(*args, **kwargs)

# register
post_save.connect(library_post_save, sender=Media)   
        
# media post save
def media_post_save(sender, **kwargs):
    log = logging.getLogger('alibrary.mediamodels.media_post_save')
    obj = kwargs['instance']
    
    print "media_post_save - PROCESSED?:",
    print obj.processed
    
    if obj.processed == 0:
        log.info('Media id: %s - Re-Process' % (obj.pk))
        pass
        obj.generate_media_versions()
        
    if obj.processed == 1 and obj.echoprint_status == 0:
        print "do echoprint geeration"
        obj.update_echoprint()
        

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