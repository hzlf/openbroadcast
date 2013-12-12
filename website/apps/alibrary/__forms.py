from django import forms
from django.forms import ModelForm, Form
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet, generic_inlineformset_factory
from django.utils.translation import ugettext as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions
from pagedown.widgets import PagedownWidget
from django.forms.widgets import FileInput
from tagging.forms import TagField

from filer.models.imagemodels import Image
from alibrary.models import Release, Media, Relation
import selectable.forms as selectable
from alibrary.lookups import *
from ac_tagging.widgets import TagAutocompleteTagIt
from lib.widgets.widgets import ReadOnlyIconField



ACTION_LAYOUT =  action_layout = FormActions(
                HTML('<button type="submit" name="save-i-classicon-arrow-upi" value="save" class="btn btn-primary pull-right ajax_submit" id="submit-id-save-i-classicon-arrow-upi"><i class="icon-ok icon-white"></i> Save</button>'),            
                HTML('<button type="reset" name="reset" value="reset" class="reset resetButton btn btn-secondary pull-right" id="reset-id-reset"><i class="icon-trash"></i> Cancel</button>'),
        )


class ActionForm(Form):
    
    def __init__(self, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.add_layout(ACTION_LAYOUT)
 

"""
Bulk edit - Autocomplete for fields to apply on whole listing
"""
class ReleaseBulkeditForm(Form):
    
    def __init__(self, *args, **kwargs):

        super(ReleaseBulkeditForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper()
        self.helper.form_id = "bulk_edit%s" % 'asd'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False

        base_layout = Div(
                Div(HTML('<h4>%s</h4><p>%s</p>' % (_('Bulk Edit'), _('Choose Artist name and/or license to apply on every track.'))), css_class='form-help'),
                Row(
                    Column(
                           Field('bulk_artist_name', css_class='input-xlarge'),
                           css_class='span6'
                           ),
                    Column(
                           HTML('<button type="button" id="bulk_apply_artist_name" value="apply" class="btn btn-mini pull-right bulk_apply" id="submit-"><i class="icon-plus"></i> %s</button>' % _('Apply Artist to all tracks')),
                           css_class='span2'
                           ),
                    css_class='releasemedia-row row',      
                ),
                Row(
                    Column(
                           Field('bulk_license', css_class='input-xlarge'),
                           css_class='span6'
                           ),
                    Column(
                           HTML('<button type="button" id="bulk_apply_license" value="apply" class="btn btn-mini pull-right bulk_apply" id="submit-"><i class="icon-plus"></i> %s</button>' % _('Apply License to all tracks')), 
                           css_class='span2'
                           ),
                    css_class='releasemedia-row row',      
                ),
                css_class='bulk_edit',
        )
        
        
        self.helper.add_layout(base_layout)
        
    # Fields
    bulk_artist_name = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False, label=_('Artist'))
    bulk_license = selectable.AutoComboboxSelectField(LicenseLookup, allow_new=False, required=False, label=_('License'))
    


class ReleaseForm(ModelForm):

    class Meta:
        model = Release
        fields = ('name','label','releasetype','release_country','catalognumber','description', 'main_image', 'releasedate', 'd_tags')
        

    def __init__(self, *args, **kwargs):

        self.user = kwargs['initial']['user']
        self.instance = kwargs['instance']
        
        print self.instance
        
        print self.user.has_perm("alibrary.edit_release")
        print self.user.has_perm("alibrary.admin_release", self.instance)

        
        self.label = kwargs.pop('label', None)

        super(ReleaseForm, self).__init__(*args, **kwargs)
        
        """
        Prototype function, set some fields to readonly depending on permissions
        """
        if not self.user.has_perm("alibrary.admin_release", self.instance):
            self.fields['catalognumber'].widget.attrs['readonly'] = 'readonly'
        

        self.helper = FormHelper()
        self.helper.form_id = "id_feedback_form_%s" % 'asd'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False
        
        
        base_layout = Fieldset(

                               
                _('General'),
                #Div(HTML('<h4>%s</h4><p>%s</p>' % (_('Bulk Edit'), _('Choose Artist name and/or license to apply on every track.'))), css_class='form-help'),
                LookupField('name', css_class='input-xlarge'),
                LookupField('releasetype', css_class='input-xlarge'),
        )
        
        artist_layout = Fieldset(
                _('Artist(s)'),
                Field('extra_artists', css_class='input-xlarge'),    
        )
        
        catalog_layout = Fieldset(
                _('Label/Catalog'),
                LookupField('label', css_class='input-xlarge'),
                LookupField('catalognumber', css_class='input-xlarge'),
                LookupField('release_country', css_class='input-xlarge'),
                LookupField('releasedate', css_class='input-xlarge'),
        )
        

        image_layout = Fieldset(
                'Meta',
                LookupField('description', css_class='input-xxlarge'),
                'main_image',
        )
        
        tagging_layout = Fieldset(
                'Tags',
                'd_tags',
        )
            
        layout = Layout(
                        #ACTION_LAYOUT,
                        base_layout,
                        artist_layout,
                        image_layout,
                        catalog_layout,
                        tagging_layout,
                        #ACTION_LAYOUT,
                        )

        self.helper.add_layout(layout)

        

    
    main_image = forms.Field(widget=FileInput(), required=False)
    releasedate = forms.DateField(required=False,)
    d_tags = TagField(widget=TagAutocompleteTagIt(max_tags=9), required=False, label=_('Tags'))
    name = forms.CharField(widget=selectable.AutoCompleteWidget(ReleaseNameLookup), required=True)
    label = selectable.AutoCompleteSelectField(ReleaseLabelLookup, allow_new=True, required=False)    
    description = forms.CharField(widget=PagedownWidget(), required=False, help_text="Markdown enabled text")   

    extra_artists = selectable.AutoComboboxSelectMultipleField(ArtistLookup, required=False)
    

    # TODO: rework clean function
    def clean(self, *args, **kwargs):
        
        cd = super(ReleaseForm, self).clean()

        print cd
        
        label = cd['label']
        if not label.pk:
            print "SEEMS TO BE NEW ONE..."
            label.save()
            
        
        if 'main_image' in cd and cd['main_image'] != None:
            print "IMAGE SAFIX!!"
            try:
                ui = cd['main_image']
                dj_file = DjangoFile(open(ui.temporary_file_path()), name='cover.jpg')
                cd['main_image'], created = Image.objects.get_or_create(
                                    original_filename='cover_%s.jpg' % self.instance.pk,
                                    file=dj_file,
                                    folder=self.instance.folder,
                                    is_public=True)
            except Exception, e:
                print e
                pass
            
        else:
            cd['main_image'] = self.instance.main_image


        

        return cd

    # TODO: take a look at save
    def save(self, *args, **kwargs):
        return super(ReleaseForm, self).save(*args, **kwargs)
   
    
    
 

  
class BaseReleaseMediaFormSet(BaseInlineFormSet): 
        

    def __init__(self, *args, **kwargs):

        self.instance = kwargs['instance']

        super(BaseReleaseMediaFormSet, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = "id_releasemediainline_form_%s" % 'asd'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False
        
        
        base_layout = Row(
                Column(
                       Field('tracknumber', css_class='input-small'),
                       Field('mediatype', css_class='input-small'),
                       Field('license', css_class='input-small'),
                       css_class='span2'
                       ),
                Column(
                                Field('name', css_class='input-xlarge'),
                                Field('artist', css_class='input-xlarge'),
                                Field('isrc', css_class='input-xlarge'),
                       css_class='span5'
                       ),
                css_class='releasemedia-row row',
        )
 
        self.helper.add_layout(base_layout)
        

        
 
    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseReleaseMediaFormSet, self).add_fields(form, index)
 
        # created the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = hash(form.prefix)
 
 

class BaseReleaseMediaForm(ModelForm):

    class Meta:
        model = Media
        parent_model = Release
        formset = BaseReleaseMediaFormSet
        fields = ('name','tracknumber',)
        
    def __init__(self, *args, **kwargs):
        self.instance = kwargs['instance']
        super(BaseReleaseMediaForm, self).__init__(*args, **kwargs)
        

    artist = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False)
    tracknumber =  forms.CharField(label=_('No.'))   




  
