# python
import datetime
import uuid
import shutil
import sys

# django
from django.db import models
from django.db.models.signals import post_save
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.files import File as DjangoFile
from django.core.urlresolvers import reverse


from django.contrib.contenttypes.generic import GenericRelation

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

from django_date_extensions.fields import ApproximateDateField

# modules
#from taggit.managers import TaggableManager
from django_countries import CountryField
from easy_thumbnails.files import get_thumbnailer

import tagging
import reversion 

from l10n.models import Country


# logging
import logging
logger = logging.getLogger(__name__)
    
import arating
    
################
from alibrary.models.basemodels import *
from alibrary.models.releasemodels import *
from alibrary.models.mediamodels import *
from alibrary.models.playlistmodels import *

from alibrary.util.signals import library_post_save
from alibrary.util.slug import unique_slugify

LOOKUP_PROVIDERS = (
    ('discogs', _('Discogs')),
    ('musicbrainz', _('Musicbrainz')),
)



class NameVariation(models.Model):

    name = models.CharField(max_length=200, db_index=True)
    artist = models.ForeignKey('Artist', related_name="namevariations", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Name variation')
        verbose_name_plural = _('Name variation')
        ordering = ('name', )

    def __unicode__(self):
        return self.name



class ArtistManager(models.Manager):

    def listed(self):
        return self.get_query_set().filter(listed=True, priority__gt=0)

class Artist(MigrationMixin):
    
    uuid = UUIDField(primary_key=False)
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)

    type = models.CharField(verbose_name="Artist type", max_length=120, blank=True, null=True)
    main_image = FilerImageField(null=True, blank=True, related_name="artist_main_image", rel='')
    real_name = models.CharField(max_length=200, blank=True, null=True)
    disambiguation = models.CharField(max_length=256, blank=True, null=True)
    
    #country = CountryField(blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)

    booking_contact = models.CharField(verbose_name=_('Booking'), max_length=256, blank=True, null=True)

    date_start = ApproximateDateField(verbose_name=_("Begin"), blank=True, null=True, help_text=_("date of formation / date of birth"))
    date_end = ApproximateDateField(verbose_name=_("End"), blank=True, null=True, help_text=_("date of breakup / date of death"))
    
    
    PRIORITY_CHOICES = (
        (0, _('- [hidden]')),
        (1, '*'),
        (2, '**'),
        (3, '***'),
        (4, '****'),
    )
    #priority = models.IntegerField(default=1, choices=PRIORITY_CHOICES, help_text=_('Priority for sorting'))

    # properties to create 'special' objects. (like 'Unknown')
    listed = models.BooleanField(verbose_name='Include in listings', default=True, help_text=_('Should this Artist be shown on the default Artist-list?'))
    disable_link = models.BooleanField(verbose_name='Disable Link', default=False, help_text=_('Disable Linking. Useful e.g. for "Varius Artists"'))
    disable_editing = models.BooleanField(verbose_name='Disable Editing', default=False, help_text=_('Disable Editing. Useful e.g. for "Unknown Artist"'))
    
    # 
    excerpt = models.TextField(blank=True, null=True)  
    biography = models.TextField(blank=True, null=True)    
    
    # relations
    members = models.ManyToManyField('self', through='ArtistMembership', symmetrical=False)
    #aliases = models.ManyToManyField("self", related_name='artist_aliases', blank=True, null=True)
    aliases = models.ManyToManyField("self", through='ArtistAlias', related_name='artist_aliases', blank=True, null=True, symmetrical=False)

    folder = models.ForeignKey(Folder, blank=True, null=True, related_name='artist_folder', on_delete=models.SET_NULL)
    
    # relations a.k.a. links
    relations = generic.GenericRelation(Relation)
    
    # tagging (d_tags = "display tags")
    d_tags = tagging.fields.TagField(max_length=1024, verbose_name="Tags", blank=True, null=True)
 
    
    professions = models.ManyToManyField(Profession, through='ArtistProfessions')
    
    # user relations
    owner = models.ForeignKey(User, blank=True, null=True, related_name="artists_owner", on_delete=models.SET_NULL)
    creator = models.ForeignKey(User, blank=True, null=True, related_name="artists_creator", on_delete=models.SET_NULL)
    publisher = models.ForeignKey(User, blank=True, null=True, related_name="artists_publisher", on_delete=models.SET_NULL)

    # identifiers
    ipi_code = models.CharField(verbose_name=_('IPI Code'), max_length=32, blank=True, null=True)
    isni_code = models.CharField(verbose_name=_('ISNI Code'), max_length=32, blank=True, null=True)


    
    # tagging
    #tags = TaggableManager(blank=True)

    enable_comments = models.BooleanField(_('Enable Comments'), default=True)
    
    # manager
    objects = ArtistManager()
    
    # auto-update
    created = models.DateField(auto_now_add=True, editable=False)
    updated = models.DateField(auto_now=True, editable=False)

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Artist')
        verbose_name_plural = _('Artists')
        ordering = ('name', )
    
    def __unicode__(self):
        
        return self.name
    
    @property
    def classname(self):
        return self.__class__.__name__
    
    def get_versions(self):
        try:
            return reversion.get_for_object(self)
        except:
            return None
        
    def get_last_revision(self):
        try:
            return reversion.get_unique_for_object(self)[0].revision
        except:
            return None
        
    def get_last_editor(self):
        latest_revision = self.get_last_revision()
        if latest_revision:
            return latest_revision.user
        else:
            return None

    @models.permalink
    def get_absolute_url(self):
        if self.disable_link:
            return None
        
        return ('alibrary-artist-detail', [self.slug])

    @models.permalink
    def get_edit_url(self):
        return ('alibrary-artist-edit', [self.pk])

    def get_admin_url(self):
        from lib.util.get_admin_url import change_url
        return change_url(self)
    
    def get_api_url(self):
        return reverse('api_dispatch_detail', kwargs={  
            'api_name': 'v1',  
            'resource_name': 'artist',  
            'pk': self.pk  
        }) + ''
    
    def get_membership(self):

        parents = []
        try:
            ms = ArtistMembership.objects.filter(child=self)
            for m in ms:
                parents.append(m.parent)
        except:
            pass
        
        return parents


    def get_alias_ids(self, exclude=[]):

        alias_ids = []
        parent_alias_ids = ArtistAlias.objects.filter(child__pk=self.pk).values_list('parent__pk', flat=True).distinct()
        child_alias_ids = ArtistAlias.objects.filter(parent__pk=self.pk).values_list('child__pk', flat=True).distinct()

        alias_ids.extend(parent_alias_ids)
        alias_ids.extend(child_alias_ids)

        for alias_id in alias_ids:
            if not alias_id == self.pk and not alias_id in exclude:
                exclude.append(alias_id)
                alias_ids.extend(Artist.objects.get(pk=alias_id).get_alias_ids(exclude=exclude))

        return alias_ids

    def get_aliases(self):

        aliases = Artist.objects.filter(pk__in=self.get_alias_ids([])).exclude(pk=self.pk).distinct()
        return aliases
    
    # release collection
    def get_releases(self):
        try:
            r = Release.objects.filter(Q(media_release__artist=self) | Q(album_artists=self)).distinct()
            return r
        except Exception, e:
            return []
        
    def get_media(self):
        try:
            m = Media.objects.filter(artist=self).distinct()
            return m
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
        

    def get_lookup_providers(self):
        
        providers = []
        for key, name in LOOKUP_PROVIDERS:
            relations = self.relations.filter(service=key)
            relation = None
            if relations.count() == 1:
                relation = relations[0]
                
            providers.append({'key': key, 'name': name, 'relation': relation})

        return providers


    def is_multiple(self):
        return self.multiple == True # TODO: actually check if combo-artist!


    def get_folder(self, name):
        folder, created = Folder.objects.get_or_create(name=name, parent=self.folder)
        return folder
        
        
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        
        # update d_tags
        t_tags = ''
        for tag in self.tags:
            t_tags += '%s, ' % tag    
        
        self.tags = t_tags;
        self.d_tags = t_tags;
        
        super(Artist, self).save(*args, **kwargs)
    
    


