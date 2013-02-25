from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from tastypie.cache import SimpleCache

from abcast.models import Jingle, JingleSet

from easy_thumbnails.files import get_thumbnailer

class JingleResource(ModelResource):
    
    set = fields.ForeignKey('abcast.api.JingleSetResource', 'set', null=True, full=True, max_depth=2)

    class Meta:
        queryset = Jingle.objects.order_by('name').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/jingle'
        excludes = ['updated',]
        #include_absolute_url = True
        authentication =  Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        #cache = SimpleCache(timeout=120)


class JingleSetResource(ModelResource):
    
    jingles = fields.ToManyField('abcast.api.JingleResource', 'jingle_set', null=True, full=True, max_depth=2)


    class Meta:
        queryset = JingleSet.objects.order_by('name').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/jingleset'
        excludes = ['updated',]
        #include_absolute_url = True
        authentication =  Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        #cache = SimpleCache(timeout=120)
        
    """"""
    def dehydrate(self, bundle):
        
        bundle.data['main_image'] = None
        
        if(bundle.obj.main_image):
            opt = dict(size=(70, 70), crop=True, bw=False, quality=80)
            try:
                main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass

        return bundle
    



    

    