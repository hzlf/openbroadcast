from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from registration.views import register as registration_register
from registration.forms import RegistrationForm
from registration.backends import default as registration_backend

from invitation.models import InvitationKey
from invitation.forms import InvitationKeyForm, InvitationKeyUseForm
from invitation.backends import InvitationBackend, InvalidInvitationError

remaining_invitations_for_user = InvitationKey.objects.remaining_invitations_for_user

def invited(request,
            form_class=InvitationKeyUseForm,
            template_name='invitation/invited.html',
            extra_context=None, initial_form_data=None):

    extra_context = extra_context is not None and extra_context.copy() or {}
    initial_form_data = initial_form_data is not None and initial_form_data.copy() or {}

    # Populate form with whatever data we have
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES,
                          initial=initial_form_data)
    elif 'email' in request.GET or 'key' in request.GET:
        form = form_class(data=request.GET, initial=initial_form_data)
    else:
        form = form_class(initial=initial_form_data)

    # If form is valid, populate session
    if form.is_valid():
        request.session['invitation_email'] = form.cleaned_data['email']
        request.session['invitation_key'] = form.cleaned_data['key']
    else:
        request.session.pop('invitation_email', '')
        request.session.pop('invitation_key', '')

    if getattr(settings, 'INVITE_MODE', False) and not form.is_valid():
        extra_context['form'] = form
        return direct_to_template(request, template_name, extra_context)
    else:
        return HttpResponseRedirect(reverse('registration_register'))

def register(request, backend, success_url=None, form_class=None,
            disallowed_url='registration_disallowed',
            template_name='registration/registration_form.html',
            wrong_template_name='invitation/wrong_invitation_key.html',
            extra_context=None, initial_form_data=None):

    extra_context = extra_context is not None and extra_context.copy() or {}
    initial_form_data = initial_form_data is not None and initial_form_data.copy() or {}

    try:
        invitation_key = request.session.get('invitation_key', None)
        invitation_email = request.session.get('invitation_email', '')
        if getattr(settings, 'INVITE_MODE', False):
            if invitation_key is None:
                raise InvalidInvitationError('Invitation not valid')
            elif not invitation_key.is_usable():
                raise InvalidInvitationError('Invitation not usable')

            if getattr(settings, 'INVITE_MODE_STRICT', False):
                if not invitation_key.validate_email(invitation_email):
                    raise InvalidInvitationError('E-mail does not match invitation')
                initial_form_data['email'] = invitation_email
        
        if 'email' not in initial_form_data:
            initial_form_data['email'] = invitation_email

        extra_context['invitation_key'] = invitation_key
        extra_context['invitation_email'] = invitation_email
        return registration_register(request, backend, success_url,
                                     form_class, disallowed_url,
                                     template_name, extra_context,
                                     initial_form_data)
    except InvalidInvitationError:
        return HttpResponseRedirect(reverse('invitation_invited'))

@login_required
def invite(request, success_url=None,
            form_class=InvitationKeyForm,
            template_name='invitation/invitation_form.html',
            email_subject_template='invitation/invitation_email_subject.txt',
            email_template='invitation/invitation_email.txt',
            extra_context=None, initial_form_data=None):

    extra_context = extra_context is not None and extra_context.copy() or {}
    initial_form_data = initial_form_data is not None and initial_form_data.copy() or {}

    remaining_invitations = remaining_invitations_for_user(request.user)

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if remaining_invitations > 0 and form.is_valid():
            invitation = InvitationKey.objects.create_invitation(
                request.user, form.cleaned_data["email"])
            invitation.send_to(form.cleaned_data["email"],
                               email_subject_template, email_template,
                               form.cleaned_data["message"])
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('invitation_complete'))
    else:
        form = form_class(initial={'message':getattr(settings,'INVITATION_DEFAULT_MESSAGE','')})
    extra_context.update({
            'form': form,
            'remaining_invitations': remaining_invitations,
        })
    return direct_to_template(request, template_name, extra_context)
