from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

from alibrary.menu import ReleaseMenu, ArtistMenu, LibraryMenu

class ReleaseApp(CMSApp):
    
    name = _("Release App")
    urls = ["alibrary.urls_release"]
    menus = [ReleaseMenu]

apphook_pool.register(ReleaseApp)


class ArtistApp(CMSApp):
    
    name = _("Artist App")
    urls = ["alibrary.urls_artist"]
    menus = [ArtistMenu]

apphook_pool.register(ArtistApp)


class LibraryApp(CMSApp):
    
    name = _("Library App")
    urls = ["alibrary.urls_library"]
    menus = [LibraryMenu]

apphook_pool.register(LibraryApp)