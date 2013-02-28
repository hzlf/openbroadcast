#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import datetime
import re

from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from cms.models import CMSPlugin
from django_extensions.db.fields import *
from django_extensions.db.fields.json import JSONField

from django.core.urlresolvers import reverse

# filer
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField

# 
from lib.fields import extra

from alibrary.models import Artist

from abcast.models import BaseModel, Station

def clean_filename(filename):
    import unicodedata
    import string
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    cleaned = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleaned if c in valid_chars)

def masterpath_by_uuid(instance, filename):
    filename, extension = os.path.splitext(filename)
    folder = "private/%s/" % (instance.uuid.replace('-', '/'))
    filename = u'master'
    return os.path.join(folder, "%s%s" % (clean_filename(filename).lower(), extension.lower()))




class JingleSet(BaseModel):
    
    # core fields
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)

    description = models.TextField(verbose_name="Extra Description", blank=True, null=True)

    main_image = FilerImageField(null=True, blank=True, related_name="jingleset_main_image", rel='')
    station = models.ForeignKey(Station, blank=True, null=True, related_name="jingleset_station", on_delete=models.SET_NULL)

    # manager
    objects = models.Manager()

    class Meta:
        app_label = 'abcast'
        verbose_name = _('Jingle-Set')
        verbose_name_plural = _('Jingle-Sets')
        ordering = ('created', )
    
    
    def __unicode__(self):
        return self.name




class Jingle(BaseModel):
    
    # core fields
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)

    PROCESSED_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    processed = models.PositiveIntegerField(max_length=2, default=0, choices=PROCESSED_CHOICES)
   
    CONVERSION_STATUS_CHOICES = (
        (0, _('Init')),
        (1, _('Completed')),
        (2, _('Error')),
    )
    conversion_status = models.PositiveIntegerField(max_length=2, default=0, choices=CONVERSION_STATUS_CHOICES)
    lock = models.PositiveIntegerField(max_length=1, default=0, editable=False)

    
    TYPE_CHOICES = (
        ('jingle', _('Jingle')),
        ('placeholder', _('Placeholder')),
    )
    type = models.CharField(verbose_name=_('Type'), max_length=12, default='jingle', choices=TYPE_CHOICES)
    description = models.TextField(verbose_name="Extra Description", blank=True, null=True)
    duration = models.PositiveIntegerField(verbose_name="Duration (in ms)", max_length=12, blank=True, null=True, editable=True)
    
    # relations
    user = models.ForeignKey(User, blank=True, null=True, related_name="jingle_user", on_delete=models.SET_NULL)
    artist = models.ForeignKey(Artist, blank=True, null=True, related_name='jingle_artist')
    set = models.ForeignKey(JingleSet, blank=True, null=True, related_name="jingle_set", on_delete=models.SET_NULL)

    # File related (new)
    master = models.FileField(max_length=1024, upload_to=masterpath_by_uuid, blank=True, null=True)
    master_sha1 = models.CharField(max_length=64, db_index=True, blank=True, null=True)
    
    folder = models.CharField(max_length=1024, null=True, blank=True, editable=False)
    
    # File Data
    """
    base_format = models.CharField(verbose_name=_('Format'), max_length=12, blank=True, null=True)
    base_filesize = models.PositiveIntegerField(verbose_name=_('Filesize'), blank=True, null=True)
    base_duration = models.FloatField(verbose_name=_('Duration'), blank=True, null=True)
    base_samplerate = models.PositiveIntegerField(verbose_name=_('Samplerate'), blank=True, null=True)
    base_bitrate = models.PositiveIntegerField(verbose_name=_('Bitrate'), blank=True, null=True)
    """
    # manager
    objects = models.Manager()

    class Meta:
        app_label = 'abcast'
        verbose_name = _('Jingle')
        verbose_name_plural = _('Jingles')
        ordering = ('created', )
    
    
    def __unicode__(self):
        return self.name
    
    