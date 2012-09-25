from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import FormActions

from importer.models import Import


class ImportCreateForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(ImportCreateForm, self).__init__(*args, **kwargs)        
        
        self.helper = FormHelper()
        self.helper.form_id = "bulk_edit%s" % 'asd'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = True
        """"""
        layout = Layout(

              Field('agree_terms'),
              Field('agree_documentation'),
  
            FormActions(
                Submit('submit', 'Continue', css_class='btn btn-primary')
            ),
        )
        self.helper.add_layout(layout)
    
    agree_terms = forms.BooleanField(
        label = _('I agree to the Terms & Conditions'),
        initial = False,
        required = True,
    )

    agree_documentation = forms.BooleanField(
        label = _('I read the ducumentation and know how Importing works'),
        initial = False,
        required = True,
    )
