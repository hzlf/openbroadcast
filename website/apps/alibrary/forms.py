from django import forms
from django.conf import settings

from django.forms import ModelForm

from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet, generic_inlineformset_factory


from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions

from filer.models.imagemodels import Image

from django.contrib.admin import widgets as admin_widgets


from alibrary.models import Release, Media, Relation

from pagedown.widgets import PagedownWidget

import selectable.forms as selectable
from alibrary.lookups import *


import floppyforms as forms


class ReleaseForm(ModelForm):

    class Meta:
        model = Release
        fields = ('name','label','releasetype','release_country','catalognumber','description', 'main_image', 'releasedate')
        

    def __init__(self, *args, **kwargs):

        self.user = kwargs['initial']['user']
        self.instance = kwargs['instance']
        
        print self.instance
        
        print self.user.has_perm("alibrary.edit_release")
        print self.user.has_perm("alibrary.admin_release", self.instance)

        
        
        
        self.label = kwargs.pop('label', None)

        
        super(ReleaseForm, self).__init__(*args, **kwargs)
        
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
                LookupField('name', css_class='input-xlarge'),
                
                Div(
                    Field('releasetype', css_class='span9 input-small'),
                    #Field('release_country', css_class='span9 input-small'),
                    css_class='controls controls-row'
                ),
                
                
                
        )
        
        artist_layout = Fieldset(
                _('Artist(s)'),
                #Field('extra_artists', css_class='input-xlarge'),    
        )
        
        
        
        
        catalog_layout = Fieldset(
                _('Label/Catalog'),
                Field('label', css_class='input-xlarge'),
                Field('catalognumber', css_class='input-xlarge'),
                Field('release_country', css_class='input-xlarge'),
                Field('releasedate', css_class='input-xlarge'),
        )
        

            
        
        image_layout = Fieldset(
                'Meta',
                Field('description', css_class='input-xxlarge'),
                'main_image',
                #Field('relations', css_class='input-xxlarge'),
        )
        
        action_layout = FormActions(
                Submit('save', 'save', css_class="btn-primary pull-right ajax_submit"),
                Reset('reset', 'reset', css_class="btn-secondary pull-right"),
        )
        
        
        

        print self.user.has_perm("alibrary.edit_release")
        
        
        
        
            
        layout = Layout(
                        base_layout,
                        artist_layout,
                        image_layout,
                        catalog_layout,
                        action_layout,
                        )

            

            
        self.helper.add_layout(layout)

        


    
    main_image = forms.Field(widget=forms.FileInput(), required=False)
    
    
    
    # releasedate = forms.Field(widget=admin_widgets.AdminDateWidget(), required=False)
    
    from floppyforms.widgets import DateInput
    releasedate = forms.DateField(required=False,)
    
        
    name = forms.CharField(widget=selectable.AutoCompleteWidget(ReleaseNameLookup), required=True)

    label = selectable.AutoCompleteSelectField(ReleaseLabelLookup, allow_new=True, required=False)
    #extra_artists = selectable.AutoCompleteSelectMultipleField(ArtistLookup, required=False)
    
    # license = selectable.AutoCompleteSelectField(LicenseLookup, allow_new=True, required=False)
    
    description = forms.CharField(widget=PagedownWidget())   

    

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
                dj_file = DjangoFile(open(ui.temporary_file_path()), name='cover')
                cd['main_image'], created = Image.objects.get_or_create(
                                    original_filename='cover_%s' % self.instance.pk,
                                    file=dj_file,
                                    folder=self.instance.folder,
                                    is_public=True)
            except Exception, e:
                print e
                pass
            
        else:
            cd['main_image'] = self.instance.main_image


        

        return cd

    """ """
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
        
        
        """
        base_layout = Fieldset(
                '',
                Field('name', css_class='input-xlarge'),
                Field('artist', css_class='input-xlarge'),
                Field('isrc', css_class='input-xlarge'),
                
                Row(
                    Column(Field('tracknumber', css_class='input-small'), css_class='span2'),
                    Column(Field('mediatype', css_class='input-small'), css_class='span1'),
                    Column(Field('license', css_class='input-small'), css_class='span1'),
                    
                    
                    #Field('release_country', css_class='span9 input-small'),
                    css_class='controls controls-row'
                ),
                css_class='releasemedia-formset',
        )
        """
        
        base_layout = Row(
            #Fieldset(
                Column(
                       Field('tracknumber', css_class='input-small'),
                       Field('mediatype', css_class='input-small'),
                       Field('license', css_class='input-small'),
                       css_class='span2'
                       ),
                Column(
                       #Fieldset(
                                Field('name', css_class='input-xlarge'),
                                Field('artist', css_class='input-xlarge'),
                                Field('isrc', css_class='input-xlarge'),
                                #Row(
                                #    Column(
                                #           Field('license', css_class='input-small'),
                                #           css_class='span2 unpadded'
                                #           ),
                                #    Column(
                                #           Field('mediatype', css_class='input-small'),
                                #           css_class='span2'
                                #           ),
                                #    ),
                       #),
                       css_class='span5'
                       ),
                css_class='releasemedia-row row',      
            #)
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
 
        # store the formset in the .nested property
        """
        form.nested = [
            TenantFormset(data=self.data,
                            instance = instance,
                            prefix = 'TENANTS_%s' % pk_value)]
        """
  
  
"""""" 
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
    
    
    #artist = selectable.AutoCompleteSelectField(widget=selectable.AutoCompleteWidget(ArtistLookup), required=True)
    
    
   
  
    

ReleaseMediaFormSet = inlineformset_factory(Release, Media, form=BaseReleaseMediaForm, formset=BaseReleaseMediaFormSet, can_delete=False, extra=0, fields=('name', 'tracknumber', 'isrc', 'artist', 'license', 'mediatype',))

ReleaseRelationFormSet = generic_inlineformset_factory(Relation, extra=1, exclude=('service', 'action',))






    