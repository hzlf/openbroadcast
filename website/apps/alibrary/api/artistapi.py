from django.conf import settings

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from easy_thumbnails.files import get_thumbnailer

from alibrary.models import Artist

class ArtistResource(ModelResource):

    class Meta:
        queryset = Artist.objects.all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'artist'
        excludes = ['updated',]
        include_absolute_url = True
        authentication =  MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication())
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        cache = SimpleCache(timeout=120)