"""
Unit tests for django-invitation.

These tests assume that you've completed all the prerequisites for
getting django-invitation running in the default setup, to wit:

1. You have ``invitation`` in your ``INSTALLED_APPS`` setting.

2. You have created all of the templates mentioned in this
   application's documentation.

3. You have added the setting ``ACCOUNT_INVITATION_DAYS`` to your
   settings file.

4. You have URL patterns pointing to the invitation views.

"""

import os
import datetime
import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core import management
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.importlib import import_module

from invitation import forms
from invitation.models import InvitationKey, InvitationUser


class InvitationTestCase(TestCase):
    """
    Base class for the test cases.

    This sets up one user and two keys -- one expired, one not -- which are
    used to exercise various parts of the application.

    """
    def setUp(self):
        self.sample_registration_data = {
            'username': 'new_user',
            'email': 'newbie@example.com',
            'password1': 'secret',
            'password2': 'secret'
        }

        self.saved_invite_mode = settings.INVITE_MODE
        # INVITE_MODE == True is the expected default for invitation
        # tests. InviteModeOffTests explicitly tests the alternative.
        settings.INVITE_MODE = True
        self.saved_invite_mode_strict = settings.INVITE_MODE_STRICT
        settings.INVITE_MODE_STRICT = True
        self.saved_invitations_per_user = settings.INVITATIONS_PER_USER
        settings.INVITATIONS_PER_USER = 10
        self.saved_template_dirs = getattr(settings, 'TEMPLATE_DIRS')
        settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

        self.sample_user = User.objects.create_user(username='alice',
                                                    password='secret',
                                                    email='alice@example.com')
        self.sample_key = InvitationKey.objects.create_invitation(
            user=self.sample_user, email=self.sample_registration_data['email'])
        self.expired_key = InvitationKey.objects.create_invitation(
            user=self.sample_user, email=self.sample_registration_data['email'])
        self.expired_key.date_invited -= datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS + 1)
        self.expired_key.save()

        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def tearDown(self):
        settings.INVITE_MODE = self.saved_invite_mode
        settings.INVITE_MODE_STRICT = self.saved_invite_mode_strict
        settings.TEMPLATE_DIRS = self.saved_template_dirs
        settings.INVITATIONS_PER_USER = self.saved_invitations_per_user
        super(InvitationTestCase, self).tearDown()

    def assertRedirect(self, response, viewname):
        """Assert that response has been redirected to ``viewname``."""
        self.assertEqual(response.status_code, 302)
        expected_location = 'http://testserver' + reverse(viewname)
        self.assertEqual(response['Location'], expected_location)


