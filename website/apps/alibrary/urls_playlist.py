from django.conf.urls.defaults import *

# app imports
from alibrary.views import *
urlpatterns = patterns('',

    url(r'^$', PlaylistListView.as_view(), name='alibrary-playlist-list'),
    
    url(r'^type/(?P<type>[-\w]+)/user/(?P<user>[-\w]+)/', PlaylistListView.as_view(), name='alibrary-playlist-type-list'),
    url(r'^type/(?P<type>[-\w]+)/', PlaylistListView.as_view(), name='alibrary-playlist-type-list'),
    url(r'^user/(?P<user>[-\w]+)/', PlaylistListView.as_view(), name='alibrary-playlist-user-list'),
    
    url(r'^create/$', PlaylistCreateView.as_view(), name='alibrary-playlist-create'),
    url(r'^(?P<slug>[-\w]+)/$', PlaylistDetailView.as_view(), name='alibrary-playlist-detail'),
    url(r'^(?P<pk>\d+)/edit/$', PlaylistEditView.as_view(), name='alibrary-playlist-edit'),
    url(r'^(?P<pk>\d+)/convert/(?P<type>[-\w]+)/$', 'alibrary.views.playlist_convert', name='alibrary-playlist-convert'),
    
    # API-like urls [responding JSON] -> moved to api
    #url(r'^(?P<pk>\d+)/reorder/$', 'alibrary.views.playlist_reorder', name='alibrary-playlist-reorder'),
    #url(r'^(?P<pk>\d+)/collect/$', 'alibrary.views.playlist_collect', name='alibrary-playlist-collect'),
    #url(r'^(?P<pk>\d+)/collect/$', 'alibrary.views.playlist_collect', name='alibrary-playlist-collect-old'),

)