from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template


# pinax
#from pinax.apps.account.openid_consumer import PinaxConsumer
handler500 = "pinax.views.server_error"

from django.contrib import admin

from cms.sitemaps import CMSSitemap

from alibrary.sitemap import ReleaseSitemap

sitemaps = {
    'releases': ReleaseSitemap,
    'pages': CMSSitemap,
}

admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()



urlpatterns = patterns('',

    # admin
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r"^admin/", include(admin.site.urls)),
    
    
    
    (r'^dev/', include('dev.urls')), # shop main urls
    
    url(r"^ratings/", include("agon_ratings.urls")),
    
    url(r"^vote/", include('arating.urls')),
    url(r'^ac_tagging/', include('ac_tagging.urls')),
    
    
    url(r"^api/", include("alibrary.urls_api")),
    
    
    url(r'^api/', include('bcmon.urls_api')),
    

    url(r'^selectable/', include('selectable.urls')),
    
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    
    # varnish / ESI
    # (r'^esi/', include('esi.urls')),
    
    (r'^accounts/', include('allauth.urls')),
    (r'^accounts/notification/', include('notification.urls')),
    
    
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
    
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
    # apps
    #(r'^blog/', include('articles.urls')),
    #(r'^', include('alibrary.urls')),
    (r'^player/', include('aplayer.urls')),
    
    # cms base
    url(r'^', include('cms.urls')),

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