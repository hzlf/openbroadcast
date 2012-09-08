from django.conf.urls.defaults import *


from tastypie.api import Api
from bcmon.api import *

api = Api(api_name='v1')
api.register(PlayoutResource())
api.register(ChannelResource())
    
urlpatterns = patterns('',
    (r'^', include(api.urls)),
)