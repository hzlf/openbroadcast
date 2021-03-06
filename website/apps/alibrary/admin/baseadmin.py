from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdmin

"""
from alibrary.models import Label, Release, Artist, License, Media, Profession, Playlist, Format, Relation, Mediaformat, Daypart
from alibrary.models import ArtistProfessions, MediaExtraartists, ReleaseExtraartists, PlaylistMedia, ReleaseRelations, APILookup, PlaylistItemPlaylist, PlaylistItem
"""
from alibrary.models import *

from django.contrib.contenttypes.generic import *

from guardian.admin import GuardedModelAdmin

from ashop.models import *

from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response
from django.template import RequestContext, loader

from multilingual.admin import MultilingualModelAdmin

from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline

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
            try:
                model_merge(master,q)
            except:
                pass
        # messages.success(request,"All " + model_name + " records have been merged into the selected " + model_name + ".")
        return HttpResponseRedirect(return_url)

    #Build the display_table... This is just for the template.
    #----------------------------------------
    display_table = []
    try:
        list_display.remove('action_checkbox')
    except Exception:
        pass

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
    exclude = ['description','slug','processed','echoprint_status','conversion_status', 'd_tags', 'echonest_id', 'danceability', 'energy', 'liveness', 'loudness', 'speechiness', 'start_of_fade_out', 'echonest_duration', 'tempo', 'key', 'sections','master_sha1', 'base_format', 'base_filesize', 'base_duration', 'base_samplerate', 'base_bitrate', 'filename', 'publish_date', 'status', 'owner', 'creator', 'publisher', 'mediamumber', 'master', 'mediatype' ]
    readonly_fields = ['artist', ]
    extra = 1
    
class FormatAdmin(BaseAdmin):
    
    list_display   = ('format', 'version', 'default_price')

    fieldsets = [
        (None,               {'fields': ['format', 'version', 'default_price', 'excerpt']}),
    ]
    
admin.site.register(Format, FormatAdmin)
    
    
class ReleaseExtraartistsInline(admin.TabularInline):
    model = ReleaseExtraartists
    extra=1   
    
    
class ReleaseAlbumartistsInline(admin.TabularInline):
    model = ReleaseAlbumartists
    extra=2
    fieldsets = [
        (None,               {'fields': ['position', 'join_phrase', 'artist']}),
    ]
   

class RelationsInline(GenericTabularInline):
    model = Relation
    extra=2
    fieldsets = [
        (None,               {'fields': ['url', 'name', 'service']}),
    ]
    readonly_fields = ['service']

    
#class ReleaseAdmin(PlaceholderAdmin, BaseAdmin):

class ReleaseMediaMediaInline(admin.TabularInline):
    model = Media

    extra = 1

""""""
class ReleaseMediaInline(admin.TabularInline):
    model = ReleaseMedia

    extra = 1 
    inlines = [ReleaseMediaMediaInline]

