from django.conf.urls.defaults import *

# app imports
from alibrary.models import Playlist
from alibrary.views import *
urlpatterns = patterns('',

    url(r'^$', PlaylistListView.as_view(), name='alibrary-playlist-list'),
    url(r'^create/$', PlaylistCreateView.as_view(), name='alibrary-playlist-create'),
    url(r'^(?P<slug>[-\w]+)/$', PlaylistDetailView.as_view(), name='alibrary-playlist-detail'),
    url(r'^(?P<pk>\d+)/edit/$', PlaylistEditView.as_view(), name='alibrary-playlist-edit'),
    
    # API-like urls [responding JSON]
    url(r'^(?P<pk>\d+)/collect/$', 'alibrary.views.playlist_collect', name='alibrary-playlist-collect'),

)