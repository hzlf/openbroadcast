#-*- coding: utf-8 -*-
import os
from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand, NoArgsCommand

from optparse import make_option
from datetime import *


class LibDebug(object):
    def __init__(self, * args, **kwargs):
        self.verbosity = int(kwargs.get('verbosity', 1))

    def test_relations(self):
        
        from alibrary.models import Relation, Release
        print "test_relations"
        
        r = Release.objects.get(pk=48)
        print r
        
        for rel in r.relations.all():
            print '*****************'
            print 'url:     %s' % rel.url
            print 'service: %s' % rel._service
            


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        lib_debug = LibDebug(**options)
        # file_importer.walker()
        lib_debug.test_relations()
