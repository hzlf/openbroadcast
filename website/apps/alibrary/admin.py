from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdmin

from alibrary.models import Label, Release, Artist, License, Media, Profession, Playlist, Format, Relation, Mediaformat
#from alibrary.models import ArtistProfessions, MediaExtraartists, PlaylistMedia
from alibrary.models import ArtistProfessions, MediaExtraartists, ReleaseExtraartists, PlaylistMedia, ReleaseRelations, APILookup

from django.contrib.contenttypes.generic import *

from guardian.admin import GuardedModelAdmin

from ashop.models import *

from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response
from django.template import RequestContext, loader

from multilingual.admin import MultilingualModelAdmin

import reversion

def merge_selected(modeladmin,request,queryset): #This is an admin/
    import copy
    model = queryset.model
    model_name = model._meta.object_name
    return_url = "."
    list_display = copy.deepcopy(modeladmin.list_display)
    ids = []

    if '_selected_action' in request.POST: #List of PK's of the selected models
        ids = request.POST.getlist('_selected_action')

    if 'id' in request.GET: #This is passed in for specific merge links. This id comes from the linking model (Consumer, IR, Contact, ...)
        id = request.GET.get('id')
        ids.append(id)
        try:
            queryset = queryset | model.objects.filter(pk=id)
        except AssertionError:
            queryset = model.objects.filter(pk__in=ids)
        return_url = model.objects.get(pk=id).get_absolute_url() or "."

    if 'return_url' in request.POST:
        return_url = request.POST['return_url']

    if 'master' in request.POST:
        master = model.objects.get(id=request.POST['master'])
        queryset = model.objects.filter(pk__in=ids)
        for q in queryset.exclude(pk=master.pk):
            model_merge(master,q)
        messages.success(request,"All " + model_name + " records have been merged into the selected " + model_name + ".")
        return HttpResponseRedirect(return_url)

    #Build the display_table... This is just for the template.
    #----------------------------------------
    display_table = []
    try: list_display.remove('action_checkbox')
    except ValueError: pass

    titles = []
    for ld in list_display:
        if hasattr(ld,'short_description'):
            titles.append(strings.pretty(ld.short_description))
        elif hasattr(ld,'func_name'):
            titles.append(strings.pretty(ld.func_name))
        elif ld == "__str__":
            titles.append(model_name)
        else:
            titles.append(ld)
    display_table.append(titles)

    for q in queryset:
        row = []
        for ld in list_display:
            if callable(ld):
                row.append(mark_safe(ld(q)))
            elif ld == "__str__":
                row.append(q)
            else:
                row.append(mark_safe(getattr(q,ld)))
        display_table.append(row)
        display_table[-1:][0].insert(0,q.pk)
    #----------------------------------------

    return render_to_response('merge_preview.html',{'queryset': queryset, 'model': model, 'return_url':return_url,\
            'display_table':display_table, 'ids': ids}, context_instance=RequestContext(request))

merge_selected.short_description = "Merge selected records"


class BaseAdmin(reversion.VersionAdmin, GuardedModelAdmin):
    
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
    exclude = ['description',]
    extra = 1
    
class LabelAdmin(PlaceholderAdmin, BaseAdmin):
    
    # inlines = [LabelInline]
    #prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ['slug']
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug']}),
        
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

    
#class ReleaseAdmin(PlaceholderAdmin, BaseAdmin):
class ReleaseAdmin(BaseAdmin):

    #list_display   = ('name', 'get_extra_artists',)
    list_display   = ('name', 'releasetype', 'label', 'slug', 'uuid', 'catalognumber',)
    search_fields = ['name', 'label__name',]
    list_filter = ('releasetype','release_country',)
    
    #inlines = [RelationsInline, MediaInline, ReleaseExtraartistsInline, DownloadreleaseInline, HardwarereleaseInline]
    inlines = [RelationsInline, MediaInline, ReleaseExtraartistsInline]
    #prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ['slug', 'license']
    
    actions = [merge_selected]
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', ('main_image', 'cover_image',), ('label', 'catalognumber'), ('releasedate', 'release_country', 'license'), ('releasetype', 'pressings'), 'publish_date', 'enable_comments', 'main_format', 'excerpt', 'description']}),
        #('Mixed content', {'fields': ['placeholder_1'], 'classes': ['plugin-holder', 'plugin-holder-nopage']}),
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
    

    list_display   = ('name', 'listed',)
    search_fields = ['name', 'media__name',]
    list_filter = ('listed',)
    
    # inlines = [LabelInline]
    
    # RelationsInline, 
    inlines = [RelationsInline, ArtistProfessionsInline, ArtistMembersInline, ArtistParentsInline,]
    
    readonly_fields = ["folder",]
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'main_image', 'aliases', 'real_name', ('listed', 'disable_link',), 'enable_comments', 'excerpt', 'folder', ]}),
        ('Mixed content', {'fields': ['placeholder_1'], 'classes': ['plugin-holder', 'plugin-holder-nopage']}),
    ]
    
admin.site.register(Artist, ArtistAdmin)
      
class LicenseAdmin(reversion.VersionAdmin, MultilingualModelAdmin):
    
    inline_instances = ('name_translated', 'restricted', 'parent',)
    
    list_display   = ('name', 'key', 'slug',)
    search_fields = ('name',)
    
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
    list_filter = ('mediatype', 'license__name', 'processed')
    
    inlines = [MediaExtraartistsInline]

    readonly_fields = ['slug']
    
    
    """"""
    fieldsets = [
        (None,  {'fields': 
                 ['name', 'slug', 'isrc', 'tracknumber', 'mediatype', 'release', 'artist', 'license', 'master']
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



admin.site.register(APILookup)













