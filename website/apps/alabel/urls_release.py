from django.conf.urls.defaults import *

# app imports
from alabel.models import Release
from alabel.views import *

urlpatterns = patterns('',
      
    url(r'^$', ReleaseListView.as_view(), name='ReleaseListlView'),
    url(r'^(?P<slug>[-\w]+)/$', ReleaseDetailView.as_view(), name='ReleaseDetailView'),

)