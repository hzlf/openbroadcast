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


from alibrary.models import Release, Media, Relation, ReleaseAlbumartists, Artist

from pagedown.widgets import PagedownWidget

import selectable.forms as selectable
from alibrary.lookups import *


import floppyforms as forms
from django_date_extensions.fields import ApproximateDateFormField


from django.forms.widgets import FileInput, HiddenInput

#from floppyforms.widgets import DateInput
from tagging.forms import TagField

# ui: http://aehlke.github.com/tag-it/
from ac_tagging.widgets import TagAutocompleteTagIt

from lib.widgets.widgets import ReadOnlyIconField

from lib.widgets.widgets import ReadOnlyField

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


class ReleaseActionForm(Form):

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', False)
        super(ReleaseActionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False



        if self.instance and self.instance.publish_date:
            self.helper.add_layout(ACTION_LAYOUT)
        else:
            self.helper.add_layout(ACTION_LAYOUT_EXTENDED)

    publish = forms.BooleanField(required=False)



"""
Bulk edit - Autocomplete for fields to apply on whole listing
"""
class ReleaseBulkeditForm(Form):

    def __init__(self, *args, **kwargs):

        self.instance = kwargs.pop('instance', False)
        self.disable_license = False
        if self.instance and self.instance.publish_date:
            self.disable_license = True

        super(ReleaseBulkeditForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper()
        self.helper.form_id = "bulk_edit%s" % 'asd'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False


        form_class = 'input-xlarge'
        if self.disable_license:
            form_class = 'hidden'


        base_layout = Div(
                Div(HTML('<h4>%s</h4><p>%s</p>' % (_('Bulk Edit'), _('Choose Artist name and/or license to apply on each track.'))), css_class='form-help'),
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
                           Field('bulk_license', css_class=form_class),
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
    #bulk_license = selectable.AutoComboboxSelectField(LicenseLookup, allow_new=False, required=False, label=_('License'))
    bulk_license = forms.ModelChoiceField(queryset=License.objects.all(), required=False, label=_('License'))



class ReleaseForm(ModelForm):

    class Meta:
        model = Release
        fields = ('name',
                  'label',
                  'releasetype',
                  'release_country',
                  'catalognumber',
                  'description',
                  'main_image',
                  'releasedate_approx',
                  'd_tags',
                  'barcode',)


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
                HTML("""<ul class="horizontal unstyled clearfix action label-select">
                    <li><a data-label="Unknown 22" href="#"><i class="icon-double-angle-right"></i> Unknown label</a></li>
                    <li><a data-label="Not on label" href="#"><i class="icon-double-angle-right"></i> Not on label</a></li>
                </ul>"""),
                LookupField('catalognumber', css_class='input-xlarge'),
                LookupField('release_country', css_class='input-xlarge'),
                # LookupField('releasedate', css_class='input-xlarge'),
                LookupField('releasedate_approx', css_class='input-xlarge'),
        )


        image_layout = Fieldset(
                'Meta',
                LookupField('description', css_class='input-xxlarge'),
                LookupImageField('main_image',),
                LookupField('remote_image',),
        )

        tagging_layout = Fieldset(
                'Tags',
                LookupField('d_tags'),
        )

        identifiers_layout = Fieldset(
                _('Identifiers'),
                LookupField('barcode', css_class='input-xlarge'),
        )

        layout = Layout(
                        #ACTION_LAYOUT,
                        base_layout,
                        # artist_layout,
                        image_layout,
                        catalog_layout,
                        tagging_layout,
                        identifiers_layout,
                        #ACTION_LAYOUT,
                        )

        self.helper.add_layout(layout)




    main_image = forms.Field(widget=FileInput(), required=False)
    remote_image = forms.URLField(required=False)
    #releasedate = forms.DateField(required=False,widget=forms.DateInput(format = '%Y-%m-%d'), input_formats=('%Y-%m-%d',))
    releasedate_approx = ApproximateDateFormField(label="Releasedate", required=False)
    d_tags = TagField(widget=TagAutocompleteTagIt(max_tags=9), required=False, label=_('Tags'))
    name = forms.CharField(widget=selectable.AutoCompleteWidget(ReleaseNameLookup), required=True)
    label = selectable.AutoCompleteSelectField(ReleaseLabelLookup, allow_new=True, required=False)
    description = forms.CharField(widget=PagedownWidget(), required=False)

    #extra_artists = selectable.AutoComboboxSelectMultipleField(ArtistLookup, required=False)


    # TODO: rework clean function
    def clean(self, *args, **kwargs):

        cd = super(ReleaseForm, self).clean()

        print
        print "ReleaseForm: clean"
        print cd
        print

        label = cd['label']
        try:
            if not label.pk:
                print "SEEMS TO BE NEW ONE..."
                label.save()
        except:
            pass


        main_image = cd.get('main_image', None)
        remote_image = cd.get('remote_image', None)

        if main_image:
            print "adding image (main)"
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
                       Field('license', css_class='input-small mode-m mode-l'),

                       Field('DELETE', css_class='input-mini'),

                       css_class='span3'
                       ),
                Column(
                        LookupField('name', css_class='input-large'),
                        LookupField('artist', css_class='input-large'),
                        Field('isrc', css_class='input-large mode-m mode-l'),
                        Field('filename', css_class='input-large mode-m mode-l'),
                       css_class='span9'
                       ),
                css_class='releasemedia-row row-fluid',
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
        #formset = BaseReleaseMediaFormSet
        #fields = ('name','tracknumber','base_filesize',)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs['instance']
        super(BaseReleaseMediaForm, self).__init__(*args, **kwargs)

        self.fields['filename'].widget.attrs['readonly'] = True

        if self.instance and self.instance.release and self.instance.release.publish_date:
            self.fields['license'].widget.attrs['readonly'] = True
            #self.fields['license'].widget = forms.TextInput(attrs={'readonly':'readonly'})


    artist = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False)
    tracknumber =  forms.CharField(label=_('No.'))
    filename =  forms.CharField(widget=ReadOnlyField(), label=_('Original File'), required=False)

    def clean_license(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.release.publish_date:
            #return
            return instance.license
        else:
            return self.cleaned_data['license']



"""
Album Artists
"""
class BaseAlbumartistFormSet(BaseInlineFormSet):


    def __init__(self, *args, **kwargs):

        self.instance = kwargs['instance']

        super(BaseAlbumartistFormSet, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_artists_form_%s" % 'inline'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False

        base_layout = Row(
                Column(
                       Field('join_phrase', css_class='input-small'),
                       css_class='span4'
                       ),
                Column(
                       Field('artist', css_class='input-xlarge'),
                       css_class='span6'
                       ),
                Column(
                       Field('DELETE', css_class='input-mini'),
                       css_class='span2'
                       ),
                css_class='albumartist-row row-fluid form-autogrow',
        )

        self.helper.add_layout(base_layout)




    def add_fields(self, form, index):
        # allow the super class to create the fields as usual
        super(BaseAlbumartistFormSet, self).add_fields(form, index)

        # created the nested formset
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance=None
            pk_value = hash(form.prefix)


class BaseAlbumartistForm(ModelForm):

    class Meta:
        model = ReleaseAlbumartists
        parent_model = Release
        fields = ('artist','join_phrase', 'position',)

    def __init__(self, *args, **kwargs):
        super(BaseAlbumartistForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)


    def clean_artist(self):

        artist = self.cleaned_data['artist']
        if not artist.pk:
            logger.debug('saving not existant artist: %s' % artist.name)
            artist.save()

        return artist

    artist = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False)
















class BaseReleaseReleationFormSet(BaseGenericInlineFormSet):



    def __init__(self, *args, **kwargs):

        self.instance = kwargs['instance']
        super(BaseReleaseReleationFormSet, self).__init__(*args, **kwargs)

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



class BaseReleaseReleationForm(ModelForm):

    class Meta:
        model = Relation
        parent_model = Release
        #formset = BaseReleaseReleationFormSet
        fields = ('url','service')

    def __init__(self, *args, **kwargs):
        super(BaseReleaseReleationForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        """"""

        self.fields['service'].widget.instance = instance

        if instance and instance.id:
            self.fields['service'].widget.attrs['readonly'] = True

    """"""
    def clean_service(self):
        return self.instance.service

    service = forms.CharField(label='', widget=ReadOnlyIconField(**{'url': 'whatever'}), required=False)
    url = forms.URLField(label=_('Website / URL'), required=False)

    #name = selectable.AutoCompleteSelectField(ArtistLookup, allow_new=True, required=False)
    #tracknumber =  forms.CharField(label=_('No.'))  


# Compose Formsets
ReleaseMediaFormSet = inlineformset_factory(Release,
                                            Media,
                                            form=BaseReleaseMediaForm,
                                            formset=BaseReleaseMediaFormSet,
                                            can_delete=True,
                                            extra=0,
                                            fields=('name', 'tracknumber', 'isrc', 'artist', 'license', 'mediatype','filename'),
                                            can_order=False)

AlbumartistFormSet = inlineformset_factory(Release,
                                           ReleaseAlbumartists,
                                           form=BaseAlbumartistForm,
                                           formset=BaseAlbumartistFormSet,
                                           extra=10,
                                           exclude=('position',),
                                           can_delete=True,
                                           can_order=False,)

ReleaseRelationFormSet = generic_inlineformset_factory(Relation,
                                                       form=BaseReleaseReleationForm,
                                                       formset=BaseReleaseReleationFormSet,
                                                       extra=10,
                                                       exclude=('action',),
                                                       can_delete=True)





    