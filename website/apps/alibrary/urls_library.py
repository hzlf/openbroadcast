from django.conf.urls.defaults import *

# app imports
from alibrary.models import Release, Artist, License
from alibrary.views import *

urlpatterns = patterns('',

    url(r'^licenses/(?P<slug>[-\w]+)/$', LicenseDetailView.as_view(), name='alibrary-license-detail'),

)