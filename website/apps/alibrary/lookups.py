from selectable.base import ModelLookup
from selectable.registry import registry

from alibrary.models import *


class ReleaseNameLookup(ModelLookup):
    model = Release
    search_fields = ['name__icontains',]
    
    def get_item_label(self, item):
        return u"%s, %s" % (item.name, item.catalognumber)
    
registry.register(ReleaseNameLookup)

""""""
class ReleaseLabelLookup(ModelLookup):
    model = Label
    search_fields = ['name__icontains',]

    #def get_item_value(self, item):
        # Display for currently selected item
        #return item.name

    def get_item_label(self, item):
        # Display for choice listings
        return u"%s (%s)" % (item.name, item.pk)

    #def get_item_id(self, item):
        #return u"%s" % item.name
    
    
    
registry.register(ReleaseLabelLookup)

""""""
class ArtistLookup(ModelLookup):
    model = Artist
    search_fields = ['name__icontains',]

    #def get_item_value(self, item):
        # Display for currently selected item
        #return item.name

    def get_item_label(self, item):
        # Display for choice listings
        return u"%s (%s)" % (item.name, item.pk)

    #def get_item_id(self, item):
        #return u"%s" % item.name
    
    
    
registry.register(ArtistLookup)


class LicenseLookup(ModelLookup):
    model = License
    search_fields = ['name__icontains',]

    def get_item_label(self, item):
        # Display for choice listings
        return u"%s (%s)" % (item.name, item.restricted)

    #def get_item_id(self, item):
        #return u"%s" % item.name
    
    
    
registry.register(LicenseLookup)
