from django.conf.urls.defaults import *
from django.db.models import Q

from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from easy_thumbnails.files import get_thumbnailer

from alibrary.models import Artist

THUMBNAIL_OPT = dict(size=(70, 70), crop=True, bw=False, quality=80)

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
            'id': ['exact', 'in'],
        }
        # cache = SimpleCache(timeout=120)
        

    def dehydrate(self, bundle):
        
        if(bundle.obj.main_image):
            bundle.data['main_image'] = None
            try:
                opt = THUMBNAIL_OPT
                main_image = image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass

        return bundle
        
    
    
    # additional methods
    def prepend_urls(self):
        
        return [
              url(r"^(?P<resource_name>%s)/autocomplete%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('autocomplete'), name="alibrary-artist_api-autocomplete"),
              # for compatibility, remove later on
              url(r"^(?P<resource_name>%s)/autocomplete-name%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('autocomplete'), name="alibrary-artist_api-autocomplete"),
        ]
        
    def autocomplete(self, request, **kwargs):
        
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)
        
        q = request.GET.get('q', None)
        result = []
        object_list = []
        objects = []
        object_count = 0
        
        qs = None
        
        if q and len(q) > 1:

            # qs = Artist.objects.filter(name__istartswith=q)
            qs = Artist.objects.filter(Q(name__istartswith=q)\
                | Q(namevariations__name__istartswith=q))
        

            object_list = qs.distinct()[0:20]
            object_count = qs.distinct().count()

            for result in object_list:
                bundle = self.build_bundle(obj=result, request=request)
                bundle = self.autocomplete_dehydrate(bundle, q)
                objects.append(bundle)
                
    
        data = {
            'meta': {
                     'query': q,
                     'total_count': object_count
                     },
            'objects': objects,
        }

            

        self.log_throttled_access(request)
        return self.create_response(request, data)
    
    

    def autocomplete_dehydrate(self, bundle, q):
        
        bundle.data['name'] = bundle.obj.name
        bundle.data['id'] = bundle.obj.pk
        bundle.data['ct'] = 'artist'
        bundle.data['get_absolute_url'] = bundle.obj.get_absolute_url()
        bundle.data['resource_uri'] = bundle.obj.get_api_url()
        bundle.data['main_image'] = None
        try:
            opt = THUMBNAIL_OPT
            main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
            bundle.data['main_image'] = main_image.url
        except:
            pass

        # namevariations
        bundle.data['namevariations'] = []
        for name in bundle.obj.namevariations.all():
            bundle.data['namevariations'].append(name.name)
        

        return bundle