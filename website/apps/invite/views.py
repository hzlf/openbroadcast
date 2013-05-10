# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from common.decorators import render_to

from invite.models import Invite
from invite.settings import PENDING_LIMIT

@login_required
@render_to('invite/message.html')
def invite_add(request):
    if request.user.invites.filter(accepted=None).count() >= PENDING_LIMIT:
        return {'message': u'Limit reached'}
    else:
        Invite.objects.create(owner=request.user)
        next = request.GET.get('next', '/')
        return redirect(next)
