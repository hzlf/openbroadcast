from menus.base import Modifier, Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _

class ArticleMenu(Menu):

    def get_nodes(self, request):
        nodes = []
        e = NavigationNode(_('News'), "/blog/", 4)
        nodes.append(e)
        return nodes

menu_pool.register_menu(ArticleMenu)

