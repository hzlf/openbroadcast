from django.conf.urls.defaults import *

# app imports

# rest
from djangorestframework.views import ListOrCreateModelView, InstanceModelView, ListModelView, InstanceModelViewRO
from importer.resources import *

urlpatterns = patterns('',

    url(r'^importer/$',          ListModelView.as_view(resource=ImportResource), name='release-resource-root'),
    url(r'^importer/(?P<pk>[-\w]+)/$', InstanceModelViewRO.as_view(resource=ImportResource), name='release-resource-detail'),

)