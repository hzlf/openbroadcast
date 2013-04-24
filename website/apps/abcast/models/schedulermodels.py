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

from alibrary.models import Artist, Playlist

from abcast.models import BaseModel, Station, Channel






class Broadcast(BaseModel):
    
    # core fields
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)

    STATUS_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    status = models.PositiveIntegerField(max_length=2, default=0, choices=STATUS_CHOICES)

    TYPE_CHOICES = (
        ('studio', _('Studio')),
        ('playlist', _('Playlist')),
        ('couchcast', _('Couchcast')),
    )
    type = models.CharField(verbose_name=_('Type'), max_length=12, default='jingle', choices=TYPE_CHOICES)
    
    description = models.TextField(verbose_name="Extra Description", blank=True, null=True)
    duration = models.PositiveIntegerField(verbose_name="Duration (in ms)", max_length=12, blank=True, null=True, editable=True)
    
    # relations
    user = models.ForeignKey(User, blank=True, null=True, related_name="scheduler_broadcasts", on_delete=models.SET_NULL)
    playlist = models.ForeignKey(Playlist, blank=True, null=True, related_name="scheduler_broadcasts", on_delete=models.SET_NULL)

    # manager
    objects = models.Manager()

    class Meta:
        app_label = 'abcast'
        verbose_name = _('Broadcast')
        verbose_name_plural = _('Broadcasts')
        ordering = ('created', )
    
    
    def __unicode__(self):
        return self.name






class Emission(BaseModel):
    
    # core fields
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', editable=True, blank=True, overwrite=True)

    STATUS_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    status = models.PositiveIntegerField(max_length=2, default=0, choices=STATUS_CHOICES)

    TYPE_CHOICES = (
        ('studio', _('Studio')),
        ('playlist', _('Playlist')),
        ('couchcast', _('Couchcast')),
    )
    type = models.CharField(verbose_name=_('Type'), max_length=12, default='playlist', choices=TYPE_CHOICES)
    
    
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    
    duration = models.PositiveIntegerField(verbose_name="Duration (in ms)", max_length=12, blank=True, null=True, editable=True)
    
    
    # relations
    user = models.ForeignKey(User, blank=True, null=True, related_name="scheduler_emissions", on_delete=models.SET_NULL)
    channel = models.ForeignKey(Channel, blank=True, null=True, related_name="scheduler_emissions", on_delete=models.SET_NULL)
    
    playlist = models.ForeignKey(Playlist, blank=True, null=True, related_name="scheduler_emissions", on_delete=models.SET_NULL)

    # manager
    objects = models.Manager()

    class Meta:
        app_label = 'abcast'
        verbose_name = _('Emission')
        verbose_name_plural = _('Emissions')
        ordering = ('created', )
    
    
    def __unicode__(self):
        return self.name
    
    