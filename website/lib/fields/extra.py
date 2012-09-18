from django.db.models import TextField, FileField
from markdown import markdown
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^lib\.fields\.extra\.MarkdownTextField"])
add_introspection_rules([], ["^lib\.fields\.extra\.ContentTypeRestrictedFileField"])


#from django.utils.html import conditional_escape, format_html, format_html_join
from django.forms.widgets import ClearableFileInput

class ExtraClearableFileInput(ClearableFileInput):
    initial_text = _('Currently')
    input_text = _('Change')
    clear_checkbox_label = _('Clear')

    template_with_initial = '<ul><li>%(initial)s</li><li>%(clear_template)s</li><li>%(input_text)s: %(input)s</li></ul>'
    template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
    

class MarkdownTextField (TextField):
    """
    A TextField that automatically implements DB-cached Markdown translation.

    Accepts two additional keyword arguments:

    if allow_html is False, Markdown will be called in safe mode,
    which strips raw HTML (default is allow_html = True).

    if html_field_suffix is given, that value will be appended to the
    field name to generate the name of the non-editable HTML cache
    field.  Default value is "_html".

    NOTE: The MarkdownTextField is not able to check whether the model
    defines any other fields with the same name as the HTML field it
    attempts to add - if there are other fields with this name, a
    database duplicate column error will be raised.

    """
    def __init__ (self, *args, **kwargs):
        self._markdown_safe = not kwargs.pop('allow_html', True)
        self._html_field_suffix = kwargs.pop('html_field_suffix', '_html')
        super(MarkdownTextField, self).__init__(*args, **kwargs)

    def contribute_to_class (self, cls, name):
        self._html_field = "%s%s" % (name, self._html_field_suffix)
        TextField(blank=True, null=True, editable=False).contribute_to_class(cls, self._html_field)
        super(MarkdownTextField, self).contribute_to_class(cls, name)

    def pre_save (self, model_instance, add):
        try:
            value = getattr(model_instance, self.attname)
            html = markdown(value, safe_mode=self._markdown_safe)
            setattr(model_instance, self._html_field, html)
            return value
        except Exception, e:
            print e
            return ""

    def __unicode__ (self):
        return self.attname
    
    
class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, content_types=None,max_upload_size=104857600, **kwargs):
        self.content_types = kwargs.pop('video/avi', 'video/mp4', 'video/3gp', 'video/wmp', 'video/flv', 'video/mov')
        self.max_upload_size = max_upload_size

        super(ContentTypeRestrictedFileField, self).__init__(**kwargs)


    def clean(self, *args, **kwargs):        
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass        

        return data
