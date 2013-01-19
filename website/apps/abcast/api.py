from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from tastypie.cache import SimpleCache

from abcast.models import Station, Channel

from easy_thumbnails.files import get_thumbnailer

class StationResource(ModelResource):
    
    # label = fields.ForeignKey('alibrary.api.LabelResource', 'label', null=True, full=True, max_depth=2)

    class Meta:
        queryset = Station.objects.order_by('name').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/station'
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
        
        if(bundle.obj.main_image):
            opt = dict(size=(70, 70), crop=True, bw=False, quality=80)
            try:
                main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass

        return bundle

class ChannelResource(ModelResource):
    
    station = fields.ForeignKey('abcast.api.StationResource', 'station', null=True, full=True, max_depth=2)

    class Meta:
        queryset = Channel.objects.order_by('name').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/channel'
        excludes = ['updated',]
        #include_absolute_url = True
        authentication =  Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        #cache = SimpleCache(timeout=120)
        

    """
    def dehydrate(self, bundle):
        
        if(bundle.obj.main_image):
            opt = dict(size=(70, 70), crop=True, bw=False, quality=80)
            try:
                main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass

        return bundle
   """
"""
class MediaResource(ModelResource):
     
    release = fields.ForeignKey(ReleaseResource, 'release', null=True, full=True, max_depth=2)
    artist = fields.ForeignKey(ArtistResource, 'artist', null=True, full=True, max_depth=2)
    
    message = fields.CharField(attribute='message', null=True)
"""



    

    