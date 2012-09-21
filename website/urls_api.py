from django.conf.urls.defaults import *


from tastypie.api import Api
from bcmon.api import PlayoutResource, ChannelResource
from alibrary.api import MediaResource
from importer.api import ImportResource

api = Api(api_name='v1')
api.register(PlayoutResource())
api.register(ChannelResource())
api.register(MediaResource())
api.register(ImportResource())
    
urlpatterns = patterns('',
    (r'^', include(api.urls)),
)