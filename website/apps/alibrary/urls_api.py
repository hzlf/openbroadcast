from django.conf.urls.defaults import *
from django.views.generic import ListView

from django.views.generic.simple import direct_to_template

# app imports
from alibrary.models import Artist, Release, Media, Label
from alibrary.views import *

# rest
from djangorestframework.views import ListOrCreateModelView, InstanceModelView, ListModelView, InstanceModelViewRO
from alibrary.resources import *

urlpatterns = patterns('',
                       
    # REST-API urls
    url(r'^/$', direct_to_template, {'template': 'alibrary/api/index.html'}),

    url(r'^releases/$',          ListModelView.as_view(resource=ReleaseResource), name='release-resource-root'),
    url(r'^releases/(?P<uuid>[-\w]+)/$', InstanceModelViewRO.as_view(resource=ReleaseResource), name='release-resource-detail'),

    url(r'^tracks/$',          ListModelView.as_view(resource=MediaResource), name='media-resource-root'),
    url(r'^tracks/(?P<uuid>[-\w]+)/$', InstanceModelViewRO.as_view(resource=MediaResource), name='media-resource-detail'),
    
    url(r'^artists/$',          ListModelView.as_view(resource=ArtistResource), name='artist-resource-root'),
    url(r'^artists/(?P<uuid>[-\w]+)/$', InstanceModelViewRO.as_view(resource=ArtistResource), name='artist-resource-detail'),
    
    
)