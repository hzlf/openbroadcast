#-*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from filer.models.filemodels import File
from filer.models.foldermodels import Folder
from filer.models.imagemodels import Image
from filer.settings import FILER_IS_PUBLIC_DEFAULT

# from bcast.settings import *
from alibrary.models import Media


class MediaFix(object):
    def __init__(self, * args, **kwargs):
        self.verbosity = int(kwargs.get('verbosity', 1))

    def fix_durations(self):
        print "fix durations"
        
        ms = Media.objects.filter(duration=None)
        for m in ms:
            m.duration = m.get_duration()
            m.save()
        
        ms = Media.objects.filter(duration=0)
        for m in ms:
            m.duration = m.get_duration()
            m.save()

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        media_fix = MediaFix(**options)
        # file_importer.walker()
        media_fix.fix_durations()
