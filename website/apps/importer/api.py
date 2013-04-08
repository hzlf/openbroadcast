from django.contrib.auth.models import User
from django.db.models import Count
import json
from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from importer.models import Import, ImportFile

from alibrary.api import MediaResource


# file = request.FILES[u'files[]']



class ImportFileResource(ModelResource):
    
    import_session = fields.ForeignKey('importer.api.ImportResource', 'import_session', null=True, full=False)
    
    media = fields.ForeignKey('alibrary.api.MediaResource', 'media', null=True, full=True)

    class Meta:
        queryset = ImportFile.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'importfile'
        # excludes = ['type','results_musicbrainz']
        excludes = ['type',]
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'import_session': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        

    def dehydrate(self, bundle):
        bundle.data['status'] = bundle.obj.get_status_display().lower();
        # offload json parsing to the backend
        # TODO: remove in js, enable here
        """
        bundle.data['import_tag'] = json.loads(bundle.data['import_tag'])
        bundle.data['results_acoustid'] = json.loads(bundle.data['results_acoustid'])
        bundle.data['results_musicbrainz'] = json.loads(bundle.data['results_musicbrainz'])
        bundle.data['results_discogs'] = json.loads(bundle.data['results_discogs'])
        bundle.data['results_tag'] = json.loads(bundle.data['results_tag'])
        """
        return bundle
        
        
    def obj_update(self, bundle, request, **kwargs):
        #import time
        #time.sleep(3)
        return super(ImportFileResource, self).obj_update(bundle, request, **kwargs)
        

    def obj_create(self, bundle, request, **kwargs):
        """
        Little switch to play with jquery fileupload
        """
        try:
            import_id = request.GET['import_session']


            print "####################################"
            print request.FILES[u'files[]']


            imp = Import.objects.get(pk=import_id)
            bundle.data['import_session'] = imp
            bundle.data['file'] = request.FILES[u'files[]']
            
            
        except Exception, e:
            print e
            
        return super(ImportFileResource, self).obj_create(bundle, request, **kwargs)


class ImportResource(ModelResource):
    
    files = fields.ToManyField('importer.api.ImportFileResource', 'files', full=True, null=True)

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

        

    
    
    

    