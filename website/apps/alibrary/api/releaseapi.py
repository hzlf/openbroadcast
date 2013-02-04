from django.conf import settings

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from easy_thumbnails.files import get_thumbnailer

from alibrary.models import Release

class ReleaseResource(ModelResource):
    
    media = fields.ToManyField('alibrary.api.MediaResource', 'media_release', null=True, full=True, max_depth=3)
    label = fields.ForeignKey('alibrary.api.LabelResource', 'label', null=True, full=True, max_depth=2)

    class Meta:
        queryset = Release.objects.order_by('-created').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'release'
        excludes = ['updated',]
        include_absolute_url = True
        authentication =  MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication())
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
                main_image = image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass
            
            bundle.data['artist'] = bundle.obj.get_artists();

        return bundle