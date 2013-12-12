from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
    (r'^refactoring/$',             'direct_to_template', {'template': 'base/listing.html'}),
)