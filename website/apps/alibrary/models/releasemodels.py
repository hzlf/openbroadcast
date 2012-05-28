# python
import datetime
from datetime import *
import time
import uuid
import shutil
import sys
import tempfile
import glob
import sets
from zipfile import ZipFile

# django
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.files import File as DjangoFile
from django.core.urlresolvers import reverse

from django.contrib.contenttypes.generic import GenericRelation

from django.http import HttpResponse # needed for absolute url

from settings import *

# django-extensions (http://packages.python.org/django-extensions/)
from django_extensions.db.fields import UUIDField

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

import tagging


# settings
from settings import TEMP_DIR

# logging
import logging
logger = logging.getLogger(__name__)
    
    
################
from alibrary.models.basemodels import *
from alibrary.models.artistmodels import *
from alibrary.models.mediamodels import *
from alibrary.models.playlistmodels import *

FORCE_CATALOGNUMBER = False

# shop
#from ashop.models import Hardwarerelease, Downloadrelease





class ReleaseManager(models.Manager):

    def active(self):
        now = datetime.now()
        return self.get_query_set().filter(
                Q(publish_date__isnull=True) |
                Q(publish_date__lte=now)
                )




class Release(MigrationMixin):
    
    #__metaclass__=classmaker()
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=False)
    
    
    release_country = models.CharField(max_length=200, blank=True, null=True)
    
    #uuid = models.CharField(max_length=36, unique=False, default=str(uuid.uuid4()), editable=True)
    uuid = UUIDField()
    
    main_image = FilerImageField(null=True, blank=True, related_name="release_main_image", rel='')
    cover_image = FilerImageField(null=True, blank=True, related_name="release_cover_image", rel='', help_text=_('Cover close-up. Used e.g. for embedding in digital files.'))
    
    
    if FORCE_CATALOGNUMBER:
        catalognumber = models.CharField(max_length=50)
    else:
        catalognumber = models.CharField(max_length=50, blank=True, null=True)
        
    releasedate = models.DateField(blank=True, null=True)
    pressings = models.PositiveIntegerField(max_length=12, default=0)
    
    publish_date = models.DateTimeField(default=datetime.now, blank=True, null=True, help_text=_('If set this Release will not be published on the site before the given date.'))

    main_format = models.ForeignKey(Mediaformat, null=True, blank=True, on_delete=models.SET_NULL)
    
    # 
    excerpt = models.TextField(blank=True, null=True)
    
    # cms field
    placeholder_1 = PlaceholderField('placeholder_1')
    
    RELEASETYPE_CHOICES = (
        ('ep', _('EP')),
        ('album', _('Album')),
        ('compilation', _('Compilation')),
        ('other', _('Other')),
    )
    releasetype = models.CharField(max_length=12, default='other', choices=RELEASETYPE_CHOICES)
    
    
    # relations
    label = models.ForeignKey(Label, blank=True, null=True, related_name='release_label', on_delete=models.SET_NULL)
    folder = models.ForeignKey(Folder, blank=True, null=True, related_name='release_folder', on_delete=models.SET_NULL)
    
    # product
    # product = models.OneToOneField(Baseproduct, blank=True, null=True, related_name='release_product', on_delete=models.SET_NULL)
    
    # extra-artists
    extra_artists = models.ManyToManyField('Artist', through='ReleaseExtraartists', blank=True, null=True)
    def get_extra_artists(self):
        ea = []
        for artist in self.extra_artists.all():
            ea.push(artist.name)
        return ea
    
    # relations a.k.a. links
    relations = generic.GenericRelation(Relation)
    
    # tagging
    #tags = TaggableManager(blank=True)
    
    tags = tagging.fields.TagField()
    
    #ntags = tagging.managers.ModelTaggedItemManager()

    enable_comments = models.BooleanField(_('Enable Comments'), default=True)
    
    # manager
    objects = ReleaseManager()
    
    # auto-update
    created = models.DateField(auto_now_add=True, editable=False)
    updated = models.DateField(auto_now=True, editable=False)

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Release')
        verbose_name_plural = _('Releases')
        ordering = ('-releasedate', )
    
    
    def __unicode__(self):
        return self.name
    
    def is_active(self):
        
        now = date.today()
        try:
            if not self.releasedate:
                return True
            
            if self.releasedate <= now:
                return True
        
        except:
            pass

        return False

    @models.permalink
    def get_absolute_url(self):
        # TODO: Make right
        # return '/releases/' + self.slug + '/'
        return ('ReleaseDetailView', [self.slug])
    
    def get_media(self):
        return Media.objects.filter(release=self).select_related()
    
    def get_products(self):
        return self.releaseproduct.all()
    
    def get_artists(self):

        artists = []
        
        try:
            re = ReleaseExtraartists.objects.filter(release=self, profession__name="Album Artist")
            for ea in re:
                # print ea.artist
                artists.append(ea.artist)
                
            if len(artists) > 0:
                return artists
        
        except Exception, e:
            print e
            pass

                
        medias = self.get_media()
        for media in medias:
            artists.append(media.artist)
        
        artists = list(set(artists))
        
        #print "GET ARTISTS"
        #print artists
        
        return artists

    def get_extra_artists(self):

        artists = []
        
        roles = ReleaseExtraartists.objects.filter(release=self.pk)
        
        for role in roles:
            try:
                role.artist.profession = role.profession.name
                artists.append(role.artist)
            except:
                pass
 
        return artists
    
    def get_downloads(self):
        
        downloads = File.objects.filter(folder=self.get_folder('downloads')).all()

        if len(downloads) < 1:
            return None
        
        return downloads
    
    
    
    def get_download_url(self, format, version):
        
        return '%sdownload/%s/%s/' % (self.get_absolute_url(), format, version)
    
    
    
    
    
    
    
    def get_cache_file_path(self, format, version):
        
        tmp_directory = TEMP_DIR
        file_name = '%s_%s_%s.%s' % (format, version, str(self.uuid), 'zip')
        tmp_path = '%s/%s' % (tmp_directory, file_name)
        
        return tmp_path
    
    
    def clear_cache_file(self):
        """
        Clears cached release (the one for buy-downloads)
        """
        
        tmp_directory = TEMP_DIR
        pattern = '*%s.zip' % (str(self.uuid))
        versions = glob.glob('%s/%s' % (tmp_directory, pattern))
        
        print versions

        try:
            for version in versions:
                os.remove(version)
  
        except Exception, e:
            print e
            pass

    def get_cache_file(self, format, version):

        cache_file_path = self.get_cache_file_path(format, version)
        
        if os.path.isfile(cache_file_path):
            logger.info('serving from cache: %s' % (cache_file_path))
            return cache_file_path
            
        else:
            return self.build_cache_file(format, version)

    def build_cache_file(self, format, version):
        
        cache_file_path = self.get_cache_file_path(format, version)
        
        logger.info('building cache for: %s' % (cache_file_path))

        try:
            os.remove(cache_file_path)
  
        except Exception, e:
            pass


        archive_file = ZipFile(cache_file_path, "w")
        
        """
        adding corresponding media files
        """
        for media in self.get_media():

            media_cache_file = media.inject_metadata(format, version)

            # filename for the file archive
            file_name = '%02d - %s - %s' % (media.tracknumber, media.artist.name, media.name)
            file_name = '%s.%s' % (file_name.encode('ascii', 'ignore'), format)

            # archive_file.write('/Users/ohrstrom/code/alibrary/website/check.txt', 'test.txt')
            archive_file.write(media_cache_file.path, file_name)
                
            
        """
        adding assets if any
        """

        asset_files = File.objects.filter(folder=self.get_folder('assets')).all()
        for asset_file in asset_files:
            
            if asset_file.name:
                file_name = asset_file.name
            else:
                file_name = asset_file.original_filename
            
            archive_file.write(asset_file.path, file_name)

            
        return cache_file_path

    def get_extraimages(self):
        
        if self.folder:
            folder = self.get_folder('pictures')
            images = folder.files.instance_of(Image)

        if len(images) > 0:
            return images
        else:
            return None
                
                

    def get_folder(self, name):
        
        if name == 'cache':
            parent_folder, created = Folder.objects.get_or_create(name='cache')
            folder, created = Folder.objects.get_or_create(name=str(self.uuid), parent=parent_folder)
        else:
            folder, created = Folder.objects.get_or_create(name=name, parent=self.folder)
            
        return folder
    
    
    def save(self, *args, **kwargs):
        
        """
        Depending if folders organized by catalognumber
        """
        if FORCE_CATALOGNUMBER:
            folder_name = self.catalognumber
        else:
            folder_name = self.name
        
        """
        if not self.product:
            product, created = Baseproduct.objects.get_or_create(name=self.catalognumber, slug=self.slug)
            self.product = product
        """
        
        if not self.folder:
            try:
                folder, created = Folder.objects.get_or_create(name=folder_name, parent=self.label.folder)
                self.folder = folder
                
                # create subdirs
                Folder.objects.get_or_create(name='pictures', parent=self.folder)
                Folder.objects.get_or_create(name='tracks', parent=self.folder)
                Folder.objects.get_or_create(name='assets', parent=self.folder)
                Folder.objects.get_or_create(name='downloads', parent=self.folder)
            except Exception, e:
                print e
            
            
        """
        clear release cache
        """
        self.clear_cache_file()
            
            
        super(Release, self).save(*args, **kwargs)

try:
    tagging.register(Release)
except:
    pass


class ReleaseExtraartists(models.Model):
    artist = models.ForeignKey('Artist', related_name='release_extraartist_artist')
    release = models.ForeignKey('Release', related_name='release_extraartist_release')
    profession = models.ForeignKey(Profession, verbose_name='Role/Profession', related_name='release_extraartist_profession', blank=True, null=True)   
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')


class ReleaseRelations(models.Model):
    relation = models.ForeignKey('Relation', related_name='release_relation_relation')
    release = models.ForeignKey('Release', related_name='release_relation_release')
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        
        
        
        
        
        
        
        
        
        
        

        
class ReleasePlugin(CMSPlugin):
    
    release = models.ForeignKey(Release)
    def __unicode__(self):
        return self.release.name

    # meta
    class Meta:
        app_label = 'alibrary'
        
        
