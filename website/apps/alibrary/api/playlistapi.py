from django.conf import settings

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from easy_thumbnails.files import get_thumbnailer

from alibrary.models import Playlist, PlaylistMedia, Media


class PlaylistMediaResource(ModelResource):

    media = fields.ToOneField('alibrary.api.MediaResource', 'media', null=True, full=True)
    class Meta:
        queryset = PlaylistMedia.objects.all()
        excludes = ['id',]

class PlaylistResource(ModelResource):

    media = fields.ToManyField('alibrary.api.PlaylistMediaResource',
            attribute=lambda bundle: bundle.obj.media.through.objects.filter(
                playlist=bundle.obj).order_by('position') or bundle.obj.media, null=True, full=True, max_depth=3)


    class Meta:
        queryset = Playlist.objects.order_by('-created').all()
        list_allowed_methods = ['get','post']
        detail_allowed_methods = ['get','delete', 'put', 'post', 'patch']
        resource_name = 'playlist'
        #excludes = ['updated',]
        include_absolute_url = True
        
        always_return_data = True
        
        authentication =  MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication())
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'status': ['exact', 'range',],
        }
        #cache = SimpleCache(timeout=120)
        
    def obj_create(self, bundle, request=None, **kwargs):
        return super(PlaylistResource, self).obj_create(bundle, request, user=request.user)
    
    def dehydrate(self, bundle):
        bundle.data['edit_url'] = bundle.obj.get_edit_url();
        return bundle
    
    def hydrate_m2m(self, bundle):
        print "hydrate m2m"
        
        """
        curl --dump-header - -H "Content-Type: application/json" -X PUT --data '{"media": [{"media": "/api/v1/track/16587/"}]}' "http://localhost:8080/de/api/v1/playlist/58/?username=root&api_key=APIKEY"
        """
        
        for item in bundle.data['media']:
            #item[u'media'] = self.get_resource_uri(bundle.obj)
            print item 
        
    
    def save_m2m(self, bundle):
        
        print 
        print
        print 'save m2m:'
        print bundle
        
        return bundle


    