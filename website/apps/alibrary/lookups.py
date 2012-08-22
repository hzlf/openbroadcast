from selectable.base import ModelLookup
from selectable.registry import registry

from alibrary.models import *


class ReleaseNameLookup(ModelLookup):
    model = Release
    search_fields = ['name__icontains',]
    
registry.register(ReleaseNameLookup)

""""""
class ReleaseLabelLookup(ModelLookup):
    model = Label
    search_fields = ['name__icontains',]
    
registry.register(ReleaseLabelLookup)
