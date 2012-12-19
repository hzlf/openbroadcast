from django.utils import simplejson
from django.core import serializers

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from alibrary.models import APILookup
from alibrary.models import *



@dajaxice_register
def api_lookup(request, *args, **kwargs):
    
    
    item_type = kwargs.get('item_type', None)
    item_id = kwargs.get('item_id', None)
    provider = kwargs.get('provider', None)
    
    print provider  
    
    try:
        if item_type == 'release':
            r = Release.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(r)        
            al, created = APILookup.objects.get_or_create(content_type=ctype, object_id=r.id, provider=provider)
            
            print 'created:',
            print created
        
        
        #al = APILookup.objects.all()[0]
        
        data = al.get_from_api()
         
        
        # js = serializers.get_serializer("json")()
        #data = js.serialize(data, ensure_ascii=False)
        data = simplejson.dumps(data)
        
        
        return data
    
    except:
        return None
