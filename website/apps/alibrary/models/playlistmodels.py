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

from django.contrib.contenttypes.models import ContentType

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

import tagging
#import reversion 

# logging
import logging
logger = logging.getLogger(__name__)
    
from lib.fields import extra

################
from alibrary.models.basemodels import *
from alibrary.models.artistmodels import *
from alibrary.models.releasemodels import *
from alibrary.models.mediamodels import *


TARGET_DURATION_CHOICES = (
    (900, '15'),
    (1800, '30'),
    (2700, '45'),
    (3600, '60'),
    (4500, '75'),
    (5400, '90'),
    (6300, '105'),
    (7200, '120'),
)

def filename_by_uuid(instance, filename):
    filename, extension = os.path.splitext(filename)
    path = "playlists/"
    filename = instance.uuid.replace('-', '/') + extension
    return os.path.join(path, filename)



class Playlist(models.Model):
    
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)
    uuid = UUIDField()
    
    STATUS_CHOICES = (
        (0, _('Init')),
        (1, _('Ready')),
        (2, _('In progress')),
        (3, _('Scheduled')),
        (3, _('Descheduled')),
        (99, _('Error')),
        (11, _('Other')),
    )
    status = models.PositiveIntegerField(default=0, choices=STATUS_CHOICES)
    
    TYPE_CHOICES = (
        ('basket', _('Basket')),
        ('playlist', _('Playlist')),
        ('broadcast', _('Broadcast')),
        ('other', _('Other')),
    )
    type = models.CharField(max_length=12, default='other', null=True, choices=TYPE_CHOICES)
    
    #main_image = FilerImageField(null=True, blank=True, related_name="playlist_main_image", rel='')
    main_image = models.ImageField(verbose_name=_('Image'), upload_to=filename_by_uuid, null=True, blank=True)
    
    # relations
    user = models.ForeignKey(User, null=True, blank=True, default = None)
    media = models.ManyToManyField('Media', through='PlaylistMedia', blank=True, null=True)
    
    items = models.ManyToManyField('PlaylistItem', through='PlaylistItemPlaylist', blank=True, null=True)


    # tagging (d_tags = "display tags")
    d_tags = tagging.fields.TagField(verbose_name="Tags", blank=True, null=True)
    
    # commenting
    enable_comments = models.BooleanField(_('Enable Comments'), default=True)
    
    # updated/calculated on save
    duration = models.IntegerField(max_length=12, null=True, default=0)
    

    target_duration = models.PositiveIntegerField(default=0, null=True, choices=TARGET_DURATION_CHOICES)
    
    dayparts = models.ManyToManyField(Daypart, null=True, blank=True, related_name='daypart_plalists')
    
    
    description = extra.MarkdownTextField(blank=True, null=True)
    
    # manager
    objects = models.Manager()
    
    # auto-update
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Playlist')
        verbose_name_plural = _('Playlists')
        ordering = ('name', )
        
        permissions = (
            ('view_playlist', 'View Playlist'),
            ('edit_playlist', 'Edit Playlist'),
            ('admin_playlist', 'Edit Playlist (extended)'),
        )
    
    
    def __unicode__(self):
        return self.name
        
        
    @models.permalink
    def get_absolute_url(self):
        return ('alibrary-playlist-detail', [self.slug])

    @models.permalink
    def get_edit_url(self):
        return ('alibrary-playlist-edit', [self.pk])
    
    def get_api_url(self):
        return reverse('api_dispatch_detail', kwargs={  
            'api_name': 'v1',  
            'resource_name': 'playlist',  
            'pk': self.pk  
        }) + ''
        


    def add_items_by_ids(self, ids, ct):
        
        from alibrary.models.mediamodels import Media
        
        log = logging.getLogger('alibrary.playlistmodels.add_items_by_ids')
        log.debug('Media ids: %s' % (ids))
        log.debug('Content Type: %s' % (ct))
        
        """
        ct = ContentType.objects.get(model=ct)
        print ct
        """

        for id in ids:
            id = int(id)
            
            if ct == 'media':
                m = Media.objects.get(pk=id)
                
            i = PlaylistItem(content_object=m)
            i.save()    
                
            pi = PlaylistItemPlaylist(item=i, playlist=self, position=self.items.count())
            pi.save()

            print pi
            
            self.save()
        
        
        """
        for id in ids:
            id = int(id)
            
            m = Media.objects.get(pk=id)
            pm = PlaylistMedia(media=m, playlist=self, position=self.media.count())
            pm.save()

            print id
            print pm
            
            self.save()
        """

    """
    old method - for non-generic playlists
    """
    def add_media_by_ids(self, ids):
        
        from alibrary.models.mediamodels import Media
        
        log = logging.getLogger('alibrary.playlistmodels.add_media_by_id')
        log.debug('Media ids: %s' % (ids))
        
        for id in ids:
            id = int(id)
            
            m = Media.objects.get(pk=id)
            pm = PlaylistMedia(media=m, playlist=self, position=self.media.count())
            pm.save()

            print id
            print pm
            
            self.save()
        
        
    def save(self, *args, **kwargs):
        
        duration = 0
        try:
            for media in self.media.all():
                media.get_duration()
                if media.duration:
                    duration += media.duration
        except Exception, e:
            print e
            pass
        
        self.duration = duration
        
        # update d_tags
        t_tags = ''
        for tag in self.tags:
            t_tags += '%s, ' % tag    
        
        self.tags = t_tags;
        self.d_tags = t_tags;
        
        # self.user = request.user  
        super(Playlist, self).save(*args, **kwargs)
    

    
