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


class FolderImporter(object):
    def __init__(self, * args, **kwargs):
        self.path = kwargs.get('path')
        self.label_name = kwargs.get('label_name')
        self.verbosity = int(kwargs.get('verbosity', 1))


    def import_file(self, file, folder):
        
        print "#########################"
        print folder.name
        print "#########################"
        

        """
        Create a Audio or an Image into the given folder
        """
        try:
            iext = os.path.splitext(file.name)[1].lower()
        except:
            iext = ''
            
        print 'iext:'
        print iext 
            
        if iext in ['.jpg', '.jpeg', '.png', '.gif']:
            obj, created = Image.objects.get_or_create(
                                original_filename=file.name,
                                file=file,
                                folder=folder,
                                is_public=True)
            
            print 'obj:',
            print obj
            
            
            
        if iext in ['.mp3', '.flac', '.wav', '.aiff']:
            obj, created = Audio.objects.get_or_create(
                                original_filename=file.name,
                                file=file,
                                folder=folder,
                                is_public=False)

        if obj:
            print 'have object'
            return obj
        else:
            return None



    def walker(self, path=None, base_folder=None):
        
        
        # Hardcoded as it is a test only...
        
        label_name = self.label_name
        label = Label.objects.get(name=label_name)
        
        
        path = path or self.path
        path = unicode(os.path.normpath(path))


        file_list = []
        file_size = 0
        folder_count = 0
        rootdir = sys.argv[1]
        
        releases = []
        artists = []
        tracks = []
        

        for root, subFolders, files in os.walk(path):
            folder_count += len(subFolders)
            for file in files:
                f = os.path.join(root,file)
                file_size = file_size + os.path.getsize(f)
                
                rel_path = f[len(path):]
                
                rel_path = rel_path.encode('ascii', 'ignore')


                #rel_path = '/The Prodigy/The Fat Of The Land/04 - Funky Stuff.flac'

                
                #print
                #print
                print '-------------------------------------------------------------'
                
                try:
                    
                    audiofile = audiotools.open(os.path.join(root, file))
                    metadata = audiofile.get_metadata()

                    print metadata
                    
                    """"""
                    artist_name = metadata.artist_name
                    release_name = metadata.album_name
                    track_name = metadata.track_name
                    tracknumber = metadata.track_number
                    

                    print 'artist: %s' % artist_name
                    print 'release: %s' % release_name
                    print 'track: %s' % track_name
                    print 'tracknumber: %s' % tracknumber
                    

                    
                    
                    """"""
                    release, release_created = Release.objects.get_or_create(name=release_name, slug=slugify(release_name), label=label)
                    artist, artist_created = Artist.objects.get_or_create(name=artist_name, slug=slugify(artist_name))
                    media, media_created = Media.objects.get_or_create(name=track_name, tracknumber=tracknumber, artist=artist, release=release)
                    
                    dj_file = DjangoFile(open(os.path.join(root, file)), name=file)
                    
                    
                    """
                    print "**:", 
                    print dj_file,
                    print dj_file.size
                    """
                    
                    
                    
                    """"""
                    if not media.master:
                        master = self.import_file(file=dj_file, folder=release.get_folder('tracks'))
                        media.master = master
                        media.save()
                        
                        
                        
                    if not release.main_image:
                        print 'Image missing'
                        tfile = 'temp/cover.jpg'
                        
                        audiofile = audiotools.open(os.path.join(root, file))
                        
                        metadata = audiofile.get_metadata()
                        for image in metadata.images():
                            #print image.data
                            
                            f = open(tfile,"wb")
                            f.write(image.data)
                            f.close()
                            
                            dj_file = DjangoFile(open(tfile), name='cover.jpg')
                            
                            cover = self.import_file(file=dj_file, folder=release.get_folder('pictures'))
                            
                            release.main_image = cover

                            release.save()
                        
                        pass
                        

                    
                except Exception, e:
                    print e
                    pass
                
        




class Command(NoArgsCommand):
    """
    Import directory structure into alibrary:

        manage.py import_folder --path=/tmp/assets/images
    """

    option_list = BaseCommand.option_list + (
        make_option('--path',
            action='store',
            dest='path',
            default=False,
            help='Import files located in the path into django-filer'),
        make_option('--label',
            action='store',
            dest='label_name',
            default=False,
            help='Label name'),
        )

    def handle_noargs(self, **options):
        folder_importer = FolderImporter(**options)
        folder_importer.walker()
