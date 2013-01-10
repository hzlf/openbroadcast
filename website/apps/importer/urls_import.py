from django.conf.urls.defaults import *
from importer.views import *
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = patterns('importer.views',
                                               
    url(r'^$', login_required(ImportListView.as_view()), name='importer-import-list'),
    url(r'^create/$', login_required(ImportCreateView.as_view()), name='importer-import-create'),
    url(r'^(?P<pk>\d+)/$', login_required(ImportUpdateView.as_view()), name='importer-import-update'),
    
    url(r'^delete/(?P<pk>\d+)/$', login_required(ImportDeleteView.as_view()), name='importer-import-delete'),
    url(r'^modify/(?P<pk>\d+)/$', login_required(ImportModifyView.as_view()), name='importer-import-modify'),
    
    # upload handler
    url(r'^multi/(?P<import_id>\d+)/$', 'multiuploader', name='importer-upload-multi'),
    
    

)