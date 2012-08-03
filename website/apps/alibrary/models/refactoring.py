# python
import datetime
import uuid
import shutil
import sys

# django
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.files import File as DjangoFile
from django.core.urlresolvers import reverse

from django.http import HttpResponse # needed for absolute url

from settings import *


# cms
from cms.models import CMSPlugin, Page
from cms.models.fields import PlaceholderField
from cms.utils.placeholder import get_page_from_placeholder_if_exists

# filer
from filer.models.filemodels import *
from filer.models.foldermodels import *
from filer.models.audiomodels import *
from filer.models.imagemodels import *
from filer.fields.image import FilerImageField
from filer.fields.audio import FilerAudioField
from filer.fields.file import FilerFileField

# modules
#from taggit.managers import TaggableManager
from django_countries import CountryField
from easy_thumbnails.files import get_thumbnailer

from polymorphic import PolymorphicManager, PolymorphicModel

# audiotools (for conversion)
from audiotools import AudioFile, MP3Audio, M4AAudio, FlacAudio, WaveAudio
import audiotools
import tempfile

# celery / task management
from celery.task import task


# shop
from shop.models import Product
from alibrary.nonconflict import classmaker
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField 

# audio processing / waveform
from lib.audioprocessing.processing import create_wave_images, AudioProcessingException
# import optparse

# logging
import logging
logger = logging.getLogger(__name__)

################
from alibrary.models import *





    
    
    
    



