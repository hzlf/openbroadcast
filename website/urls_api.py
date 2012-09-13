from django.conf.urls.defaults import *


from tastypie.api import Api
from bcmon.api import *
from alibrary.api import *

api = Api(api_name='v1')
api.register(PlayoutResource())
api.register(ChannelResource())
api.register(MediaResource())
    
urlpatterns = patterns('',
    (r'^', include(api.urls)),
)