try:
    tagging.register(Artist)
except:
    pass

# register
arating.enable_voting_on(Artist)
post_save.connect(library_post_save, sender=Artist)   

from actstream import action
def action_handler(sender, instance, created, **kwargs):
    try:
        if instance.get_last_editor():
            action.send(instance.get_last_editor(), verb=_('updated'), target=instance)
    except Exception, e:
        print e

post_save.connect(action_handler, sender=Artist)   

class ArtistMembership(models.Model):
    
    parent = models.ForeignKey(Artist, related_name='artist_parent')
    child = models.ForeignKey(Artist, related_name='artist_child')
    profession = models.ForeignKey(Profession, related_name='artist_membership_profession', blank=True, null=True)

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Membersip')
        verbose_name_plural = _('Membersips')

class ArtistAlias(models.Model):

    parent = models.ForeignKey(Artist, related_name='alias_parent')
    child = models.ForeignKey(Artist, related_name='alias_child')

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Alias')
        verbose_name_plural = _('Aliases')
    

class ArtistProfessions(models.Model):
    artist = models.ForeignKey('Artist')
    profession = models.ForeignKey('Profession')

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Profession')
        verbose_name_plural = _('Professions')
    
    
    
        
        

""""""
class ArtistPlugin(CMSPlugin):
    
    artist = models.ForeignKey(Artist)
    def __unicode__(self):
        return self.artist.name

    # meta
    class Meta:
        app_label = 'alibrary'
