from django.conf import settings

from django import forms
from django.forms import widgets
from django.forms import ValidationError

from django.utils.translation import ugettext_lazy as _

from models import InvitationKey

from registration.forms import RegistrationForm

class InvitationKeyForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField(widget=widgets.Textarea, required=False)

class InvitationKeyField(forms.CharField):
    default_error_messages = {
        'used':    _(u'Invitations key can only be used once'),
        'expired': _(u'Invitation key has expired'),
        'invalid': _(u'Invitation key is invalid')
    }
    def __init__(self, *args, **kwargs):
        if 'error_messages' in kwargs:
            self.error_messages = kwargs['error_messages']
        else:
            self.error_messages = InvitationKeyField.default_error_messages
        return super(InvitationKeyField, self).__init__(*args, **kwargs)

    def clean(self, value):
        data = super(InvitationKeyField, self).clean(value)
        key = InvitationKey.objects.get_key(data)
        if key:
            if key.is_usable():
                return key # everything is OK
            elif key.key_used():
                raise ValidationError(self.error_messages['used'])
            elif key.key_expired():
                raise ValidationError(self.error_messages['expired'])
        raise ValidationError(self.error_messages['invalid'])

class InvitationKeyUseForm(forms.Form):
    default_error_messages = {
        'wrong_email': _(u'The e-mail does not match the invitation')
    }

    email = forms.EmailField()
    key = InvitationKeyField()

    def __init__(self, *args, **kwargs):
        if 'error_messages' in kwargs:
            self.error_messages = kwargs['error_messages']
        else:
            self.error_messages = InvitationKeyUseForm.default_error_messages
        return super(InvitationKeyUseForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(InvitationKeyUseForm, self).clean()
        if 'email' in data and 'key' in data:
            if getattr(settings, 'INVITE_MODE_STRICT', False) \
               and not data['key'].validate_email(data['email']):
                del data['key']
                del data['email']
                raise ValidationError(self.error_messages['wrong_email'])
        return data

class StrictRegistrationForm(RegistrationForm):
    default_error_messages = {
        'wrong_email': _(u'The e-mail does not match the invitation')
    }
    def __init__(self, *args, **kwargs):
        if 'error_messages' in kwargs:
            self.error_messages = kwargs['error_messages']
        else:
            self.error_messages = InvitationKeyUseForm.default_error_messages

        self.initial = kwargs.get('initial', {})
        self.force_initial_email  = getattr(settings, 'INVITE_MODE', False) and \
                                    getattr(settings, 'INVITE_MODE_STRICT', False)
        if self.force_initial_email and 'email' not in  self.initial:
            raise ValueError('Initial values must include email in strict invitation mode')

        super(StrictRegistrationForm, self).__init__(*args, **kwargs)
        if self.force_initial_email:
            self.fields['email'].widget.attrs['readonly'] = True
        
    def clean_email(self):
        data = self.cleaned_data['email']
        if self.force_initial_email and data != self.initial['email']:
            del self.cleaned_data['email']
            raise ValidationError(self.error_messages['wrong_email'])
        return data
