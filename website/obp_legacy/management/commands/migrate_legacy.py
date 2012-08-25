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

from filer.models.filemodels import File
from filer.models.audiomodels import Audio
from filer.models.imagemodels import Image

from obp_legacy.models import *

from django.template.defaultfilters import slugify

from datetime import datetime

from lib.util import filer_extra

from audiotools import AudioFile, MP3Audio, M4AAudio, FlacAudio, WaveAudio, MetaData
import audiotools


def id_to_location(id):
    l = "%012d" % id
    return '%d/%d/%d' % (int(l[0:4]), int(l[4:8]), int(l[8:12]))
    
    

class LegacyImporter(object):
    def __init__(self, * args, **kwargs):
        self.object_type = kwargs.get('object_type')
        self.verbosity = int(kwargs.get('verbosity', 1))
        



    def import_release(self, lr):

        print 'trying to get related data'
        
        lms = lr.mediasreleases_set.all()
        las = lr.artistsreleases_set.all()
        lls = lr.labelsreleases_set.all()
        
        
        print 'legacy_id: %s' % lr.id
        
        r, created = Release.objects.get_or_create(legacy_id=lr.id)
        
        if created:
            print 'Not here yet -> created'
        else:
            print 'found by legacy_id -> use'
        
        """
        Release creation/update & mapping
        """
        r.slug = slugify(lr.name)
        r.legacy_id = lr.id
        
        """
        Mapping new <> legacy
        """
        r.name = lr.name
        print u'%s' % r.id
        


        
        if lr.catalognumber:
            r.catalognumber = lr.catalognumber
        
        if lr.releasetype:
            r.releasetype = lr.releasetype
        
        if lr.releasestatus:
            r.releasestatus = lr.releasestatus
        
        if lr.published:
            r.publish_date = lr.published
        
        if lr.notes:
            r.excerpt = lr.notes
            
        if lr.totaltracks:
            r.totaltracks = lr.totaltracks
            print 'totaltracks: %s' % r.totaltracks
        
        if lr.releasecountry and len(lr.releasecountry) == 2:
            r.release_country = lr.releasecountry
            
            
        # "relation" mapping
        if lr.discogs_releaseid and lr.discogs_releaseid != 'nf':
            url = 'http://www.discogs.com/release/%s' % lr.discogs_releaseid
            print 'discogs_url: %s' % url
            rel = Relation(content_object=r, url=url)
            rel.save()
            
        if lr.myspace_url:
            print 'myspace_url: %s' % lr.myspace_url
            rel = Relation(content_object=r, url=lr.myspace_url)
            rel.save()
            
        if lr.wikipedia_url:
            print 'wikipedia_url: %s' % lr.wikipedia_url
            rel = Relation(content_object=r, url=lr.wikipedia_url)
            rel.save()
            
            
        if lr.releasedate:
            print 'legacy-date: %s' % lr.releasedate

            seg = lr.releasedate.split('-')
            
            print seg
            
            # year only
            if len(seg) == 1:
                r.releasedate = '%s-%s-%s' % (seg[0], '01', '01')
            
            # year & month only
            if len(seg) == 2:
                if seg[1] in ('00', '0'):
                    seg[1] = '01'
                r.releasedate = '%s-%s-%s' % (seg[0], seg[1], '01')
            
            # full date
            if len(seg) == 3 and seg[0] != '0000':
                if seg[1] in ('00', '0'):
                    seg[1] = '01'
                if seg[2] in ('00', '0'):
                    seg[2] = '01'
                r.releasedate = '%s-%s-%s' % (seg[0], seg[1], seg[2] )
                
            
            print 'new-date: %s' % r.releasedate
            
        
        
        
        
        #time.sleep(2)
        
        
        r.save()
        
        # id:
        try:
            img_url = 'http://openbroadcast.ch/static/images/release/%s/original.jpg' % id_to_location(r.legacy_id)
            print img_url
            img = filer_extra.url_to_file(img_url, r.folder)
            
            r.main_image = img
            r.save()
        except:
            pass
        
        
        """
        Tag Mapping
        """
        ntrs = NtagsReleases.objects.using('legacy').filter(release_id=lr.id)
        # r.tags.clear()
        for ntr in ntrs:
            print 'Tag ID: %s' % ntr.ntag_id
            try:
                nt = Ntags.objects.using('legacy').get(id=ntr.ntag_id)
                print 'Tag Name: %s' % nt.name
                Tag.objects.add_tag(r, u'"%s"' % nt.name)
            except Exception, e:
                print e
                pass
            
            #r.tags.add_tag(nt.name)
            #r.tags.add(nt.name)
        
        
        """
        Label mapping
        """
        for ll in lls:
            l, created = Label.objects.get_or_create(legacy_id=ll.label.id)
            l.slug = slugify(ll.label.name)
            """
            Mapping new <> legacy
            """
            l.name = ll.label.name
            
            # save (& send to process queue...) :)
            l.save()
            
            # assign release
            r.label = l
            r.save()
        
        
        """
        Loop tracks and track-related artists
        """
        """""" 
        for lm in lms:
            m, created = Media.objects.get_or_create(legacy_id=lm.media.id)
            m.slug = slugify(lm.media.name)
                
            
            # Mapping new <> legacy
            
            m.name = lm.media.name
            try:
                m.tracknumber = int(lm.media.tracknumber)
            except Exception, e:
                m.tracknumber = 0
            
            # assign release
            m.release = r
            
            
            # license mapping
            if lm.media.license_id:
                lic, created = License.objects.get_or_create(legacy_id=lm.media.license_id)
                lic.name = lm.media.license_id
                lic.save()
                
                m.license = lic
            
            # save (& send to process queue...) :)
            m.save()
                
                
            # get master file / audio
            print "-----------------------------------------------------------"
            print "Import Audiofile:"
            if lm.media.sourcepath:
                print "source path: %s" % lm.media.sourcepath
                
                full_path = '/my_file/%s' % lm.media.sourcepath
                
                full_path = 'tmp/dummy.mp3'
                
                print "full path: %s" % full_path
                
                

                
                m.duration = lm.media.length
                
                if not m.master:
                    
                    audiofile = audiotools.open(full_path)
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
                
                    dj_file = DjangoFile(open(full_path), name=lm.media.filename)
                    
                    master = self.import_file(file=dj_file, folder=r.get_folder('tracks'))
                    
                    master.bits_per_sample = audiofile.bits_per_sample()
                    master.sample_rate = audiofile.sample_rate()
                    master.total_frames = audiofile.total_frames()
                    #master.seconds_length = audiofile.seconds_length()
                    
                    
                    

                    try:
                        iext = os.path.splitext(full_path)[1].lower()[1:]
                    except:
                        iext = None
                        
                    print 'IEXT %s' % iext
                    
                    master.filetype = iext
                    
                    master.save()
                    
                    m.master = master
                    
            m.save()
            
            
            # get track artist
            tlas = lm.media.artistsmedias_set.all()
            for tla in tlas:
                print "** TLA **"
                #print tla.artist.name
                
                a, created = Artist.objects.get_or_create(legacy_id=tla.artist.id)
                a.slug = slugify(tla.artist.name)
                a.name = tla.artist.name
                
                a.save()
                
                m.artist = a
                
            m.save()
            
            
            
        
        
        """
        Update migration timestamp on legacy database
        """
        lr.migrated = datetime.now()
        lr.save()
        
        
        return


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
            
            
            
        if iext in ['.mp3','.flac','.m4a','.mp4','.wav','.aiff','.ogg']:
            obj, created = Audio.objects.get_or_create(
                                original_filename=file.name,
                                file=file,
                                folder=folder,
                                is_public=False)
        else:
            obj = None

        if obj:
            print 'have object'
            return obj
        else:
            return None






    def walker(self):
        
        if(self.object_type == 'releases'):
            
            lrs = Releases.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:100000]
        
        
            for lr in lrs:
                print
                print '----------------------------------------'
                print 'got release:',
                print u'%s' % lr.name.encode('ascii', 'replace')
                
                try:
                    self.import_release(lr)
                except Exception, e:
                    print e
                    pass
                
                #print lr.id
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
