from django.conf.urls.defaults import *


from tastypie.api import Api
from bcmon.api import PlayoutResource, ChannelResource
from alibrary.api import MediaResource, ReleaseResource
from importer.api import ImportResource, ImportFileResource

api = Api(api_name='v1')
api.register(PlayoutResource())
api.register(ChannelResource())
api.register(MediaResource())
api.register(ImportResource())
api.register(ImportFileResource())
    
urlpatterns = patterns('',
    (r'^', include(api.urls)),
)