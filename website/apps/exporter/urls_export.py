from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

from exporter.views import *


urlpatterns = patterns('exporter.views',
                                               
    url(r'^$', login_required(ExportListView.as_view()), name='exporter-export-list'),
    url(r'^settings/$', login_required(ExportListView.as_view()), name='exporter-export-settings'),
    url(r'^(?P<pk>\d+)/$', login_required(ExportUpdateView.as_view()), name='exporter-export-update'),

    url(r'^delete-all/$', login_required(ExportDeleteAllView.as_view()), name='exporter-export-delete-all'),
    url(r'^delete/(?P<pk>\d+)/$', login_required(ExportDeleteView.as_view()), name='exporter-export-delete'),
    url(r'^modify/(?P<pk>\d+)/$', login_required(ExportModifyView.as_view()), name='exporter-export-modify'),
    
    url(r'^download/(?P<uuid>[^//]+)/(?P<token>[^//]+)/$', export_download, name='exporter-export-download'),

)