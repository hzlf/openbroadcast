from django.conf.urls.defaults import *
from django.views.generic import ListView

from django.views.generic.simple import direct_to_template

# app imports
from importer.models import Artist, Release, Media, Label

# rest
from djangorestframework.views import ListOrCreateModelView, InstanceModelView, ListModelView, InstanceModelViewRO
from importer.resources import *

urlpatterns = patterns('',

    url(r'^importer/$',          ListModelView.as_view(resource=ImportResource), name='release-resource-root'),
    url(r'^importer/(?P<pk>[-\w]+)/$', InstanceModelViewRO.as_view(resource=ImportResource), name='release-resource-detail'),

)