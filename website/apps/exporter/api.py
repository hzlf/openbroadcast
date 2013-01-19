from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from exporter.models import Export, ExportItem

from alibrary.api import MediaResource


# file = request.FILES[u'files[]']



class ExportItemResource(ModelResource):
    
    import_session = fields.ForeignKey('exporter.api.ExportResource', 'import_session', null=True, full=False)
    
    media = fields.ForeignKey('alibrary.api.MediaResource', 'media', null=True, full=True)

    class Meta:
        queryset = ExportItem.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'exportitem'
        # excludes = ['type','results_musicbrainz']
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


            print "####################################"
            print request.FILES[u'files[]']


            imp = Export.objects.get(pk=import_id)
            bundle.data['import_session'] = imp
            bundle.data['file'] = request.FILES[u'files[]']
            
            
        except Exception, e:
            print e
            
        return super(ExportItemResource, self).obj_create(bundle, request, **kwargs)


class ExportResource(ModelResource):
    
    files = fields.ToManyField('exporter.api.ExportItemResource', 'files', full=True, null=True)

    class Meta:
        queryset = Export.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        #list_allowed_methods = ['get',]
        #detail_allowed_methods = ['get',]
        resource_name = 'export'
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
    

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)

        

    
    
    

    