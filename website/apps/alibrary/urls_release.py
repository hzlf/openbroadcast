from django.conf.urls.defaults import *

# app imports
from alibrary.models import Release
from alibrary.views import *

urlpatterns = patterns('',
    
    url(r'^autocomplete/$', release_autocomplete, name='release_autocomplete'),
      
    url(r'^$', ReleaseListView.as_view(), dict(filters=[{'field':'account__username','relationship':'iexact'}], orders=[{'field':'foobar'}]), name='ReleaseListView'),
    
    url(r'^(?P<slug>[-\w]+)/$', ReleaseDetailView.as_view(), name='ReleaseDetailView'),
    
    url(r'^(?P<slug>[-\w]+)/edit/$', ReleaseEditView.as_view(), name='alibrary-release-edit-view'),

    

)