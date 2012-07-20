from django.conf.urls.defaults import *

# app imports
from alibrary.models import Release
from alibrary.views import *

urlpatterns = patterns('',
      
    #url(r'^$', ReleaseListView.as_view(), name='ReleaseListView'),
    url(r'^$', ReleaseListView.as_view(), dict(filters=[{'field':'account__username','relationship':'iexact'}], orders=[{'field':'foobar'}]), name='ReleaseListView'),
    url(r'^(?P<slug>[-\w]+)/$', ReleaseDetailView.as_view(), name='ReleaseDetailView'),

)