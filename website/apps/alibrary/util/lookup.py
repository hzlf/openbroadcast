from django.contrib.contenttypes.models import ContentType

from alibrary.models.basemodels import *
from alibrary.models.artistmodels import *
from alibrary.models.mediamodels import *
from alibrary.models.releasemodels import *
from alibrary.models.playlistmodels import *


import logging
log = logging.getLogger(__name__)


def object_by_mb_id(mb_id, type):
    
    log = logging.getLogger('alibrary.util.lookup.media_by_mb_id')
    log.debug('Looking for media with mb_id: %s' % mb_id)
    
    rel_type = ContentType.objects.get(app_label="alibrary", model=type)
    
    return Relation.objects.filter(content_type=rel_type, url__contains=mb_id)


def media_by_mb_id(mb_id):
    
    rels = object_by_mb_id(mb_id, 'media')
    rel_ids = []
    for rel in rels:
        rel_ids.append(rel.content_object.pk)

    return Media.objects.filter(pk__in=rel_ids)

def release_by_mb_id(mb_id):
    
    rels = object_by_mb_id(mb_id, 'release')
    rel_ids = []
    for rel in rels:
        rel_ids.append(rel.content_object.pk)

    return Release.objects.filter(pk__in=rel_ids)

def artist_by_mb_id(mb_id):
    return object_by_mb_id(mb_id, 'artist')

def label_by_mb_id(mb_id):
    return object_by_mb_id(mb_id, 'label')