class ReleaseAdmin(BaseAdmin):

    #list_display   = ('name', 'get_extra_artists',)
    list_display   = ('name', 'releasetype', 'label', 'slug', 'uuid', 'catalognumber',)
    search_fields = ['name', 'label__name',]
    list_filter = ('releasetype','release_country',)
    
    date_hierarchy = 'created'
    
    #inlines = [RelationsInline, MediaInline, ReleaseExtraartistsInline, DownloadreleaseInline, HardwarereleaseInline]
    inlines = [ReleaseAlbumartistsInline, ReleaseMediaInline, RelationsInline, MediaInline, ReleaseExtraartistsInline]
    #prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ['slug', 'license', 'd_tags']
    
    actions = [merge_selected]
    
    """"""
    fieldsets = [
        (None,  {
                'fields': ['name', 'slug', ('main_image', 'cover_image',), ('label', 'catalognumber'), ('releasedate', 'release_country', 'license'), ('releasetype', 'pressings'), 'publish_date', 'enable_comments', 'main_format', 'd_tags', 'excerpt', 'description']
                }),
        #('Artist relations',  {
        #        'fields': ['album_artists', 'album_artists_join',]
        #        }),
        ('Users', {'fields' : ['owner', 'creator', 'publisher']}),
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


class AgencyArtistInline(admin.TabularInline):
    model = Agency.artists.through
    extra = 1


class NameVariationInline(admin.TabularInline):
    model = NameVariation
    extra = 3
         
class ArtistAdmin(PlaceholderAdmin, BaseAdmin):
    

    list_display   = ('name', 'type', 'disambiguation', 'listed',)
    search_fields = ['name', 'media__name',]
    list_filter = ('listed',)
    
    # inlines = [LabelInline]
    
    # RelationsInline, 
    inlines = [NameVariationInline, RelationsInline, ArtistProfessionsInline, ArtistMembersInline, ArtistParentsInline, AgencyArtistInline]
    
    readonly_fields = ["folder",]
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'main_image', 'real_name', 'country', ('listed', 'disable_link',), 'enable_comments', 'biography', 'excerpt', 'folder', ]}),
        ('Users', {'fields' : ['owner', 'creator', 'publisher']}),
        #('Mixed content', {'fields': ['placeholder_1'], 'classes': ['plugin-holder', 'plugin-holder-nopage']}),
    ]
    
admin.site.register(Artist, ArtistAdmin)
admin.site.register(NameVariation)

class LicenseAdmin(reversion.VersionAdmin, MultilingualModelAdmin):
    
    inline_instances = ('name_translated', 'restricted', 'parent',)
    
    list_display   = ('name', 'key', 'slug',)
    search_fields = ('name',)
    
admin.site.register(License, LicenseAdmin)
      
      
      
      
class ServiceAdmin(BaseAdmin):
    pass
    
admin.site.register(Service, ServiceAdmin)      
      
      
class RelationAdmin(BaseAdmin):

    list_display = ('url', 'service', 'name',)
    list_filter = ('service',)
    search_fields = ('url',)
    fieldsets = [
        (None,               {'fields': ['url', 'service']}),
    ]
    #readonly_fields = ['service']
    
admin.site.register(Relation, RelationAdmin)
      
class ProfessionAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Profession, ProfessionAdmin)


""""""
class MediaReleaseInline(admin.TabularInline):
    model = Release.media.through
    extra = 1

    
class MediaAdmin(BaseAdmin):
    
    list_display   = ('name', 'created', 'release_link', 'artist', 'mediatype', 'tracknumber', 'mediamumber', 'duration', 'processed', 'echoprint_status', 'conversion_status')
    search_fields = ['artist__name', 'release__name', 'name']
    list_filter = ('mediatype', 'license__name', 'processed', 'echoprint_status', 'conversion_status')
    
    inlines = [MediaReleaseInline, RelationsInline, MediaExtraartistsInline]

    readonly_fields = ['slug', 'folder', 'uuid', 'base_format', 'base_filesize', 'base_duration','base_samplerate', 'base_bitrate', 'release_link', 'master_sha1', 'd_tags']


    date_hierarchy = 'created'
    
    """"""
    fieldsets = [
        (None,  {'fields': 
                 ['name', 'slug', 'isrc', 'filename', 'uuid', ('tracknumber', 'mediamumber'), 'mediatype', ('release', 'release_link'), 'artist', 'license', 'd_tags']
                 }),
                 
        ('Users', {'fields' : ['owner', 'creator', 'publisher']}),
                 
        ('Storage related',  {
                'fields': ['master', 'master_sha1', 'folder', ('base_format', 'base_filesize', 'base_duration',), ('base_samplerate', 'base_bitrate')]
                 }),

        ('Mixed content', {'fields': ['description'], 'classes': ['']}),
        ('Advanced options [Know what you are doing!!!!!!!!]', {
            'classes': ('uncollapse',),
            'fields': ('processed','echoprint_status','conversion_status',)
        }),
    ]
    
    
admin.site.register(Media, MediaAdmin)
    
    
class DistributorLabelInline(admin.TabularInline):
    model = Distributor.labels.through
    extra = 1
    
