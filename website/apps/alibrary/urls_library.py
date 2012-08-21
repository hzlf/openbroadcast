from django.conf.urls.defaults import *

# app imports
from alibrary.models import Release, Artist, License
from alibrary.views import *

urlpatterns = patterns('',
      
    #url(r'^releases/$', ReleaseListView.as_view(), name='ReleaseListView'),
    #url(r'^releases/(?P<slug>[-\w]+)/$', ReleaseDetailView.as_view(), name='ReleaseDetailView'),
      
    url(r'^artists/$', ArtistListView.as_view(), name='ArtistListlView'),              
    url(r'^artists/(?P<slug>[-\w]+)/$', ArtistDetailView.as_view(), name='ArtistDetailView'),
              
    url(r'^licenses/(?P<slug>[-\w]+)/$', LicenseDetailView.as_view(), name='LicenseDetailView'),

)