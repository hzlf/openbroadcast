from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

from alabel.menu import ReleaseMenu, ArtistMenu

class ReleaseApp(CMSApp):
    
    name = _("Release App")
    urls = ["alabel.urls_release"]
    menus = [ReleaseMenu]

apphook_pool.register(ReleaseApp)


class ArtistApp(CMSApp):
    
    name = _("Artist App")
    urls = ["alabel.urls_artist"]
    menus = [ArtistMenu]

apphook_pool.register(ArtistApp)