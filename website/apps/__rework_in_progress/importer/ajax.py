from django.utils import simplejson
from django.core import serializers

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from importer.models import *

@dajaxice_register
def get_import(request, *args, **kwargs):
    
    import_id = kwargs.get('item_type', None)
    
    data = []
    
    import_files = ImportFile.objects.all()
    
    for import_file in import_files:
        
        data.append({'id': import_file.pk, 'status': import_file.status})
    
    
    
    #data = [1,2,3,4,6,7,8,9]

    data = simplejson.dumps(data)
    
    
    return data
