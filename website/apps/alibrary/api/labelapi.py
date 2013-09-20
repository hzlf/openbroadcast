from django.conf import settings

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from easy_thumbnails.files import get_thumbnailer

from alibrary.models import Label

THUMBNAIL_OPT = dict(size=(70, 70), crop=True, bw=False, quality=80)

class LabelResource(ModelResource):

    class Meta:
        queryset = Label.objects.all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'label'
        excludes = ['updated',]
        #include_absolute_url = True
        authentication =  MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication())
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'id': ['exact', 'in'],
        }
        cache = SimpleCache(timeout=120)


    def dehydrate(self, bundle):

        if(bundle.obj.main_image):
            bundle.data['main_image'] = None
            try:
                opt = THUMBNAIL_OPT
                main_image = image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass



        # try to get all media



        return bundle
        