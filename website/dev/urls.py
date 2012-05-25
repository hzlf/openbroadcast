from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('django.views.generic.simple',
    (r'^refactoring/$',             'direct_to_template', {'template': 'base/listing.html'}),
)