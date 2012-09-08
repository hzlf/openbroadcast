from django.contrib import admin

from bcmon.models import *

from lib.admin.actions import export_as_csv_action

#class ChannelInline(admin.TabularInline):
#    model = Channel



class PlayoutAdmin(admin.ModelAdmin):    
    
    list_display = ('title', 'created', 'channel',)
    list_filter = ('channel',)
    
    readonly_fields = ('created', 'updated', 'uuid', )

    date_hierarchy = 'created'
    
    inlines = []
    
    actions = [export_as_csv_action("CSV Export", fields=['title', 'created', 'channel'])]
    actions = [export_as_csv_action("CSV Export ALL",)]


admin.site.register(Playout, PlayoutAdmin)
admin.site.register(Channel)














