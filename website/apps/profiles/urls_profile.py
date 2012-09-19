from django.conf.urls.defaults import *
from profiles.views import *

urlpatterns = patterns('profiles.views',
                                               
    url(r'^$', ProfileListView.as_view(), name='profiles-profile-list'),
    url(r'^edit/$',  view='profile_edit', name='profiles-profile-edit'),
    url(r'^(?P<slug>[-\w]+)/$', ProfileDetailView.as_view(), name='profiles-profile-detail'),

)