from django.contrib import admin

from abcast.models import *


class BroadcastAdmin(admin.ModelAdmin):
    pass
    #list_display = ('name', 'duration', 'set', 'type' )
    #list_filter = ('type',)
    #readonly_fields = ('uuid', 'slug', )
    
admin.site.register(Broadcast, BroadcastAdmin)

class EmissionAdmin(admin.ModelAdmin):
    pass
    #list_display = ('name', 'duration', 'set', 'type' )
    #list_filter = ('type',)
    #readonly_fields = ('uuid', 'slug', )
    
admin.site.register(Emission, EmissionAdmin)