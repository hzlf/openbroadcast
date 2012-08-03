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

# logging
import logging
logger = logging.getLogger(__name__)
    
    
################
from alibrary.models.basemodels import *
from alibrary.models.artistmodels import *
from alibrary.models.releasemodels import *
from alibrary.models.mediamodels import *




class Playlist(models.Model):
    
    name = models.CharField(max_length=200)
    
    slug = models.SlugField(max_length=100, unique=False)
    #uuid = models.CharField(max_length=36, unique=False, default=str(uuid.uuid4()), editable=False)
    uuid = UUIDField()
    
    PLAYLISTTYPE_CHOICES = (
        ('compilation', _('Compilation')),
        ('wishlist', _('Wishlist')),
        ('other', _('Other')),
    )
    playlisttype = models.CharField(max_length=12, default='other', choices=PLAYLISTTYPE_CHOICES)
    
    
    # relations
    user = models.ForeignKey(User, null=True, blank=True, default = None)
    media = models.ManyToManyField('Media', through='PlaylistMedia', blank=True, null=True)

    # tagging
    #tags = TaggableManager(blank=True)
    
    # manager
    objects = models.Manager()
    
    # auto-update
    created = models.DateField(auto_now_add=True, editable=False)
    updated = models.DateField(auto_now=True, editable=False)

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Playlist')
        verbose_name_plural = _('Playlists')
        ordering = ('name', )
    
    
    def __unicode__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # self.user = request.user  
        super(Playlist, self).save(*args, **kwargs)
    

class PlaylistMedia(models.Model):
    playlist = models.ForeignKey('Playlist', related_name='playlist_playlist')
    media = models.ForeignKey('Media', related_name='playlist_media')
    created = models.DateField(auto_now_add=True, editable=False)
    position = models.PositiveIntegerField(max_length=12, default=0)
    class Meta:
        app_label = 'alibrary'