class BaseReleaseReleationFormSet(BaseGenericInlineFormSet):

        
        
    def __init__(self, *args, **kwargs):

        self.instance = kwargs['instance']
        super(BaseReleaseReleationFormSet, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_releasemediainline_form_%s" % 'relations'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False
        
        base_layout = Row(
                Column(
                       Field('url', css_class='input-xlarge'),
                       css_class='span5'
                       ),
                Column(
                       Field('service', css_class='input-small'),
                       css_class='span1'
                       ),
                Column(
                       Field('DELETE', css_class='input-mini'),
                       css_class='span1'
                       ),
                css_class='row relation-row',
        )
 
        self.helper.add_layout(base_layout)
        


class BaseReleaseReleationForm(ModelForm):

    class Meta:
        model = Relation
        parent_model = Release
        formset = BaseReleaseReleationFormSet
        fields = ('url','service',)
        
    def __init__(self, *args, **kwargs):
        super(BaseReleaseReleationForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['service'].widget.attrs['readonly'] = True
        
    def clean_service(self):
        return self.instance.service

    service = forms.CharField(label='', widget=ReadOnlyIconField(), required=False)
    url = forms.URLField(label=_('Website / URL'), required=False)

    #name = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False)
    #tracknumber =  forms.CharField(label=_('No.'))  


# Compose Formsets
ReleaseMediaFormSet = inlineformset_factory(Release, Media, form=BaseReleaseMediaForm, formset=BaseReleaseMediaFormSet, can_delete=False, extra=0, fields=('name', 'tracknumber', 'isrc', 'artist', 'license', 'mediatype',), can_order=False)
ReleaseRelationFormSet = generic_inlineformset_factory(Relation, form=BaseReleaseReleationForm, formset=BaseReleaseReleationFormSet, extra=3, exclude=('action',), can_delete=True)






    