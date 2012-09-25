from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from menus.base import Modifier, Menu, NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu

from importer.models import Import

class ImportMenu(CMSAttachMenu):
    
    name = _("Import Menu")
    
    def get_nodes(self, request):
        nodes = []
        
        """"""
        node = NavigationNode(
            _('My Imports'),
            reverse('importer-import-list'),
            181
        )
        nodes.append(node)
        
        """"""
        node = NavigationNode(
            _('Help'),
            reverse('importer-import-list'),
            182
        )
        nodes.append(node)
        
        
        return nodes
    
menu_pool.register_menu(ImportMenu)


