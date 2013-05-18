#-*- coding: utf-8 -*-
from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
import os
import sys

import time

import re

from tagging.models import Tag

#from alibrary.models import Artist, Release, Media, Label, Relation, License

from filer.models.filemodels import File
from filer.models.audiomodels import Audio
from filer.models.imagemodels import Image

from obp_legacy.models import *


from django.template.defaultfilters import slugify

from datetime import datetime

from lib.util import filer_extra

from audiotools import AudioFile, MP3Audio, M4AAudio, FlacAudio, WaveAudio, MetaData
import audiotools

from obp_legacy.util.migrator import get_release_by_legacy_object
from obp_legacy.util.migrator import get_label_by_legacy_object
from obp_legacy.util.migrator import get_artist_by_legacy_object
from obp_legacy.util.migrator import get_media_by_legacy_object
from obp_legacy.util.migrator import get_playlist_by_legacy_object
from obp_legacy.util.migrator import get_user_by_legacy_legacy_object
from obp_legacy.util.migrator import get_community_by_legacy_legacy_object


def id_to_location(id):
    l = "%012d" % id
    return '%d/%d/%d' % (int(l[0:4]), int(l[4:8]), int(l[8:12]))
    
    

class LegacyImporter(object):
    def __init__(self, * args, **kwargs):
        self.object_type = kwargs.get('object_type')
        self.verbosity = int(kwargs.get('verbosity', 1))
        
    def walker(self):
        
        if(self.object_type == 'release'):

            objects = Releases.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:100000]
        
            for legacy_obj in objects:
                obj, status = get_release_by_legacy_object(legacy_obj)                
                legacy_obj.migrated = datetime.now()
                legacy_obj.save()
        
        
        if(self.object_type == 'media'):

            objects = Medias.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:100000]
        
            print 'NUM OBJECTS: %s' % objects.count()
        
            for legacy_obj in objects:
                obj, status = get_media_by_legacy_object(legacy_obj)                
                legacy_obj.migrated = datetime.now()
                legacy_obj.save()
                
                        
        if(self.object_type == 'label'):

            objects = Labels.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:100000]
        
            for legacy_obj in objects:
                obj, status = get_label_by_legacy_object(legacy_obj)                
                legacy_obj.migrated = datetime.now()
                legacy_obj.save()
                
                        
        if(self.object_type == 'artist'):

            objects = Artists.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:100]
        
            for legacy_obj in objects:
                obj, status = get_artist_by_legacy_object(legacy_obj)                
                legacy_obj.migrated = datetime.now()
                legacy_obj.save()
                
                        
        if(self.object_type == 'user'):

            #objects = Users.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:5]
            #objects = Users.objects.using('legacy').exclude(username=u'').all()[0:1000]
            from obp_legacy.models_legacy import ElggUsers
            objects = ElggUsers.objects.using('legacy_legacy').filter(user_type='person')[0:2000]
            #objects = ElggUsers.objects.using('legacy_legacy').filter(user_type='person', ident=9)[0:2000] # jonas
        
            for legacy_obj in objects:
                obj, status = get_user_by_legacy_legacy_object(legacy_obj)                
                #legacy_obj.migrated = datetime.now()
                legacy_obj.save()
                
                        
        if(self.object_type == 'group'):

            #objects = Users.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:5]
            #objects = Users.objects.using('legacy').exclude(username=u'').all()[0:1000]
            from obp_legacy.models_legacy import ElggUsers
            objects = ElggUsers.objects.using('legacy_legacy').filter(user_type='community')[0:50]
        
            for legacy_obj in objects:
                obj, status = get_community_by_legacy_legacy_object(legacy_obj)                
                #legacy_obj.migrated = datetime.now()
                legacy_obj.save()
                
                        
        if(self.object_type == 'playlist'):

            from obp_legacy.models_legacy import ElggCmMaster
            objects = ElggCmMaster.objects.using('legacy_legacy').filter(type='Container')[0:100]
        
            for legacy_obj in objects:
                obj, status = get_playlist_by_legacy_object(legacy_obj)                
                #legacy_obj.migrated = datetime.now()
                legacy_obj.save()
                
                
        




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
