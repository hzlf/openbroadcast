from menus.base import Modifier, Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _

from alabel.models import Profession

class TestMenu(Menu):

    def get_nodes(self, request):
        
        nodes = []
        r = NavigationNode(_('Releases'), "/releases/", 3)
        a = NavigationNode(_('Artists'), "/artists/", 4)
        t = NavigationNode(_('Tracks'), "/tracks/", 5)
        nodes.append(r)
        nodes.append(a)
        nodes.append(t)

        
        """
        extra subnodes
        """
        professions = Profession.objects.all()
        
        for profession in professions:
            # print profession
            
            node = NavigationNode(profession.name, "/artists/?profession=" + profession.name, profession.id, 2)
            nodes.append(node)
        
        return nodes

menu_pool.register_menu(TestMenu)



class Level(Modifier):
    """
    marks all node levels
    """
    post_cut = True

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if breadcrumb:
            return nodes
        for node in nodes:
            if not node.parent:
                if post_cut:
                    node.menu_level = 0
                else:
                    node.level = 0
                self.mark_levels(node, post_cut)
        return nodes

    def mark_levels(self, node, post_cut):
        for child in node.children:
            
            # print child
            
            if post_cut:
                child.menu_level = node.menu_level + 1
            else:
                child.level = node.level + 1
            self.mark_levels(child, post_cut)

menu_pool.register_modifier(Level)