from django.conf.urls.defaults import *
from exporter.views import *
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = patterns('exporter.views',
                                               
    url(r'^$', login_required(ExportListView.as_view()), name='exporter-export-list'),
    url(r'^(?P<pk>\d+)/$', login_required(ExportUpdateView.as_view()), name='exporter-export-update'),
    
    url(r'^delete/(?P<pk>\d+)/$', login_required(ExportDeleteView.as_view()), name='exporter-export-delete'),
    url(r'^modify/(?P<pk>\d+)/$', login_required(ExportModifyView.as_view()), name='exporter-export-modify'),

)