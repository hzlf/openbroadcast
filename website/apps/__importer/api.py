from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from importer.models import Import, ImportFile




# file = request.FILES[u'files[]']



class ImportFileResource(ModelResource):
    
    import_session = fields.ForeignKey('importer.api.ImportResource', 'import_session', null=True, full=False)

    class Meta:
        queryset = ImportFile.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'importfile'
        excludes = ['type',]
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'import_session': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        

    def obj_create(self, bundle, request, **kwargs):
        """
        Little switch to play with jquery fileupload
        """
        try:
            import_id = request.GET['import_session'] 
            imp = Import.objects.get(pk=int(import_id))
            
            bundle.data['import_session'] = imp
            
            
            bundle.data['file'] = request.FILES[u'files[]']
            
            
        except Exception, e:
            print e
            
        return super(ImportFileResource, self).obj_create(bundle, request, **kwargs)


class ImportResource(ModelResource):
    
    files = fields.ToManyField('importer.api.ImportFileResource', 'files', full=True)

    class Meta:
        queryset = Import.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        #list_allowed_methods = ['get',]
        #detail_allowed_methods = ['get',]
        resource_name = 'import'
        excludes = ['updated',]
        include_absolute_url = True
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        
    def save_related(self, obj):
        return True

        

    
    
    

    