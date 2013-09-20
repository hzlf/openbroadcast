# python
import datetime
import uuid
import shutil
import sys

# django
from django.db import models
from django import forms
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.files import File as DjangoFile
from django.core.urlresolvers import reverse

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.http import HttpResponse # needed for absolute url

from settings import *


# cms
# from cms.models import CMSPlugin, Page
from cms.models.fields import PlaceholderField
from cms.utils.placeholder import get_page_from_placeholder_if_exists

# filer
from filer.models.filemodels import *
from filer.models.foldermodels import *
from filer.models.audiomodels import *
from filer.models.imagemodels import *
from filer.fields.image import FilerImageField

# modules
#from taggit.managers import TaggableManager
from django_countries import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from easy_thumbnails.files import get_thumbnailer

from l10n.models import AdminArea, Country

import tagging
import reversion 

# model extensions
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField 

# django-extensions (http://packages.python.org/django-extensions/)
from django_extensions.db.fields import UUIDField, AutoSlugField



# logging
import logging
logger = logging.getLogger(__name__)

import arating

################
from alibrary.models import MigrationMixin
from alibrary.util.signals import library_post_save
from alibrary.util.slug import unique_slugify


from lib.fields import extra


LOOKUP_PROVIDERS = (
    ('discogs', _('Discogs')),
    #('musicbrainz', _('Musicbrainz')),
)

class LabelManager(models.Manager):

    def active(self):
        now = datetime.now()
        return self.get_query_set().exclude(listed=False)


class Label(MPTTModel, MigrationMixin):

    # core fields
    uuid = UUIDField(primary_key=False)
    name = models.CharField(max_length=400)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)
    
    
    labelcode = models.CharField(max_length=250, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    #country = CountryField(blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    
    email = models.EmailField(blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    fax = PhoneNumberField(blank=True, null=True)
    
    
    main_image = FilerImageField(null=True, blank=True, related_name="label_main_image", rel='')
    
    description = extra.MarkdownTextField(blank=True, null=True)
    
    first_placeholder = PlaceholderField('first_placeholder')
    
    # auto-update
    created = models.DateField(auto_now_add=True, editable=False)
    updated = models.DateField(auto_now=True, editable=False)
    
    # relations
    parent = TreeForeignKey('self', null=True, blank=True, related_name='label_children')
    folder = models.ForeignKey(Folder, blank=True, null=True, related_name='label_folder')
    
    # user relations
    owner = models.ForeignKey(User, blank=True, null=True, related_name="labels_owner", on_delete=models.SET_NULL)
    creator = models.ForeignKey(User, blank=True, null=True, related_name="labels_creator", on_delete=models.SET_NULL)
    publisher = models.ForeignKey(User, blank=True, null=True, related_name="labels_publisher", on_delete=models.SET_NULL)
    
    # properties to create 'special' objects. (like 'Unknown')
    listed = models.BooleanField(verbose_name='Include in listings', default=True, help_text=_('Should this Label be shown on the default Label-list?'))
    disable_link = models.BooleanField(verbose_name='Disable Link', default=False, help_text=_('Disable Linking. Useful e.g. for "Unknown Label"'))
    disable_editing = models.BooleanField(verbose_name='Disable Editing', default=False, help_text=_('Disable Editing. Useful e.g. for "Unknown Label"'))
    
    TYPE_CHOICES = (
        ('unknown', _('Unknown')),
        ('major', _('Major Label')),
        ('indy', _('Independent Label')),
        ('net', _('Netlabel')),
        ('event', _('Event Label')),
    )
    
    type = models.CharField(verbose_name="Label type", max_length=12, default='unknown', choices=TYPE_CHOICES)


    # relations a.k.a. links
    relations = generic.GenericRelation('Relation')
    
    # tagging (d_tags = "display tags")
    d_tags = tagging.fields.TagField(max_length=1024,verbose_name="Tags", blank=True, null=True)
 
    
    # manager
    objects = LabelManager()

    # meta
    class Meta:
        app_label = 'alibrary'
        verbose_name = _('Label')
        verbose_name_plural = _('Labels')
        ordering = ('name', )

        permissions = (
            ('merge_label', 'Merge Labels'),
        )

    class MPTTMeta:
        order_insertion_by = ['name']
    
    def __unicode__(self):
        return self.name

    
    def get_folder(self, name):
        folder, created = Folder.objects.get_or_create(name=name, parent=self.folder)
        return folder




    @models.permalink
    def get_absolute_url(self):
        if self.disable_link:
            return None
        
        return ('alibrary-label-detail', [self.slug])

    @models.permalink
    def get_edit_url(self):
        return ('alibrary-label-edit', [self.pk])

    def get_admin_url(self):
        from lib.util.get_admin_url import change_url
        return change_url(self)


    def get_api_url(self):
        return reverse('api_dispatch_detail', kwargs={
            'api_name': 'v1',
            'resource_name': 'label',
            'pk': self.pk
        }) + ''



    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        
        # update d_tags
        t_tags = ''
        for tag in self.tags:
            t_tags += '%s, ' % tag    
        
        self.tags = t_tags;
        self.d_tags = t_tags;
        
        super(Label, self).save(*args, **kwargs)
    
        
try:
    tagging.register(Label)
except:
    pass

# register
post_save.connect(library_post_save, sender=Label)   
arating.enable_voting_on(Label)
   