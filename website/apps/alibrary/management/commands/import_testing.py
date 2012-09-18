#-*- coding: utf-8 -*-
from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
import os
import sys

import re

from django.template.defaultfilters import slugify
from alibrary.models import Artist, Release, Media, Label

from filer.models.filemodels import File
from filer.models.audiomodels import Audio
from filer.models.imagemodels import Image

from audiotools import AudioFile, MP3Audio, M4AAudio, FlacAudio, WaveAudio, MetaData
import audiotools

from ep.API import fp
import echoprint
import subprocess
import struct


class FolderImporter(object):
    
    def __init__(self, * args, **kwargs):
        self.id = kwargs.get('id')


    def walker(self):
        print 'Walker...'
        
        if self.id:
            r = Release.objects.get(pk=int(self.id))
            print r




class Command(NoArgsCommand):

    option_list = BaseCommand.option_list + (
        make_option('--id',
            action='store',
            dest='id',
            default=False,
            help='The ID'),
        )

    def handle_noargs(self, **options):
        folder_importer = FolderImporter(**options)
        folder_importer.walker()
