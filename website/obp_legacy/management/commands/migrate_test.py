#-*- coding: utf-8 -*-
from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
import os
import sys

import time

import re

from tagging.models import Tag

from alibrary.models import Artist, Release, Media, Label, Relation, License

from obp_legacy.models import *

from django.template.defaultfilters import slugify

from datetime import datetime

from lib.util import filer_extra

from filer.models import *


def id_to_location(id):
    l = "%012d" % id
    return '%d/%d/%d' % (int(l[0:4]), int(l[4:8]), int(l[8:12]))
    
    

class LegacyImporter(object):
    
    def __init__(self, * args, **kwargs):
        self.object_type = kwargs.get('object_type')
        self.verbosity = int(kwargs.get('verbosity', 1))
        

    def import_image(self):
        print 'image importer'
        
        url = 'http://userpage.chemie.fu-berlin.de/~gd/root_broschuere/media/bilder/anclusnan/anclusnan2x.jpg'
        folder = Folder.objects.get(name='01574266-d9ab-11e1-ba53-b8f6b11a3aed')
        
        filer_extra.url_to_file(url, folder)
        
        
        return









    def walker(self):
        
        if(self.object_type == 'image'):
                
            self.import_image()
                
        return
                
        




class Command(NoArgsCommand):
    """
    Import directory structure into alibrary:

        manage.py import_folder --path=/tmp/assets/images
    """

    option_list = BaseCommand.option_list + (
        make_option('--type',
            action='store',
            dest='object_type',
            default=False,
            help='Import files located in the path into django-filer'),
        )

    def handle_noargs(self, **options):
        legacy_importer = LegacyImporter(**options)
        legacy_importer.walker()
