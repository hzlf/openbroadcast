from django import forms
from django.conf import settings

from django.forms import ModelForm, Form

from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet, generic_inlineformset_factory


from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions

from filer.models.imagemodels import Image

from django.contrib.admin import widgets as admin_widgets

import logging
logger = logging.getLogger(__name__)


from alibrary.models import Release, Media, Relation

from pagedown.widgets import PagedownWidget

import selectable.forms as selectable
from alibrary.lookups import *


import floppyforms as forms
from django_date_extensions.fields import ApproximateDateFormField

from ajax_select.fields import AutoCompleteSelectField
from ajax_select import make_ajax_field

    
from django.forms.widgets import FileInput, HiddenInput

#from floppyforms.widgets import DateInput
from tagging.forms import TagField
from ac_tagging.widgets import TagAutocompleteTagIt

from lib.widgets.widgets import ReadOnlyIconField

from lib.util.filer_extra import url_to_file



ACTION_LAYOUT =  action_layout = FormActions(
                HTML('<button type="submit" name="save" value="save" class="btn btn-primary pull-right ajax_submit" id="submit-id-save-i-classicon-arrow-upi"><i class="icon-save icon-white"></i> Save</button>'),            
                HTML('<button type="reset" name="reset" value="reset" class="reset resetButton btn btn-secondary pull-right" id="reset-id-reset"><i class="icon-trash"></i> Cancel</button>'),
        )
ACTION_LAYOUT_EXTENDED =  action_layout = FormActions(
                Field('publish', css_class='input-hidden' ),
                HTML('<button type="submit" name="save" value="save" class="btn btn-primary pull-right ajax_submit" id="submit-id-save-i-classicon-arrow-upi"><i class="icon-save icon-white"></i> Save</button>'),            
                HTML('<button type="submit" name="save-and-publish" value="save" class="btn pull-right ajax_submit save-and-publish" id="submit-id-save-i-classicon-arrow-upi"><i class="icon-bullhorn icon-white"></i> Save & Publish</button>'),            
                HTML('<button type="reset" name="reset" value="reset" class="reset resetButton btn btn-secondary pull-right" id="reset-id-reset"><i class="icon-trash"></i> Cancel</button>'),
        )


