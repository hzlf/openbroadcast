from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from menus.base import Modifier, Menu, NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu


from profiles.models import Profile


class ProfileMenu(CMSAttachMenu):
    
    name = _("Profile Menu")
    
    def get_nodes(self, request):
        nodes = []
        
        """"""
        node = NavigationNode(
            _('All Profiles'),
            reverse('profiles-profile-list'),
            171
        )
        nodes.append(node)
        
        node = NavigationNode(
            _('My Profile'),
            reverse('profiles-profile-detail', args=['root']),
            111
        )
        nodes.append(node)
        
        
        node = NavigationNode(
            _('Edit my Profile'),
            reverse('profiles-profile-edit'),
            121
        )
        nodes.append(node)
        
        return nodes
    
menu_pool.register_menu(ProfileMenu)


