from django.conf.urls import *
from django.views.generic.simple import direct_to_template

from invitation.forms import StrictRegistrationForm
from invitation.views import invite, invited, register

urlpatterns = patterns('',
    url(r'^invite/complete/$',
                direct_to_template,
                {'template': 'invitation/invitation_complete.html'},
                name='invitation_complete'),
    url(r'^invite/$',
                invite,
                name='invitation_invite'),
    url(r'^invited/$',
                invited,
                name='invitation_invited'),
    url(r'^register/$',
                register,
                {
                    'backend': 'invitation.backends.InvitationBackend',
                    'form_class': StrictRegistrationForm,
                },
                name='registration_register'),
)
