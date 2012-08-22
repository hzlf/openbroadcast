from django import forms
from django.conf import settings

from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Div, HTML, Field
from crispy_forms.bootstrap import FormActions



from alibrary.models import Release, Media, Relation

import selectable.forms as selectable
from alibrary.lookups import *

class ReleaseForm(ModelForm):

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
        
        
    name = forms.CharField(widget=selectable.AutoCompleteWidget(ReleaseNameLookup), required=True)
    
    
    
    label = forms.CharField(widget=selectable.AutoCompleteSelectWidget(ReleaseLabelLookup, allow_new=True), required=True)
    

    def clean(self, *args, **kwargs):
          
        cd = super(ReleaseForm, self).clean()
        
        print cd
        
        print '::: LABEL :::'
        print cd['label']
        
        # label id
        label_id = cd['label'][2]
        
        print 'id',
        print label_id
        
        # mapping
        cd['label'], created = Label.objects.get_or_create(pk=label_id)

        return cd

    """ """
    def save(self, *args, **kwargs):
        return super(ReleaseForm, self).save(*args, **kwargs)
   
    
    
    
    
    
    


ReleasekMediaFormSet = inlineformset_factory(Release, Media, extra=2)