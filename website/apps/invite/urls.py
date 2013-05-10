# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('invite.views',
    url(r'^add/$', 'invite_add', name='invite-add'),
)
