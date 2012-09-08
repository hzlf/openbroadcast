from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from cms.models import CMSPlugin
from django_extensions.db.fields import *

class BaseModel(models.Model):
    
    uuid = UUIDField()
    
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    
    class Meta:
        abstract = True


class Playout(BaseModel):

    title = models.CharField(max_length=256, null=False, blank=True)
    channel = models.ForeignKey('Channel', null=True, blank=True, on_delete=models.SET_NULL)
    
    STATUS_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    
    status = models.PositiveIntegerField(default=0, choices=STATUS_CHOICES)
    
    # meta
    class Meta:
        app_label = 'bcmon'
        verbose_name = _('Playout')
        verbose_name_plural = _('Playouts')
        ordering = ('title', )

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('bcmon-playout-detail', [self.pk])


class Channel(BaseModel):

    name = models.CharField(max_length=256, null=False, blank=True)
    slug = AutoSlugField(populate_from='name')
    
    stream_url = models.CharField(max_length=256, null=False, blank=True)
    title_format = models.CharField(max_length=256, null=False, blank=True)
    
    class Meta:
        app_label = 'bcmon'
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')
        ordering = ('name', )

    def __unicode__(self):
        return "%s" % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('bcbon-channel-detail', [self.pk])
