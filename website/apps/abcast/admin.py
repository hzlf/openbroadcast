from django.contrib import admin

from abcast.models import *

class StationAdmin(admin.ModelAdmin):    
    
    list_display = ('name', 'type',)
    readonly_fields = ('uuid', 'slug', )
    
    inlines = []
    
class ChannelAdmin(admin.ModelAdmin):    
    
    list_display = ('name', 'station', 'type', 'stream_url', )
    list_filter = ('station', 'type',)
    readonly_fields = ('uuid', 'slug', )
    

admin.site.register(Station, StationAdmin)
admin.site.register(Channel, ChannelAdmin)














