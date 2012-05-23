from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

# pinax
#from pinax.apps.account.openid_consumer import PinaxConsumer
handler500 = "pinax.views.server_error"

from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',

    # admin
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r"^admin/", include(admin.site.urls)),
    
    # varnish / ESI
    # (r'^esi/', include('esi.urls')),
    
    (r'^accounts/', include('allauth.urls')),
    
    # filer (protected)
    (r'^', include('filer.server.urls')),
    
    # only devel
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }), 

    # shop
    (r'^shop/discount/', include('discount.urls')),
    # (r'^shop/cart/', include('shop_simplevariations.urls')), # urls for variations
    (r'^shop/cart/', include('shop_ajax.urls')), # urls for variations
    (r'^shop/', include('shop.urls')), # shop main urls
    
    # apps
    #(r'^blog/', include('articles.urls')),
    (r'^', include('alabel.urls')),
    (r'^player/', include('aplayer.urls')),
    
    # cms base
    (r'^', include('cms.urls')),

)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
)
    
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
)