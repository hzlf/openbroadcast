from django.conf.urls.defaults import *
from django.views.generic import ListView

from django.views.generic.simple import direct_to_template

# app imports
from alabel.models import Artist, Release, Media, Label
from alabel.views import *

# rest
from djangorestframework.views import ListOrCreateModelView, InstanceModelView, ListModelView, InstanceModelViewRO
from alabel.resources import *

urlpatterns = patterns('',
                       
    (r'^aaaartists/$', ListView.as_view(
        #model=Artist,
        queryset=Artist.objects.order_by("name"),
        #context_object_name="artist_list",
    )),
                       
    url('^ajax/', include('alabel.ajax.urls')),
    
    url(r'^crossdomain.xml$', direct_to_template, {'template': 'lib/crossdomain.xml', 'mimetype': 'application/xml'}),
    url(r'^crossdomain.xml/$', direct_to_template, {'template': 'lib/crossdomain.xml', 'mimetype': 'application/xml'}),
                       
    
    # artists
    #(r'^artists/', include('alabel.urls_artist')),
    #(r'^artists/$', ArtistListView.as_view()),              
    #url(r'^artists/(?P<slug>[-\w]+)/$', ArtistDetailView.as_view(), name='ArtistDetailView'),
    
    # releases
    #(r'^releases/', include('alabel.urls_release')),
    #url(r'^releases/$', ReleaseListView.as_view(), name='ReleaseListlView'),
    #url(r'^releases/(?P<slug>[-\w]+)/$', ReleaseDetailView.as_view(), name='ReleaseDetailView'),

    
    # form-test
    
    
    #url(r'^releases/(?P<slug>[-\w]+)/edit/$', ReleaseEditView.as_view(), name='ReleaseEditView'),
    #(r'^releases/(?P<slug>[-\w]+)/xml/$', ReleaseDetailView.as_view(
    #    template_name="alabel/xml/dummy.xml",
    #)),
    #(r'^releases/(?P<slug>[-\w]+)/json/$', JSONReleaseDetailView.as_view()),
    
    
    # media                   
    #(r'^tracks/$', MediaListView.as_view()),              
    #url(r'^tracks/(?P<slug>[-\w]+)/$', MediaDetailView.as_view(), name='TrackDetailView'),
    
    # views to serve protected (buyed) files
    url(r'^releases/(?P<slug>[-\w]+)/download/(?P<format>[a-z0-9]+)/(?P<version>[a-z0-9]+)/$', 'alabel.views.release_download', name='release-zip-view'),
    url(r'^tracks/(?P<slug>[-\w]+)/download/(?P<format>[a-z0-9]+)/(?P<version>[a-z0-9]+)/$', 'alabel.views.media_download', name='media-zip-view'),
    
    # html5 stream
    url(r'^tracks/(?P<uuid>[-\w]+)/stream_html5/$', 'alabel.views.stream_html5', name='media-stream_html5'),
    
    
    # playlist urls (for embedding)
    url(r'^releases/(?P<slug>[-\w]+)/playlist/(?P<format>[a-z0-9]+)/(?P<version>[a-z0-9]+)/$', 'alabel.views.release_playlist', name='release-playlist-view'),

    
    # REST-API urls
    url(r'^api/$', direct_to_template, {'template': 'alabel/api/index.html'}),

    url(r'^api/releases/$',          ListModelView.as_view(resource=ReleaseResource), name='release-resource-root'),
    url(r'^api/releases/(?P<uuid>[-\w]+)/$', InstanceModelViewRO.as_view(resource=ReleaseResource), name='release-resource-detail'),

    url(r'^api/tracks/$',          ListModelView.as_view(resource=MediaResource), name='media-resource-root'),
    url(r'^api/tracks/(?P<uuid>[-\w]+)/$', InstanceModelViewRO.as_view(resource=MediaResource), name='media-resource-detail'),
    
    url(r'^api/artists/$',          ListModelView.as_view(resource=ArtistResource), name='artist-resource-root'),
    url(r'^api/artists/(?P<uuid>[-\w]+)/$', InstanceModelViewRO.as_view(resource=ArtistResource), name='artist-resource-detail'),
    
    
)