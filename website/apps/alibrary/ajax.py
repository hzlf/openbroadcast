from django.core import serializers

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from alibrary.models import APILookup
from alibrary.models import Release

import json

# logging
import logging
logger = logging.getLogger(__name__)


@dajaxice_register
def api_lookup(request, *args, **kwargs):
    
    
    log = logging.getLogger('alibrary.ajax.api_lookup')
    
    
    item_type = kwargs.get('item_type', None)
    item_id = kwargs.get('item_id', None)
    provider = kwargs.get('provider', None)
    
    log.debug('type: %s - id: %s - provider: %s' % (item_type, item_id, provider))

    try:
        if item_type == 'release':
            r = Release.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(r)        
            al, created = APILookup.objects.get_or_create(content_type=ctype, object_id=r.id, provider=provider)
            if created:
                log.debug('APILookup created: %s' % (al.pk))

        
        data = al.get_from_api()
         
        
        # js = serializers.get_serializer("json")()
        #data = js.serialize(data, ensure_ascii=False)
        data = json.dumps(data)
        
        
        return data
    
    except Exception, e:
        log.warning('%s' % e)
        return None
