from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdmin

from alibrary.models import Label, Release, Artist, License, Media, Profession, Playlist, Format, Relation, Mediaformat
#from alibrary.models import ArtistProfessions, MediaExtraartists, PlaylistMedia
from alibrary.models import ArtistProfessions, MediaExtraartists, ReleaseExtraartists, PlaylistMedia, ReleaseRelations

from django.contrib.contenttypes.generic import *



from ashop.models import *


class BaseAdmin(admin.ModelAdmin):
    
    search_fields = ['name']
    save_on_top = True
    
    
class HardwarereleaseInline(admin.TabularInline):
    max_num = 10
    model = Hardwarerelease
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'medium', 'unit_price', 'active']}),
    ]
    readonly_fields = ['slug', 'medium']
    
class DownloadreleaseInline(admin.TabularInline):
    max_num = 1
    model = Downloadrelease
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'unit_price', 'active']}),
    ]
    readonly_fields = ['slug', 'name', 'unit_price']

class LabelInline(admin.TabularInline):
    model = Label
    extra = 1

class MediaInline(admin.TabularInline):
    model = Media
    exclude = ['tags', 'description']
    extra = 1
    
class LabelAdmin(PlaceholderAdmin, BaseAdmin):
    
    # inlines = [LabelInline]
    prepopulated_fields = {"slug": ("name",)}
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'folder']}),
        
        ('Relations', {'fields': ['parent'], 'classes': ['']}),
        
        ('Other content', {'fields': ['first_placeholder'], 'classes': ['plugin-holder', 'plugin-holder-nopage']}),
    ]
    
admin.site.register(Label, LabelAdmin)
    
class FormatAdmin(BaseAdmin):
    
    list_display   = ('format', 'version', 'default_price')

    fieldsets = [
        (None,               {'fields': ['format', 'version', 'default_price', 'excerpt']}),
    ]
    
admin.site.register(Format, FormatAdmin)
    
    
class ReleaseExtraartistsInline(admin.TabularInline):
    model = ReleaseExtraartists
    extra=1    
   

class RelationsInline(GenericTabularInline):
    model = Relation
    extra=2
    fieldsets = [
        (None,               {'fields': ['url', 'name', 'service']}),
    ]
    readonly_fields = ['service']

    
class ReleaseAdmin(PlaceholderAdmin, BaseAdmin):

    #list_display   = ('name', 'get_extra_artists',)
    list_display   = ('name', 'releasetype', 'label', 'releasedate',)
    search_fields = ['name', 'label__name',]
    list_filter = ('releasetype','release_country',)
    
    #inlines = [RelationsInline, MediaInline, ReleaseExtraartistsInline, DownloadreleaseInline, HardwarereleaseInline]
    inlines = [RelationsInline, MediaInline, ReleaseExtraartistsInline]
    prepopulated_fields = {"slug": ("name",)}
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', ('main_image', 'cover_image',), ('label', 'catalognumber', 'releasedate', 'release_country'), 'publish_date', 'enable_comments', 'main_format', 'excerpt']}),
        ('Mixed content', {'fields': ['placeholder_1'], 'classes': ['plugin-holder', 'plugin-holder-nopage']}),
        #('Test', {'fields' : ['tags']})
    ]
    
admin.site.register(Release, ReleaseAdmin)
  


class ArtistMembersInline(admin.TabularInline):
    model = Artist.members.through
    fk_name = 'parent'
    extra=1
    
class ArtistParentsInline(admin.TabularInline):
    model = Artist.members.through
    fk_name = 'child'
    extra=1
    
class ArtistProfessionsInline(admin.TabularInline):
    model = ArtistProfessions
    extra=1
    
class MediaExtraartistsInline(admin.TabularInline):
    model = MediaExtraartists
    extra=1


         
class ArtistAdmin(PlaceholderAdmin, BaseAdmin):
    

    list_display   = ('name', 'listed', 'priority',)
    search_fields = ['name', 'media__name',]
    list_filter = ('priority', 'listed')
    
    # inlines = [LabelInline]
    inlines = [RelationsInline, ArtistProfessionsInline, ArtistMembersInline, ArtistParentsInline,]
    
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["folder",]
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'main_image', 'aliases', 'real_name', ('priority', 'listed', 'disable_link',), 'enable_comments', 'excerpt', 'folder', ]}),
        ('Mixed content', {'fields': ['placeholder_1'], 'classes': ['plugin-holder', 'plugin-holder-nopage']}),
    ]
    
admin.site.register(Artist, ArtistAdmin)
      
class LicenseAdmin(BaseAdmin):
    pass
    
admin.site.register(License, LicenseAdmin)
      
class RelationAdmin(BaseAdmin):

    fieldsets = [
        (None,               {'fields': ['url', 'service']}),
    ]
    readonly_fields = ['service']
    
admin.site.register(Relation, RelationAdmin)
      
class ProfessionAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Profession, ProfessionAdmin)




    
class MediaAdmin(BaseAdmin):
    
    list_display   = ('name', 'release', 'artist', 'mediatype', 'tracknumber', 'processed')
    search_fields = ['artist__name', 'release__name']
    list_filter = ('artist__name','release__name', 'mediatype', 'license__name', 'processed')
    
    inlines = [MediaExtraartistsInline]


    
    
    """"""
    fieldsets = [
        (None,  {'fields': 
                 ['name', 'isrc', 'tracknumber', 'mediatype', 'release', 'artist', 'license', 'master', 'tags']
                 }),

        ('Mixed content', {'fields': ['description'], 'classes': ['']}),
        ('Advanced options [Know what you are doing!!!!!!!!]', {
            'classes': ('collapse',),
            'fields': ('processed',)
        }),
    ]
    
    
admin.site.register(Media, MediaAdmin)


    
class PlaylistmediaInline(admin.TabularInline):
    model = PlaylistMedia
    extra=1
        
class PlaylistAdmin(BaseAdmin):
    inlines = [PlaylistmediaInline]  
    
admin.site.register(Playlist, PlaylistAdmin)
        
class MediaformatAdmin(BaseAdmin):
    pass
    
admin.site.register(Mediaformat, MediaformatAdmin)

