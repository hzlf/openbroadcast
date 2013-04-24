from django.conf.urls.defaults import *

# app imports
from alibrary.models import License
from alibrary.views import *

urlpatterns = patterns('',

    url(r'^license/(?P<slug>[-\w]+)/$', LicenseDetailView.as_view(), name='alibrary-license-detail'),

)