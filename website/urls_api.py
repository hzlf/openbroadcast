from django.conf.urls.defaults import *


from tastypie.api import Api
from bcmon.api import PlayoutResource, ChannelResource
from alibrary.api import MediaResource, ReleaseResource, ArtistResource
from importer.api import ImportResource, ImportFileResource
from exporter.api import ExportResource, ExportItemResource
from abcast.api import StationResource, ChannelResource

from fluent_comments.api import CommentResource

api = Api(api_name='v1')

# bcmon
api.register(PlayoutResource())
api.register(ChannelResource())

# library
api.register(MediaResource())
api.register(ReleaseResource())
api.register(ArtistResource())

# importer
api.register(ImportResource())
api.register(ImportFileResource())

# exporter
api.register(ExportResource())
api.register(ExportItemResource())

# abcast
api.register(StationResource())
api.register(ChannelResource())

# comment
api.register(CommentResource())

    
urlpatterns = patterns('',
    (r'^', include(api.urls)),
)