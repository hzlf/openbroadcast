from django.contrib import admin
from alibrary.models import *
from django.contrib.contenttypes.generic import *
from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response
from django.template import RequestContext, loader

from guardian.admin import GuardedModelAdmin

from multilingual.admin import MultilingualModelAdmin
from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline

import reversion

from alibrary.admin import BaseAdmin

__all__ = ('RelationsInline', 'RelationAdmin')

class RelationsInline(GenericTabularInline):
    model = Relation
    extra=2
    fieldsets = [
        (None,               {'fields': ['url', 'name', 'service']}),
    ]
    readonly_fields = ['service']
      
      
class RelationAdmin(BaseAdmin):

    fieldsets = [
        (None,               {'fields': ['url', 'service']}),
    ]
    readonly_fields = ['service']
    
admin.site.register(Relation, RelationAdmin)
