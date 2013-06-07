from django.contrib import admin

# generic relations
from genericrelations.models import RelatedContentInline
from genericrelations.admin import GenericAdminModelAdmin

from abcast.models import Broadcast, Emission


class BroadcastAdmin(admin.ModelAdmin):
    pass
    #list_display = ('name', 'duration', 'set', 'type' )
    #list_filter = ('type',)
    #readonly_fields = ('uuid', 'slug', )
    
admin.site.register(Broadcast, BroadcastAdmin)

class EmissionAdmin(GenericAdminModelAdmin):
    pass
    # inlines = [RelatedContentInline,]
    list_display = ('name', 'time_start', 'time_end', 'type', 'user', 'source', 'locked', 'status')
    list_filter = ('type', 'status',)
    date_hierarchy = 'time_start'
    readonly_fields = ('duration', 'uuid', 'slug', )
    
admin.site.register(Emission, EmissionAdmin)