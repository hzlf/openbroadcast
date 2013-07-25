from django.conf.urls.defaults import *
from spf.views import matches_csv
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = patterns('importer.views',

    url(r'^csv/$', login_required(matches_csv), name='spf-matches-csv'),

)