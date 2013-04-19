from django.contrib import admin

from importer.models import *


class ImportImportFileInline(admin.TabularInline):
    model = ImportFile
    extra = 0
    readonly_fields = ('filename', 'mimetype', 'media')
    exclude = ('messages', 'results_tag', 'results_acoustid', 'results_musicbrainz', 'results_discogs', 'import_tag', 'imported_api_url')
    
class ImportItemnline(admin.TabularInline):
    model = ImportItem
    extra = 0
    readonly_fields = ('content_type', 'object_id',)

class ImportAdmin(admin.ModelAdmin):    
    
    list_display = ('created', 'user', 'status', 'type',)
    list_filter = ('status', 'user',)    
    readonly_fields = ('created', 'updated',)
    date_hierarchy = 'created'
    inlines = [ImportImportFileInline, ImportItemnline]

class ImportFileAdmin(admin.ModelAdmin):    
    
    list_display = ('created', 'filename', 'status',)
    list_filter = ('status', 'import_session__user',)    
    readonly_fields = ('created', 'updated', 'mimetype', 'import_session', 'results_tag', 'import_tag', 'results_musicbrainz', 'results_discogs',)
    date_hierarchy = 'created'

admin.site.register(Import, ImportAdmin)
admin.site.register(ImportFile, ImportFileAdmin)
admin.site.register(ImportItem)