class InvitationModelTests(InvitationTestCase):
    """
    Tests for the model-oriented functionality of django-invitation.

    """
    def test_invitation_key_created(self):
        """
        Test that a ``InvitationKey`` is created for a new key.

        """
        self.assertEqual(InvitationKey.objects.count(), 2)

    def test_invitation_email(self):
        """
        Test that ``InvitationKey.send_to`` sends an invitation email.

        """
        self.sample_key.send_to('bob@example.com')
        self.assertEqual(len(mail.outbox), 1)

    def test_key_expiration_condition(self):
        """
        Test that ``InvitationKey.key_expired()`` returns ``True`` for expired
        keys, and ``False`` otherwise.

        """
        # Unexpired user returns False.
        self.assertFalse(self.sample_key.key_expired())
        self.assertTrue(self.sample_key.is_usable())

        # Expired user returns True.
        self.assertTrue(self.expired_key.key_expired())
        self.assertFalse(self.expired_key.is_usable())

    def test_key_used_condition(self):
        """
        Test that ``InvitationKey.key_used()`` returns ``True`` for used
        keys, and ``False`` otherwise.

        """
        # Unused key returns False.
        self.assertFalse(self.sample_key.key_used())
        self.assertTrue(self.sample_key.is_usable())

        # Create a used key
        used_key = InvitationKey.objects.create_invitation(
            user=self.sample_user, email=self.sample_registration_data['email'])
        used_key.registrant = self.sample_user

        # Used key True.
        self.assertTrue(used_key.key_used())
        self.assertFalse(used_key.is_usable())

    def test_validate_email(self):
        """
        Test that ``InvitationKey.validate_email()`` returns ``True`` iff
        e-mail address that matches the one used to create the invitation.
        """
        self.assertTrue(self.sample_key.validate_email(self.sample_registration_data['email']))
        self.assertFalse(self.sample_key.validate_email('different@example.com'))


    def test_expired_unused_key_deletion(self):
        """
        Test ``InvitationKey.objects.delete_unused_expired_keys()``.

        Only keys whose expiration date has passed are deleted by
        delete_unused_expired_keys. Used keys are left alone.

        """
        expired_used_key = InvitationKey.objects.create_invitation(
            user=self.sample_user, email=self.sample_registration_data['email'])
        expired_used_key.registrant = self.sample_user
        expired_used_key.date_invited -= datetime.timedelta(days=settings.ACCOUNT_INVITATION_DAYS + 1)
        expired_used_key.save()

        InvitationKey.objects.delete_unused_expired_keys()
        self.assertEqual(InvitationKey.objects.count(), 2)

    def test_management_command(self):
        """
        Test that ``manage.py cleanupinvitation`` functions correctly.

        """
        management.call_command('cleanupinvitation')
        self.assertEqual(InvitationKey.objects.count(), 1)

    def test_invitations_remaining(self):
        """Test InvitationUser calculates remaining invitations properly."""
        remaining_invites = InvitationKey.objects.remaining_invitations_for_user

        # New user starts with settings.INVITATIONS_PER_USER
        user = User.objects.create_user(username='newbie',
                                        password='secret',
                                        email='newbie@example.com')
        self.assertEqual(remaining_invites(user), settings.INVITATIONS_PER_USER)

        # After using some, amount remaining is decreased
        used = InvitationKey.objects.filter(from_user=self.sample_user).count()
        expected_remaining = settings.INVITATIONS_PER_USER - used
        remaining = remaining_invites(self.sample_user)
        self.assertEqual(remaining, expected_remaining)

        # Using Invitationuser via Admin, remaining can be increased
        invitation_user = InvitationUser.objects.get(inviter=self.sample_user)
        new_remaining = 2 * settings.INVITATIONS_PER_USER + 1
        invitation_user.invitations_remaining = new_remaining
        invitation_user.save()
        remaining = remaining_invites(self.sample_user)
        self.assertEqual(remaining, new_remaining)

        # If no InvitationUser (for pre-existing/legacy User), one is created
        old_sample_user = User.objects.create_user(username='lewis',
                                                   password='secret',
                                                   email='lewis@example.com')
        old_sample_user.invitationuser_set.all().delete()
        self.assertEqual(old_sample_user.invitationuser_set.count(), 0)
        remaining = remaining_invites(old_sample_user)
        self.assertEqual(remaining, settings.INVITATIONS_PER_USER)


class InvitationFormTests(InvitationTestCase):
    """
    Tests for the forms and custom validation logic included in
    django-invitation.

    """
    def test_invitation_key_form(self):
        """
        Test that ``InvitationKeyForm`` enforces email constraints.

        """
        invalid_data_dicts = [
            # Invalid email.
            {
                'data': {'email': 'example.com'},
                'error': ('email', [u"Enter a valid e-mail address."])
            },
            ]

        for invalid_dict in invalid_data_dicts:
            form = forms.InvitationKeyForm(data=invalid_dict['data'])
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors[invalid_dict['error'][0]], invalid_dict['error'][1])

        form = forms.InvitationKeyForm(data={'email': 'foo@example.com'})
        self.assertTrue(form.is_valid())

    def test_invitation_key_use_form(self):
        """
        Test that ``InvitationKeyUseForm`` enforces valid key, valid e-mail,
        and key matching e-mail.
        """

        valid_data_dicts = [
            {
                'email': self.sample_registration_data['email'],
                'key': self.sample_key.key
            }
        ]

        invalid_data_dicts = [
            {
                'email': 'foobar',
                'key': self.sample_key.key,
            },
            {
                'email': self.sample_registration_data['email'],
                'key': self.expired_key.key,
            },
            {
                'email': 'different@example.com',
                'key': self.sample_key.key,
            },
        ]

        # valid input
        for d in valid_data_dicts:
            form = forms.InvitationKeyUseForm(data=d)
            self.assertFalse(form.errors)
            
        # invalid input
        for d in invalid_data_dicts:
            form = forms.InvitationKeyUseForm(data=d)
            self.assertTrue(form.errors)