class ArtistActionForm(Form):
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', False)        
        super(ArtistActionForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        
        
        self.helper.add_layout(ACTION_LAYOUT)
        """
        if self.instance and self.instance.publish_date:
            self.helper.add_layout(ACTION_LAYOUT)
        else:
            self.helper.add_layout(ACTION_LAYOUT_EXTENDED)
        """    
    publish = forms.BooleanField(required=False)


class ArtistForm(ModelForm):

    class Meta:
        model = Artist
        fields = ('name',
                  'real_name',
                  'type',
                  'country',
                  'booking_contact',
                  'biography',
                  'main_image',
                  'date_start',
                  'date_end',
                  'd_tags',
                  'ipi_code',
                  'isni_code',)
        

    def __init__(self, *args, **kwargs):

        self.user = kwargs['initial']['user']
        self.instance = kwargs['instance']
        

        # print self.user.has_perm("alibrary.edit_release")
        # print self.user.has_perm("alibrary.admin_release", self.instance)

        
        self.label = kwargs.pop('label', None)
        

        super(ArtistForm, self).__init__(*args, **kwargs)
        
        """
        Prototype function, set some fields to readonly depending on permissions
        """
        """
        if not self.user.has_perm("alibrary.admin_release", self.instance):
            self.fields['catalognumber'].widget.attrs['readonly'] = 'readonly'
        """

        self.helper = FormHelper()
        self.helper.form_id = "id_feedback_form_%s" % 'asd'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False
        
        
        base_layout = Fieldset(
                               
                _('General'),
                LookupField('name', css_class='input-xlarge'),
                LookupField('namevariations', css_class='input-xlarge'),
                LookupField('real_name', css_class='input-xlarge'),
                LookupField('type', css_class='input-xlarge'),
                LookupField('country', css_class='input-xlarge'),
                LookupField('booking_contact', css_class='input-xlarge'),
        )


        activity_layout = Fieldset(
                _('Activity'),
                LookupField('date_start', css_class='input-xlarge'),
                LookupField('date_end', css_class='input-xlarge'),
        )

        meta_layout = Fieldset(
                _('Meta information'),
                LookupField('biography', css_class='input-xxlarge'),
                LookupImageField('main_image',),
                LookupField('remote_image',),
        )
        
        tagging_layout = Fieldset(
                'Tags',
                LookupField('d_tags'),
        )

        identifiers_layout = Fieldset(
                _('Identifiers'),
                LookupField('ipi_code', css_class='input-xlarge'),
                LookupField('isni_code', css_class='input-xlarge'),
        )
            
        layout = Layout(
                        base_layout,
                        activity_layout,
                        # artist_layout,
                        meta_layout,
                        tagging_layout,
                        identifiers_layout,
                        )

        self.helper.add_layout(layout)

        if self.instance:
            self.fields['namevariations'].initial = ', '.join(self.instance.namevariations.values_list('name', flat=True).distinct())

        

    
    main_image = forms.Field(widget=FileInput(), required=False)
    remote_image = forms.URLField(required=False)
    d_tags = TagField(widget=TagAutocompleteTagIt(max_tags=9), required=False, label=_('Tags'))
    namevariations = forms.CharField(widget=forms.Textarea(attrs={'rows':'2'}), required=False, label=_('Variations'))
    biography = forms.CharField(widget=PagedownWidget(), required=False, help_text="Markdown enabled text")
    # aliases = selectable.AutoCompleteSelectMultipleField(ArtistLookup, required=False)

    

    def clean(self, *args, **kwargs):
        
        cd = super(ArtistForm, self).clean()

        print "** ArtistForm cleaned data **********"
        print cd
        print "*************************************"
        
        main_image = cd.get('main_image', None)
        remote_image = cd.get('remote_image', None)

        if main_image:
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




        elif remote_image:
            print "adding image (remote)"
            try:
                cd['main_image'] = url_to_file(remote_image, self.instance.folder)
            except Exception, e:
                print e
            
        else:
            cd['main_image'] = self.instance.main_image


        return cd

    # TODO: take a look at save
    def save(self, *args, **kwargs):
        return super(ArtistForm, self).save(*args, **kwargs)
   
    
    

"""
Artists members / membership
"""
class BaseMemberFormSet(BaseInlineFormSet):


    def __init__(self, *args, **kwargs):

        self.instance = kwargs['instance']

        super(BaseMemberFormSet, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_artists_form_%s" % 'inline'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False

        base_layout = Row(
                Column(
                       Field('child', css_class='input-xlarge'),
                       css_class='span9'
                       ),
                Column(
                       Field('DELETE', css_class='input-mini'),
                       css_class='span3'
                       ),
                css_class='albumartist-row row-fluid form-autogrow',
        )

        self.helper.add_layout(base_layout)




    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseMemberFormSet, self).add_fields(form, index)

        # created the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = hash(form.prefix)


class BaseMemberForm(ModelForm):

    class Meta:
        model = ArtistMembership
        parent_model = Artist
        fields = ('child',)

    def __init__(self, *args, **kwargs):
        super(BaseMemberForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

    child = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False, label=_('Member'))
    #service = forms.CharField(label='', widget=ReadOnlyIconField(**{'url': 'whatever'}), required=False)
    #url = forms.URLField(label=_('Website / URL'), required=False)


    def clean_child(self):

        child = self.cleaned_data['child']
        if not child.pk:
            logger.debug('saving not existant child: %s' % child.name)
            child.save()
        return child


    def save(self, *args, **kwargs):
        instance = super(BaseMemberForm, self).save(*args, **kwargs)
        return instance


"""
Artists alias / "other projects"
"""

""""""
class BaseAliasFormSet(BaseInlineFormSet):


    def __init__(self, *args, **kwargs):

        self.instance = kwargs['instance']

        super(BaseAliasFormSet, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_artists_form_%s" % 'inline'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False

        base_layout = Row(
                Column(
                       Field('child', css_class='input-xlarge'),
                       css_class='span9'
                       ),
                Column(
                       Field('DELETE', css_class='input-mini'),
                       css_class='span3'
                       ),
                css_class='albumartist-row row-fluid form-autogrow',
        )

        self.helper.add_layout(base_layout)




    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseAliasFormSet, self).add_fields(form, index)

        # created the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = hash(form.prefix)


class BaseAliasForm(ModelForm):

    class Meta:
        model = Artist
        parent_model = Artist
        #fields = ('child',)

    def __init__(self, *args, **kwargs):
        super(BaseAliasForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

    child = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False, label=_('Alias'))
    #service = forms.CharField(label='', widget=ReadOnlyIconField(**{'url': 'whatever'}), required=False)
    #url = forms.URLField(label=_('Website / URL'), required=False)

    def clean_child(self):

        child = self.cleaned_data['child']
        if not child.pk:
            logger.debug('saving not existant child: %s' % child.name)
            child.save()
        return child

    def clean(self, *args, **kwargs):

        cd = super(BaseAliasForm, self).clean()
        return cd


    def save(self, *args, **kwargs):
        instance = super(BaseAliasForm, self).save(*args, **kwargs)
        return instance















  
class BaseArtistReleationFormSet(BaseGenericInlineFormSet):

        
        
    def __init__(self, *args, **kwargs):

        self.instance = kwargs['instance']
        super(BaseArtistReleationFormSet, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_releasemediainline_form_%s" % 'asdfds'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False
        
        base_layout = Row(
                Column(
                       Field('url', css_class='input-xlarge'),
                       css_class='span6 relation-url'
                       ),
                Column(
                       Field('service', css_class='input-mini'),
                       css_class='span4'
                       ),
                Column(
                       Field('DELETE', css_class='input-mini'),
                       css_class='span2'
                       ),
                css_class='row-fluid relation-row form-autogrow',
        )
 
        self.helper.add_layout(base_layout)
        


class BaseArtistReleationForm(ModelForm):

    class Meta:
        model = Relation
        parent_model = Artist
        formset = BaseArtistReleationFormSet
        fields = ('url','service',)
        
    def __init__(self, *args, **kwargs):
        super(BaseArtistReleationForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        self.fields['service'].widget.instance = instance

        if instance and instance.id:
            self.fields['service'].widget.attrs['readonly'] = True
        
    def clean_service(self):
        return self.instance.service

    service = forms.CharField(label='', widget=ReadOnlyIconField(), required=False)
    url = forms.URLField(label=_('Website / URL'), required=False)



# Compose Formsets
ArtistRelationFormSet = generic_inlineformset_factory(Relation,
                                                      form=BaseArtistReleationForm,
                                                      formset=BaseArtistReleationFormSet,
                                                      extra=10, exclude=('action',),
                                                      can_delete=True,)


MemberFormSet = inlineformset_factory(Artist,
                                       ArtistMembership,
                                       form=BaseMemberForm,
                                       formset=BaseMemberFormSet,
                                       fk_name = 'parent',
                                       extra=4,
                                       exclude=('position',),
                                       can_delete=True,
                                       can_order=False,)


AliasFormSet = inlineformset_factory(Artist,
                                       ArtistAlias,
                                       form=BaseAliasForm,
                                       formset=BaseAliasFormSet,
                                       fk_name = 'parent',
                                       extra=4,
                                       #exclude=('position',),
                                       can_delete=True,
                                       can_order=False,)

