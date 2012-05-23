from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template


urlpatterns = patterns('',

    (r'^popup/$', direct_to_template, {'template': 'aplayer/popup.html'}),
    
    (r'^proxy/$', 'aplayer.views.sc_proxy'),
    
)