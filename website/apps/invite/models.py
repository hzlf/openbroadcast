# -*- coding: utf-8 -*-
from random import choice
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError

from invite.settings import CODE_CHARS


def random_code():
    return ''.join(choice(CODE_CHARS) for x in xrange(40))


class Invite(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    owner = models.ForeignKey(User, related_name=u'invites')
    acceptor = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    accepted = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.pk

    def save(self, *args, **kwargs):
        # Needs to fix issue when invite accepted via admin interface
        if self.acceptor:
            if not self.accepted:
                self.accepted = datetime.now()

        if self.pk:
            return super(Invite, self).save(*args, **kwargs)
        else:
            for x in xrange(10):
                self.pk = random_code()
                try:
                    return super(Invite, self).save(*args, **kwargs)
                except IntegrityError:
                    pass
            else:
                raise Exception('Could not generate unique invite code')