class InvitationViewTests(InvitationTestCase):
    """
    Tests for the views included in django-invitation.

    """
    urls = 'invitation.tests.urls'

    def test_invitation_view(self):
        """
        Test that the invitation view rejects invalid submissions,
        and creates a new key and redirects after a valid submission.

        """
        # You need to be logged in to send an invite.
        response = self.client.login(username='alice', password='secret')
        remaining_invitations = InvitationKey.objects.remaining_invitations_for_user(self.sample_user)

        # Invalid email data fails.
        response = self.client.post(reverse('invitation_invite'),
                                    data={'email': 'example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'])
        self.assertTrue(response.context['form'].errors)

        # Valid email data succeeds.
        response = self.client.post(reverse('invitation_invite'),
                                    data={'email': 'foo@example.com'})
        self.assertRedirect(response, 'invitation_complete')
        self.assertEqual(InvitationKey.objects.count(), 3)
        self.assertEqual(InvitationKey.objects.remaining_invitations_for_user(self.sample_user), remaining_invitations - 1)

        # Once remaining invitations exhausted, you fail again.
        while InvitationKey.objects.remaining_invitations_for_user(self.sample_user) > 0:
            self.client.post(reverse('invitation_invite'),
                             data={'email': 'foo@example.com'})
        self.assertEqual(InvitationKey.objects.remaining_invitations_for_user(self.sample_user), 0)
        response = self.client.post(reverse('invitation_invite'),
                                    data={'email': 'foo@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['remaining_invitations'], 0)
        self.assertTrue(response.context['form'])

    def test_invited_view(self):
        """
        Test that the invited view invite the user from a valid
        key and fails if the key is invalid or has expired.

        """
        # GET request with valid data redirects to registration
        response = self.client.get(reverse('invitation_invited'),
                                   {
                                       'key': self.sample_key.key,
                                       'email': self.sample_registration_data['email'],
                                   })
        self.assertRedirect(response, 'registration_register')
        self.assertEqual(self.client.session['invitation_key'], self.sample_key)
        self.assertEqual(self.client.session['invitation_email'],
                         self.sample_registration_data['email'])
        

        # GET request with invalid data loads the form pre-filled with values
        response = self.client.get(reverse('invitation_invited'),
                                   {
                                       'key': self.sample_key.key,
                                       'email': 'different@stampforge.org'
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invitation/invited.html')
        self.assertTrue(response.context['form'].non_field_errors())

        # Valid key and e-mail: redirect to registration
        response = self.client.post(reverse('invitation_invited'),
                                   {
                                       'key': self.sample_key.key,
                                       'email': self.sample_registration_data['email'],
                                   })
        self.assertRedirect(response, 'registration_register')
        self.assertEqual(self.client.session['invitation_key'], self.sample_key)
        self.assertEqual(self.client.session['invitation_email'],
                         self.sample_registration_data['email'])

        # Valid key without e-mail: asks for email address
        response = self.client.post(reverse('invitation_invited'),
                                   {'invitation_key': self.sample_key.key})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invitation/invited.html')
        self.assertIn('email', response.context['form'].errors)

        # Valid key and wrong e-mail: prefilled and asks for email address
        response = self.client.post(reverse('invitation_invited'),
                                   {
                                       'key': self.sample_key.key,
                                       'email': 'different@example.com',
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invitation/invited.html')
        self.assertTrue(response.context['form'].non_field_errors())

        # Expired key is flagged as an error
        response = self.client.post(reverse('invitation_invited'),
                                           {'key': self.expired_key.key})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invitation/invited.html')
        self.assertIn('key', response.context['form'].errors)

        # Invalid key is flagged as an error
        response = self.client.post(reverse('invitation_invited'),
                                           {'key': 'foo'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invitation/invited.html')
        self.assertIn('key', response.context['form'].errors)

        # Nonexistent key is flagged as an error
        response = self.client.post(reverse('invitation_invited'),
                                           {'key': hashlib.sha1('foo').hexdigest()})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invitation/invited.html')
        self.assertIn('key', response.context['form'].errors)

    def test_register_view_invalid_key(self):
        """
        Test that registration view expects a valid key in the session.

        Requests without a valid key are redirected to the invitation use form.

        """
        # Invalid key in session
        self.session['invitation_key'] = None
        self.session.save()

        # GET with invalid key
        response = self.client.get(reverse('registration_register'))
        self.assertRedirect(response, 'invitation_invited')

        # POST with invalid key
        data = self.sample_registration_data.copy()
        response = self.client.post(reverse('registration_register'), data)
        self.assertRedirect(response, 'invitation_invited')

    def test_register_view_valid_key(self):
        """
        Test that registration view works with a valid key.

        After a successful registration, the key is no longer usable and the
        session data is removed.

        """
        # Valid key in session
        self.session['invitation_key'] = self.sample_key
        self.session['invitation_email'] = self.sample_registration_data['email']
        self.session.save()

        # GET with valid key and matching e-mail
        response = self.client.get(reverse('registration_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_form.html')

        # POST with valid key but wrong e-mail
        data = self.sample_registration_data.copy()
        data['email'] = 'different@example.com'
        response = self.client.post(reverse('registration_register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_form.html')
        self.assertIn('email', response.context['form'].errors)

        # POST with valid key and matching e-mail
        data = self.sample_registration_data.copy()
        response = self.client.post(reverse('registration_register'), data)
        self.assertRedirect(response, 'registration_complete')

        # Verify user was created correctly
        user = User.objects.get(username=self.sample_registration_data['username'])
        key = InvitationKey.objects.get_key(self.sample_key.key)
        self.assertEqual(user, key.registrant)
        self.assertFalse(key.is_usable())
        self.assertNotIn('invitation_key', self.client.session)
        self.assertNotIn('invitation_email', self.client.session)

        self.assertTrue( user.is_active )
        self.assertEqual(len(mail.outbox), 0)

class StrictInviteModeOffTests(InvitationTestCase):
    """
    Tests for the case where INVITE_MODE_STRICT is False.

    (The test cases above generally assume that INVITE_MODE_STRICT is True.)
    """
    def setUp(self):
        super(StrictInviteModeOffTests, self).setUp()
        settings.INVITE_MODE_STRICT = False

    def test_register_view_different_email(self):
        """
        Test that registration view accepts a key with a different e-mail
        address and asks the user to to confirm their account.
        """
        # Valid key and some valid e-mail in session
        session = self.session
        session['invitation_key'] = self.sample_key
        session['invitation_email'] = 'different@example.com'
        session.save()

        # GET with valid key and some matching e-mail
        response = self.client.get(reverse('registration_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_form.html')

        # POST with valid key and some valid e-mail
        data = self.sample_registration_data.copy()
        data['email'] = 'different@example.com'
        response = self.client.post(reverse('registration_register'), data)
        self.assertRedirect(response, 'registration_complete')

        # Verify user was created correctly
        user = User.objects.get(username=self.sample_registration_data['username'])
        key = InvitationKey.objects.get_key(self.sample_key.key)
        self.assertEqual(user, key.registrant)
        self.assertFalse(key.is_usable())
        self.assertNotIn('invitation_key', self.client.session)
        self.assertNotIn('invitation_email', self.client.session)

        self.assertFalse( user.is_active )
        self.assertEqual(len(mail.outbox), 1)


class InviteModeOffTests(InvitationTestCase):
    """
    Tests for the case where INVITE_MODE is False.

    (The test cases above generally assume that INVITE_MODE is True.)

    """
    def setUp(self):
        super(InviteModeOffTests, self).setUp()
        settings.INVITE_MODE = False

    def test_invited_view(self):
        """
        Test that the invited view redirects to registration_register.

        """
        response = self.client.get(reverse('invitation_invited'),
                                   {'invitation_key': self.sample_key.key})
        self.assertRedirect(response, 'registration_register')

    def test_register_view(self):
        """
        Test register view.

        With INVITE_MODE = FALSE, django-invitation just passes this view on to
        django-registration's register.

        """
        # get
        response = self.client.get(reverse('registration_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_form.html')

        # post
        response = self.client.post(reverse('registration_register'),
                                    data=self.sample_registration_data)
        self.assertRedirect(response, 'registration_complete')
