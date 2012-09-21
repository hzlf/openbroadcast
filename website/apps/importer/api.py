from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from importer.models import Import, ImportFile








class ImportFileResource(ModelResource):
    
    channel = fields.ForeignKey('importer.api.ImportResource', 'import_session', null=True, full=False)

    class Meta:
        queryset = ImportFile.objects.all()
        #list_allowed_methods = ['get', 'post']
        #detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'importfile'
        excludes = ['type',]
        authentication = Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }


class ImportResource(ModelResource):
    
    files = fields.ToManyField('importer.api.ImportFileResource', 'files', full=True)

    class Meta:
        queryset = Import.objects.all()
        #list_allowed_methods = ['get', 'post']
        #detail_allowed_methods = ['get', 'post', 'put', 'delete']
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'import'
        excludes = ['updated',]
        include_absolute_url = True
        authentication = Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }

        

    
    
    

    