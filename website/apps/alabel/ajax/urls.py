from django.conf.urls.defaults import *

# app imports
# from alabel.models import Artist, Release, Media, Label
from alabel.ajax.views import *


urlpatterns = patterns('',

    # releases                   
    (r'^releases/$', ReleaseAjaxListView.as_view()),
    #(r'^releases/(?P<slug>[-\w]+)/$', ReleaseDetailView.as_view()),

    
)