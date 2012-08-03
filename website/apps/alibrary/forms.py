from django import forms
from django.conf import settings

from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Div, HTML, Field
from crispy_forms.bootstrap import FormActions

from alibrary.models import Release, Media, Relation

class ReleaseForm(ModelForm):
    pass
    class Meta:
        model = Release
        fields = ('name','label','releasetype','release_country','catalognumber',)
        

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = "id_feedback_form_%s" % 'asd'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                'Generic',
                'name',
                'label',
                'releasetype',
            ),
            Fieldset(
                'Location',
                'release_country',
                'catalognumber',
            ),
            FormActions(
                Submit('save', 'save', css_class="btn-primary pull-right ajax_submit"),
            )
        )
        super(ReleaseForm, self).__init__(*args, **kwargs)

ReleasekMediaFormSet = inlineformset_factory(Release, Media, extra=2)