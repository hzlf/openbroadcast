from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from menus.base import Modifier, Menu, NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu


from actstream.models import Action


class ActionMenu(CMSAttachMenu):
    
    name = _("Action Menu")
    
    def get_nodes(self, request):
        nodes = []
        
        """"""
        node = NavigationNode(
            _('All Actions'),
            reverse('actstream-action-list'),
            201
        )
        nodes.append(node)
        
        node = NavigationNode(
            _('My Action'),
            reverse('actstream-action-detail', args=['root']),
            211
        )
        nodes.append(node)

        
        return nodes
    
menu_pool.register_menu(ActionMenu)


