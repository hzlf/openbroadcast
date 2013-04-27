from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

#from abcast.menu import JingleMenu

class JingleApp(CMSApp):
    
    name = _("Jingle App")
    urls = ["abcast.urls_jingle"]
    # menus = [JingleMenu]

apphook_pool.register(JingleApp)
