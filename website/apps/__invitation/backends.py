from django.conf import settings

from django.contrib.auth.models import User
from registration.backends.default import DefaultBackend
from invitation.models import InvitationKey

import registration.signals

class InvalidInvitationError(Exception):
    pass

class InvitationBackend(DefaultBackend):
    def register(self, request, *args, **kwargs):
        """
        Register a new user account.
        """
        invitation_key = request.session.get('invitation_key', None)
        desired_email = kwargs.get('email', '')

        correct_key = False
        correct_email = False

        if invitation_key is not None and invitation_key.is_usable():
            correct_key = True
            if invitation_key.validate_email(desired_email):
                correct_email = True

        if getattr(settings, 'INVITE_MODE', False):
            if correct_key:
                if getattr(settings, 'INVITE_MODE_STRICT', False) and not correct_email:
                    raise InvalidInvitationError('Invalid e-mail')
            else:
                raise InvalidInvitationError('Invalid invitation')

        if correct_email:
            # We know the user owns the e-mail address because we sent them an
            # invitation and they accepted it. Just create a regular user.
            user = User.objects.create_user(username=kwargs['username'],
                                            email=kwargs['email'],
                                            password=kwargs['password1'])
            registration.signals.user_registered.send(sender=self.__class__,
                                                      user=user,
                                                      request=request)

        else:
            # Not sure if this address belongs to the user or not. Follow
            # through the regular user registration work flow.
            user = super(InvitationBackend, self).register(request, *args, **kwargs)

        if correct_key and user is not None:
            invitation_key.mark_used(user)
            request.session.pop('invitation_key', '')
            request.session.pop('invitation_email', '')

        return user
