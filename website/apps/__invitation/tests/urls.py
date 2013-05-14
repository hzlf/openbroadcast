from django.conf.urls import *
from django.views.generic.simple import direct_to_template

from registration.forms import RegistrationFormTermsOfService
from invitation.views import invite, invited, register

urlpatterns = patterns('',
                       url(r'', include('invitation.urls')),
                       url(r'', include('registration.backends.default.urls')),
)
