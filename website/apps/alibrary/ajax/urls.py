from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

# app imports
from alibrary.ajax.views import *

urlpatterns = patterns('',

    # releases                   
    (r'^releases/$', cache_page(ReleaseAjaxListView.as_view(), 60*60)),
    (r'^artists/$', cache_page(ArtistAjaxListView.as_view(), 60*60)),

    
)