try:
    pass
    tagging.register(Playlist)
except:
    pass
    
arating.enable_voting_on(Playlist)


def playlist_post_save(sender, **kwargs):
    obj = kwargs['instance']
    pass
    
post_save.connect(playlist_post_save, sender=Playlist)
    

class PlaylistMedia(models.Model):
    #playlist = models.ForeignKey('Playlist', related_name='playlist_playlist')
    #media = models.ForeignKey('Media', related_name='playlist_media')
    
    uuid = UUIDField()
    
    playlist = models.ForeignKey('Playlist')
    media = models.ForeignKey('Media')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    position = models.PositiveIntegerField(max_length=12, default=0)
    # 
    cue_in = models.PositiveIntegerField(max_length=12, default=0)
    cue_out = models.PositiveIntegerField(max_length=12, default=0)
    fade_in = models.PositiveIntegerField(max_length=12, default=0)
    fade_out = models.PositiveIntegerField(max_length=12, default=0)
    class Meta:
        app_label = 'alibrary'
    


class PlaylistItemPlaylist(models.Model):
    playlist = models.ForeignKey('Playlist')
    item = models.ForeignKey('PlaylistItem')

    uuid = UUIDField()
    
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    position = models.PositiveIntegerField(max_length=12, default=0)
    # 
    cue_in = models.PositiveIntegerField(max_length=12, default=0)
    cue_out = models.PositiveIntegerField(max_length=12, default=0)
    fade_in = models.PositiveIntegerField(max_length=12, default=0)
    fade_out = models.PositiveIntegerField(max_length=12, default=0)
    class Meta:
        app_label = 'alibrary'
        
        
 
class PlaylistItem(models.Model):
    
    uuid = UUIDField()

    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Playlist Item')
        verbose_name_plural = _('Playlist Items')
        #ordering = ('-created', )
        
    ct_limit = models.Q(app_label = 'alibrary', model = 'media') | models.Q(app_label = 'alibrary', model = 'release')
    
    content_type = models.ForeignKey(ContentType, limit_choices_to = ct_limit)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return '%s' % (self.pk)
    
    def save(self, *args, **kwargs):
        super(PlaylistItem, self).save(*args, **kwargs)         
  
