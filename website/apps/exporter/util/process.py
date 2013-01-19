from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

from django.conf import settings

import logging
log = logging.getLogger(__name__)

class Process(object):


    def __init__(self):
        log = logging.getLogger('util.process.Process.__init__')


