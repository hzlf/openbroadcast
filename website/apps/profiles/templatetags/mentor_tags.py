# -*- coding: utf-8 -*-
from django import template

from classytags.helpers import InclusionTag
from classytags.core import Options
from classytags.arguments import Argument
from django.utils.safestring import mark_safe
import re

from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _

from ..models import Profile
from django.contrib.auth.models import User, Group

register = template.Library()


@register.inclusion_tag('profiles/templatetags/mentor_for_user.html', takes_context=True)
def mentor_for_user(context, profile, mentor):
    
    actions = []
    notes = None
    
    if profile.mentor == mentor and not profile.is_approved:
        
        notes = _("You're mentoring this user. Approving his/her profile will give full platform-access to the respective user. Pleace think twice before handling!")
        
        actions.append({
                        'description': _('asd'),
                        'name': _('Approve profile'),
                        'url': reverse('profiles-profile-mentor-approve', kwargs={'pk': profile.pk}),
                        })
        actions.append({
                        'description': _('asd'),
                        'name': _('Cancel mentorship'),
                        'url': reverse('profiles-profile-mentor-cancel', kwargs={'pk': profile.pk}),
                        })
    
    if not profile.mentor and mentor.has_perm('profiles.mentor_profiles'):
        
        # notes = _("Do youwant to become the mentor of this user?")
        
        actions.append({
                        'description': _('asd'),
                        'name': _('Become the mentor'),
                        'url': reverse('profiles-profile-mentor-become', kwargs={'pk': profile.pk}),
                        })
    
    
    context.update({
                    'user': profile.user,
                    'profile': profile,
                    'mentor': mentor,
                    'actions': actions,
                    'notes': notes,
                    })
    return context



