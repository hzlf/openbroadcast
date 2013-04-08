from django.conf.urls.defaults import *
from django.conf import settings

from django.db.models import Q

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache
from tastypie.utils import trailing_slash

from easy_thumbnails.files import get_thumbnailer

from alibrary.models import Release

THUMBNAIL_OPT = dict(size=(70, 70), crop=True, bw=False, quality=80)

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
            bundle.data['main_image'] = None
            try:
                opt = THUMBNAIL_OPT
                main_image = image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass
            
            bundle.data['artist'] = bundle.obj.get_artists();

        return bundle
    
    
    
    
    
    
    
    
    # additional methods
    def prepend_urls(self):
        
        return [
              url(r"^(?P<resource_name>%s)/autocomplete%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('autocomplete'), name="alibrary-release_api-autocomplete"),
              url(r"^(?P<resource_name>%s)/autocomplete-name%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('autocomplete_name'), name="alibrary-release_api-autocomplete_name"),
        ]



    def autocomplete(self, request, **kwargs):
        
        self.method_check(request, allowed=['get'])
        # self.is_authenticated(request)
        self.throttle_check(request)
        
        q = request.GET.get('q', None)
        result = []
        object_list = []
        qs = None
        if q and len(q) > 1:
            qs = Release.objects.filter(Q(name__istartswith=q)\
                | Q(media_release__name__icontains=q)\
                | Q(media_release__artist__name__icontains=q)\
                | Q(label__name__icontains=q))
        

        if qs:
           object_list = qs.distinct()[0:20]

        objects = []
        for result in object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.autocomplete_dehydrate(bundle, q)
            objects.append(bundle)

        if qs:
            meta = {
                    'query': q,
                    'total_count': qs.distinct().count()
                    }
    
            data = {
                'meta': meta,
                'objects': objects,
            }
        else:
            meta = {
                    'query': q,
                    'total_count': 0
                    }
    
            data = {
                'meta': meta,
                'objects': {},
            }
            

        self.log_throttled_access(request)
        return self.create_response(request, data)
    
    

    def autocomplete_dehydrate(self, bundle, q):
        bundle.data['name'] = bundle.obj.name
        bundle.data['get_absolute_url'] = bundle.obj.get_absolute_url()
        bundle.data['resource_uri'] = bundle.obj.get_api_url()
        bundle.data['main_image'] = None
        try:
            opt = THUMBNAIL_OPT
            main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
            bundle.data['main_image'] = main_image.url
        except:
            pass
        
        media_list = []
        for media in bundle.obj.media_release.filter(Q(name__icontains=q) | Q(artist__name__icontains=q)).distinct():
            media_list.append({'name': media.name, 'artist': media.artist.name})
        
        bundle.data['media'] = media_list
        return bundle
    
    
    




    def autocomplete_name(self, request, **kwargs):
        
        self.method_check(request, allowed=['get'])
        # self.is_authenticated(request)
        self.throttle_check(request)
        
        q = request.GET.get('q', None)
        result = []
        object_list = []
        qs = None
        if q and len(q) > 1:
            qs = Release.objects.filter(name__istartswith=q)
        
        if qs:
           object_list = qs.distinct()[0:20]

        objects = []
        for result in object_list:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.autocomplete_name_dehydrate(bundle, q)
            objects.append(bundle)

        if qs:
            meta = {
                    'query': q,
                    'total_count': qs.distinct().count()
                    }
    
            data = {
                'meta': meta,
                'objects': objects,
            }
        else:
            meta = {
                    'query': q,
                    'total_count': 0
                    }
    
            data = {
                'meta': meta,
                'objects': {},
            }
            

        self.log_throttled_access(request)
        return self.create_response(request, data)
    

    
    

    def autocomplete_name_dehydrate(self, bundle, q):
        bundle.data['name'] = bundle.obj.name
        bundle.data['id'] = bundle.obj.pk
        bundle.data['ct'] = 'release'
        bundle.data['releasedate'] = bundle.obj.releasedate
        bundle.data['artist'] = bundle.obj.get_artists()
        bundle.data['media_count'] = bundle.obj.media_release.count()
        bundle.data['get_absolute_url'] = bundle.obj.get_absolute_url()
        bundle.data['resource_uri'] = bundle.obj.get_api_url()
        bundle.data['main_image'] = None
        try:
            opt = THUMBNAIL_OPT
            main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
            bundle.data['main_image'] = main_image.url
        except:
            pass

        return bundle
    