from django.conf import settings

from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from tastypie.cache import SimpleCache

from abcast.models import Emission

from easy_thumbnails.files import get_thumbnailer

class EmissionResource(ModelResource):
    
    # set = fields.ForeignKey('abcast.api.JingleSetResource', 'set', null=True, full=True, max_depth=2)
    
    playlist = fields.ForeignKey('alibrary.api.PlaylistResource', 'playlist', null=True, full=True, max_depth=3)

    class Meta:
        queryset = Emission.objects.order_by('name').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/emission'
        excludes = ['updated',]
        #include_absolute_url = True
        authentication =  Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        #cache = SimpleCache(timeout=120)


    def dehydrate(self, bundle):
        
        obj = bundle.obj
        # bundle.data['stream'] = stream

        return bundle
    