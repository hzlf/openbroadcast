from django.contrib import admin
from django import forms

# generic relations
from genericrelations.models import RelatedContentInline
from genericrelations.admin import GenericAdminModelAdmin

from abcast.models import Broadcast, Emission, Daypart, DaypartSet, Weekday


class BroadcastAdmin(admin.ModelAdmin):
    pass
    #list_display = ('name', 'duration', 'set', 'type' )
    #list_filter = ('type',)
    #readonly_fields = ('uuid', 'slug', )
    
admin.site.register(Broadcast, BroadcastAdmin)

class EmissionAdmin(GenericAdminModelAdmin):
    # inlines = [RelatedContentInline,]
    list_display = ('name', 'time_start', 'time_end', 'type', 'user', 'source', 'locked', 'status')
    list_filter = ('type', 'status',)
    date_hierarchy = 'time_start'
    readonly_fields = ('duration', 'uuid', 'slug', )
    
admin.site.register(Emission, EmissionAdmin)



# daypart integration
class DaypartInline(admin.TabularInline):
    model = Daypart

class DaypartSetAdmin(GenericAdminModelAdmin):
    list_display = ('channel', 'time_start', 'time_end',)
    list_filter = ('channel',)
    date_hierarchy = 'time_start'
    readonly_fields = ('uuid',)
    
    inlines = [DaypartInline,]

"""
class DaypartAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
"""
"""
class DaypartAdminForm(forms.ModelForm):
    class Meta:
        model = Daypart
        widgets = {
            'tags': admin.widgets.AdminTextareaWidget
        }
    
class DaypartAdmin(admin.ModelAdmin):
    form = DaypartAdminForm
"""    
admin.site.register(DaypartSet, DaypartSetAdmin)
admin.site.register(Daypart)
admin.site.register(Weekday)
