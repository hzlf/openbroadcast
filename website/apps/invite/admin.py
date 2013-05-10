# -*- coding: utf-8

from django.contrib import admin
from invite.models import Invite

class InviteAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'acceptor', 'accepted']
    search_fields = ['id', 'owner', 'acceptor']

admin.site.register(Invite, InviteAdmin)
