from django.conf.urls.defaults import *
from django.views.generic import ListView

from django.views.generic.simple import direct_to_template

# app imports
from alabel.models import Artist, Release, Media, Label
from alabel.views import *

# rest
from djangorestframework.views import ListOrCreateModelView, InstanceModelView
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
    (r'^artists/$', ArtistListView.as_view()),              
    url(r'^artists/(?P<slug>[-\w]+)/$', ArtistDetailView.as_view(), name='ArtistDetailView'),
    
    # releases                   
    (r'^releases/$', ReleaseListView.as_view()),
    (r'^releases/(?P<slug>[-\w]+)/$', ReleaseDetailView.as_view()),
    
    # form-test
    url(r'^releases/(?P<slug>[-\w]+)/edit/$', ReleaseEditView.as_view(), name='ReleaseEditView'),
    
    (r'^releases/(?P<slug>[-\w]+)/xml/$', ReleaseDetailView.as_view(
        template_name="alabel/xml/dummy.xml",
    )),
    (r'^releases/(?P<slug>[-\w]+)/json/$', JSONReleaseDetailView.as_view()),
    
    
    # media                   
    (r'^tracks/$', MediaListView.as_view()),              
    url(r'^tracks/(?P<slug>[-\w]+)/$', MediaDetailView.as_view(), name='TrackDetailView'),
    
    # views to serve protected (buyed) files
    url(r'^releases/(?P<slug>[-\w]+)/download/(?P<format>[a-z0-9]+)/(?P<version>[a-z0-9]+)/$', 'alabel.views.release_download', name='release-zip-view'),
    url(r'^tracks/(?P<slug>[-\w]+)/download/(?P<format>[a-z0-9]+)/(?P<version>[a-z0-9]+)/$', 'alabel.views.media_download', name='media-zip-view'),
    
    # playlist urls (for embedding)
    url(r'^releases/(?P<slug>[-\w]+)/playlist/(?P<format>[a-z0-9]+)/(?P<version>[a-z0-9]+)/$', 'alabel.views.release_playlist', name='release-playlist-view'),
    
    
    
    # REST-API urls

    url(r'^api/releases/$',          ListOrCreateModelView.as_view(resource=ReleaseResource), name='release-resource-root'),
    url(r'^api/releases/(?P<uuid>[-\w]+)/$', InstanceModelView.as_view(resource=ReleaseResource), name='release-resource-detail'),

    url(r'^api/tracks/$',          ListOrCreateModelView.as_view(resource=MediaResource), name='media-resource-root'),
    url(r'^api/tracks/(?P<uuid>[-\w]+)/$', InstanceModelView.as_view(resource=MediaResource), name='media-resource-detail'),
    

    url(r'^api/artists/$',          ListOrCreateModelView.as_view(resource=ArtistResource), name='artist-resource-root'),
    url(r'^api/artists/(?P<uuid>[-\w]+)/$', InstanceModelView.as_view(resource=ArtistResource), name='artist-resource-detail'),
    
    
)