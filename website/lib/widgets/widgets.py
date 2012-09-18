from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.widgets import ClearableFileInput, CheckboxInput, HiddenInput, Widget


from filer.models import File, Image



class ReadOnlyIconField(Widget):
    
    def render(self, name, value, attrs=None):
        
        if not value:
            value = 'unknown'

        return mark_safe('<ul class="links external"><li class="icon external %s"></li></ul>' % value)

class AdvancedFileInput(ClearableFileInput):

    def __init__(self, *args, **kwargs):

        self.url_length = kwargs.pop('url_length',30)
        self.preview = kwargs.pop('preview',True)
        self.image_width = kwargs.pop('image_width',100)
        super(AdvancedFileInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None,):

        substitutions = {
            'initial_text': '',
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': '',
        }
        template = u'%(input)s'

        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)

        print "VALUE"
        print value

        file = File.objects.get(pk=value)
        
        print file.url

        if file.url:

            template = self.template_with_initial
            if self.preview:
                print "HAVE PREVIEW!!"
                substitutions['initial'] = (u'<a href="{0}">{1}</a><br>\
                <a href="{0}" target="_blank"><img src="{0}" width="{2}"></a>'.format
                    (escape(file.url),'.',
                     self.image_width))
            else:
                substitutions['initial'] = (u'<a href="{0}">{1}</a>'.format
                    (escape(value.url),'.'))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