class LabelAdmin(PlaceholderAdmin, BaseAdmin):
    
    # inlines = [LabelInline]
    #prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ['slug']
    
    inlines = [RelationsInline]
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'type', 'description']}),
        ('Contact', {'fields' : ['address', 'country', ('phone', 'fax'), 'email']}),
        ('Settings', {'fields' : ['listed', 'disable_link', 'disable_editing']}),
        ('Relations', {'fields': ['parent',], 'classes': ['']}),
        ('Users', {'fields' : [('owner', 'creator', 'publisher'),]}),
    ]
    
admin.site.register(Label, LabelAdmin)
    
class DistributorAdmin(PlaceholderAdmin, BaseAdmin):
    
    # inlines = [LabelInline]
    #prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ['slug', 'd_tags']
    
    inlines = [DistributorLabelInline, RelationsInline]
    
    """"""
    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'type', 'description']}),
        ('Contact', {'fields' : ['address', 'country', ('phone', 'fax'), 'email']}),
        ('Relations', {'fields': ['parent'], 'classes': ['']}),
        ('Users', {'fields' : [('owner', 'creator', 'publisher'),]}),
        ('Other content', {'fields': ['first_placeholder'], 'classes': ['plugin-holder', 'plugin-holder-nopage']}),
    ]
    
admin.site.register(Distributor, DistributorAdmin)



class AgencyAdmin(BaseAdmin):

    # inlines = [LabelInline]
    #prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ['slug', 'd_tags']

    inlines = [AgencyArtistInline, RelationsInline]

    fieldsets = [
        (None,               {'fields': ['name', 'slug', 'type', 'description']}),
        ('Contact', {'fields' : ['address', 'country', ('phone', 'fax'), 'email']}),
        ('Relations', {'fields': ['parent'], 'classes': ['']}),
        ('Users', {'fields' : [('owner', 'creator', 'publisher'),]}),
    ]

admin.site.register(Agency, AgencyAdmin)
admin.site.register(AgencyScope)


    
class PlaylistmediaInline(GenericTabularInline):
    model = PlaylistMedia
    extra=1
    
class PlaylistItemInline(GenericTabularInline):
    model = PlaylistItem
    extra=1
    
class PlaylistItemPlaylistInline(admin.TabularInline):
    model = PlaylistItemPlaylist
    inlines = [PlaylistItemInline,] 
    extra=1
        
class PlaylistAdmin(GenericAdminModelAdmin):
    
    list_display   = ('name', 'user', 'type', 'duration', 'target_duration', 'is_current', 'rotation', 'updated')
    list_filter = ('type', 'broadcast_status', )

    search_fields = ['name', 'user__username',]
    date_hierarchy = 'created'
    
    #readonly_fields = ['slug', 'is_current',]

    inlines = [PlaylistItemPlaylistInline] 
 
class PlaylistItemAdmin(GenericAdminModelAdmin):
    pass
        
class DaypartAdmin(BaseAdmin):
    
    list_display   = ('day', 'time_start', 'time_end', 'active', 'playlist_count',)
    list_filter = ('day', 'active',)


    
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Daypart, DaypartAdmin)
admin.site.register(PlaylistItem, PlaylistItemAdmin)


        
class MediaformatAdmin(BaseAdmin):
    pass
    
admin.site.register(Mediaformat, MediaformatAdmin)



admin.site.register(APILookup)


from modeltranslation.admin import TranslationAdmin
class SeasonAdmin(TranslationAdmin):
    pass
class WeatherAdmin(TranslationAdmin):
    pass

admin.site.register(Season, SeasonAdmin)
admin.site.register(Weather, WeatherAdmin)

admin.site.register(Series)




"""
from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

admin.site.register(ApiKey)
admin.site.register(ApiAccess)


class UserModelAdmin(UserAdmin):
    inlines = UserAdmin.inlines + [ApiKeyInline]

admin.site.unregister(User)
admin.site.register(User,UserModelAdmin)
"""


