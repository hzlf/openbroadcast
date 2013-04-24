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
    
class JingleInline(admin.TabularInline):
    
    exclude = ['description', 'slug', 'processed', 'conversion_status']
    
    model = Jingle
    
class JingleAdmin(admin.ModelAdmin):    
    
    list_display = ('name', 'duration', 'set', 'type' )
    list_filter = ('type',)
    readonly_fields = ('uuid', 'slug', )
    
class JingleSetAdmin(admin.ModelAdmin):    
    
    #list_display = ('name', 'duration', 'set', 'type' )
    #list_filter = ('type',)
    readonly_fields = ('uuid', 'slug', )
    
    inlines = [JingleInline, ]
    
    
    

admin.site.register(Station, StationAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Jingle, JingleAdmin)
admin.site.register(JingleSet, JingleSetAdmin)














