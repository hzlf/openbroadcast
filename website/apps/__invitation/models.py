import os
import random
import datetime
import hashlib

try:
    from django.utils import timezone
    def now():
        return timezone.now()
except:
    def now():
        return datetime.datetime.now()

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.http import int_to_base36
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from registration.models import SHA1_RE


class InvitationKeyManager(models.Manager):
    def get_key(self, invitation_key):
        """
        Return InvitationKey, or None if it doesn't (or shouldn't) exist.
        """
        # Don't bother hitting database if invitation_key doesn't match pattern.
        if not SHA1_RE.search(invitation_key):
            return None

        try:
            key = self.get(key=invitation_key)
        except self.model.DoesNotExist:
            return None

        return key

    def is_key_valid(self, invitation_key):
        """
        Check if an ``InvitationKey`` is valid or not, returning a boolean,
        ``True`` if the key is valid.
        """
        invitation_key = self.get_key(invitation_key)
        return invitation_key and invitation_key.is_usable()

    def create_invitation(self, user, email):
        """
        Create an ``InvitationKey`` and returns it.

        The key for the ``InvitationKey`` will be a SHA1 hash, generated
        from a combination of the ``User``'s username and a random salt.
        """
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        key = hashlib.sha1("%s%s%s%s" % (now(), salt, user.username, email)).hexdigest()
        email_hash = hashlib.sha1(email).hexdigest()
        return self.create(from_user=user, key=key, email_hash=email_hash)

    def remaining_invitations_for_user(self, user):
        """
        Return the number of remaining invitations for a given ``User``.
        """
        invitation_user, created = InvitationUser.objects.get_or_create(
            inviter=user,
            defaults={'invitations_remaining': settings.INVITATIONS_PER_USER})

        if invitation_user.invitations_remaining == -1 \
                or settings.INVITATIONS_PER_USER == -1:
            return 1
        return invitation_user.invitations_remaining

    def delete_unused_expired_keys(self):
        for key in self.all():
            if key.key_expired() and not key.key_used():
                key.delete()


class InvitationKey(models.Model):
    key = models.CharField(_('invitation key'), max_length=40)
    email_hash =  models.CharField(_('email hash'), max_length=40)
    date_invited = models.DateTimeField(_('date invited'), 
                                        default=lambda: now())
    from_user = models.ForeignKey(User, 
                                  related_name='invitations_sent')
    registrant = models.OneToOneField(User, null=True, blank=True,
                                  related_name='invitations_used')

    objects = InvitationKeyManager()

    def __unicode__(self):
        return u"Invitation from %s on %s" % (self.from_user.username, self.date_invited)

    def is_usable(self):
        """
        Return whether this key is still valid for registering a new user.
        """
        return not (self.key_used() or self.key_expired())

    def key_used(self):
        """
        Return whether this key is still valid for registering a new user.
        """
        return self.registrant is not None

    def key_expired(self):
        """
        Determine whether this ``InvitationKey`` has expired, returning
        a boolean -- ``True`` if the key has expired.

        The date the key has been created is incremented by the number of days
        specified in the setting ``ACCOUNT_INVITATION_DAYS`` (which should be
        the number of days after invite during which a user is allowed to
        create their account); if the result is less than or equal to the
        current date, the key has expired and this method returns ``True``.

        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS)
        return self.date_invited + expiration_date <= now()
    key_expired.boolean = True

    def mark_used(self, registrant):
        """
        Note that this key has been used to register a new user.
        """
        self.registrant = registrant
        self.save()
        
    def send_to(self, email,
                email_subject_template='invitation/invitation_email_subject.txt',
                email_template='invitation/invitation_email.txt',
                message=''):
        """
        Send an invitation email to ``email``. Optionally include ``message``.
        """
        current_site = Site.objects.get_current()

        context = {
            'invitation_key': self,
            'invitation_path': self.build_invitation_path(email),
            'expiration_days': settings.ACCOUNT_INVITATION_DAYS,
            'site': current_site,
            'message': message
        }
        
        subject = render_to_string(email_subject_template, context)

        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message = render_to_string(email_template, context)
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    def validate_email(self, email):
        candidate_email_hash = hashlib.sha1(email).hexdigest()
        return candidate_email_hash == self.email_hash

    def build_invitation_path(self, email=None):
        return '%s?%s' % (reverse('invitation_invited'),
                         urlencode({ 'key': self.key, 'email': email, }))

class InvitationUser(models.Model):
    inviter = models.ForeignKey(User, unique=True)
    invitations_remaining = models.IntegerField()

    def __unicode__(self):
        return u"InvitationUser for %s" % self.inviter.username


def user_post_save(sender, instance, created, **kwargs):
    """Create InvitationUser for user when User is created."""
    if created:
        invitation_user = InvitationUser()
        invitation_user.inviter = instance
        invitation_user.invitations_remaining = settings.INVITATIONS_PER_USER
        invitation_user.save()

models.signals.post_save.connect(user_post_save, sender=User)


def invitation_key_post_save(sender, instance, created, **kwargs):
    """Decrement invitations_remaining when InvitationKey is created."""
    if created:
        invitation_user, created_user = InvitationUser.objects.get_or_create(
            inviter=instance.from_user,
            defaults={'invitations_remaining': settings.INVITATIONS_PER_USER})
        remaining = invitation_user.invitations_remaining
        if remaining != -1 and settings.INVITATIONS_PER_USER != -1:
            invitation_user.invitations_remaining = max(0, remaining - 1)
            invitation_user.save()

models.signals.post_save.connect(invitation_key_post_save, sender=InvitationKey)
