from django.conf.urls.defaults import *

# app imports
from alabel.models import Artist
from alabel.views import *

urlpatterns = patterns('',
      
    url(r'^$', ArtistListView.as_view(), name='ArtistListlView'),              
    url(r'^(?P<slug>[-\w]+)/$', ArtistDetailView.as_view(), name='ArtistDetailView'),

)