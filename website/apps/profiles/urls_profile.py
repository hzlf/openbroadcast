from django.conf.urls.defaults import *
from profiles.views import *

urlpatterns = patterns('profiles.views',
                       
        
    url(r'^edit/$',
        view='profile_edit',
        name='profile_edit',
    ),
                               
    url(r'^$', ProfileListView.as_view(), name='profiles-profile-list'),
    url(r'^(?P<slug>[-\w]+)/$', ProfileDetailView.as_view(), name='profiles-profile-detail'),

               
    #url(r'^(?P<username>[-\w]+)/$',
    #    view='profile_detail',
    #    name='profile_detail',
    #),
    #url (r'^$',
    #    view='profile_list',
    #    name='profile_list',
    #),
)