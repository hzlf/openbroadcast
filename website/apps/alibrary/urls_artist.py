from django.conf.urls.defaults import *

# app imports
from alibrary.models import Artist
from alibrary.views import ArtistDetailView, ArtistListView

urlpatterns = patterns('',
      
    url(r'^$', ArtistListView.as_view(), name='ArtistListlView'),              
    url(r'^(?P<slug>[-\w]+)/$', ArtistDetailView.as_view(), name='ArtistDetailView'),

)