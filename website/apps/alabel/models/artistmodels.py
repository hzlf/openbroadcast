# python
import datetime
import uuid
import shutil
import sys

# django
from django.db import models
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
from taggit.managers import TaggableManager
from django_countries import CountryField
from easy_thumbnails.files import get_thumbnailer



# logging
import logging
logger = logging.getLogger(__name__)
    
    
################
from alabel.models.basemodels import *
from alabel.models.releasemodels import *
from alabel.models.mediamodels import *
from alabel.models.playlistmodels import *



class ArtistManager(models.Manager):

    def listed(self):
        return self.get_query_set().filter(listed=True, priority__gt=0)

class Artist(models.Model):
    
    name = models.CharField(max_length=200)
    
    slug = models.SlugField(max_length=100, unique=False)
    #uuid = models.CharField(max_length=36, unique=False, default=str(uuid.uuid4()), editable=False)
    #slug = AutoSlugField(populate_from='name')
    uuid = UUIDField()
    
    main_image = FilerImageField(null=True, blank=True, related_name="artist_main_image", rel='')
    
    real_name = models.CharField(max_length=200, blank=True, null=True)
    
    
    PRIORITY_CHOICES = (
        (0, _('- [hidden]')),
        (1, '*'),
        (2, '**'),
        (3, '***'),
        (4, '****'),
    )
    priority = models.IntegerField(default=1, choices=PRIORITY_CHOICES, help_text=_('Priority for sorting'))

    
    # cms field
    placeholder_1 = PlaceholderField('placeholder_1')

    multiple = models.NullBooleanField(null=True, blank=True)
    
    listed = models.BooleanField(verbose_name='Include in listings', default=True, help_text=_('Should this Artist be shown on the default Artist-list?'))
    disable_link = models.BooleanField(verbose_name='Disable Link', default=False, help_text=_('Disable Linking. Useful e.g. for "Varius Artists"'))
    
    # 
    excerpt = models.TextField(blank=True, null=True)  
    biography = models.TextField(blank=True, null=True)    
    
    # relations
    # parent = TreeManyToManyField('self', null=True, blank=True, related_name='artist_parent')
    members = models.ManyToManyField('self', through='ArtistMembership', symmetrical=False)
    aliases = models.ManyToManyField("self", related_name='artist_aliases', blank=True, null=True)
    
    folder = models.ForeignKey(Folder, blank=True, null=True, related_name='artist_folder', on_delete=models.SET_NULL)
    
    relations = generic.GenericRelation(Relation)
    
    professions = models.ManyToManyField(Profession, through='ArtistProfessions')
    
    # tagging
    tags = TaggableManager(blank=True)

    enable_comments = models.BooleanField(_('Enable Comments'), default=True)
    
    # manager
    objects = ArtistManager()
    
    # auto-update
    created = models.DateField(auto_now_add=True, editable=False)
    updated = models.DateField(auto_now=True, editable=False)

    # meta
    class Meta:
        app_label = 'alabel'
        verbose_name = _('Artist')
        verbose_name_plural = _('Artists')
        ordering = ('-priority', 'name', )
    
    def __unicode__(self):
        
        if self.is_multiple():
            return 'COMBO: ' + self.name
        
        return self.name

    @models.permalink
    def get_absolute_url(self):
        if self.disable_link:
            return None
        
        return ('ArtistDetailView', None, {'slug': self.slug})
    
    def get_membership(self):

        parents = []
        try:
            ms = ArtistMembership.objects.filter(child=self)
            for m in ms:
                parents.append(m.parent)
        except:
            pass
        
        return parents
    
    # release collection
    def get_releases(self):
        try:
            r = Release.objects.filter(media_release__artist=self).distinct()
            return r
        except Exception, e:
            return []
        
    
    def get_downloads(self):
        
        downloads = File.objects.filter(folder=self.get_folder('downloads')).all()

        if len(downloads) < 1:
            return None
        
        return downloads
    
    def get_images(self):
        images = []
        
        if self.main_image:
            images.append(self.main_image)
            
        try:
            extra_images = Image.objects.filter(folder=self.get_folder('pictures')).all()
            
            for ea in extra_images:
                if ea != self.main_image:
                    images.append(ea)
            
        except Exception, e:
            pass
            
        
        return images
        



    def is_multiple(self):
        return self.multiple == True # TODO: actually check if combo-artist!


    def get_folder(self, name):
        folder, created = Folder.objects.get_or_create(name=name, parent=self.folder)
        return folder
        
        
    def save(self, *args, **kwargs):
        
        folder_name = self.name
        parent, created = Folder.objects.get_or_create(name='Artists')
        
        if not self.folder:
            folder, created = Folder.objects.get_or_create(name=folder_name, parent=parent)
            self.folder = folder
            
            # create subdirs
            Folder.objects.get_or_create(name='pictures', parent=self.folder)
            Folder.objects.get_or_create(name='press', parent=self.folder)
            Folder.objects.get_or_create(name='downloads', parent=self.folder)

            
        super(Artist, self).save(*args, **kwargs)
    
    

class ArtistMembership(models.Model):
    
    parent = models.ForeignKey(Artist, related_name='artist_parent')
    child = models.ForeignKey(Artist, related_name='artist_child')
    profession = models.ForeignKey(Profession, related_name='artist_membership_profession', blank=True, null=True)

    # meta
    class Meta:
        app_label = 'alabel'
        verbose_name = _('Membersip')
        verbose_name_plural = _('Membersips')
    

class ArtistProfessions(models.Model):
    artist = models.ForeignKey('Artist')
    profession = models.ForeignKey('Profession')

    # meta
    class Meta:
        app_label = 'alabel'
        verbose_name = _('Profession')
        verbose_name_plural = _('Professions')
    
    
    
        
        

""""""
class ArtistPlugin(CMSPlugin):
    
    artist = models.ForeignKey(Artist)
    def __unicode__(self):
        return self.artist.name

    # meta
    class Meta:
        app_label = 'alabel'
