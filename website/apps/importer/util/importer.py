from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

from django.conf import settings

import os
import string
import unicodedata

import locale
import acoustid
import requests

from alibrary.models import Relation, Release, Artist, Media, Label

from lib.util import filer_extra

from alibrary.util import lookup

from settings import MEDIA_ROOT

import musicbrainzngs
import discogs_client as discogs

import shutil


from base import discogs_image_by_url 

import logging
log = logging.getLogger(__name__)


MUSICBRAINZ_HOST = getattr(settings, 'MUSICBRAINZ_HOST', None)
MUSICBRAINZ_RATE_LIMIT = getattr(settings, 'MUSICBRAINZ_RATE_LIMIT', True)

def clean_filename(filename):
    import unicodedata
    import string
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    cleaned = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleaned if c in valid_chars)

def masterpath_by_uuid(instance, filename):
    filename, extension = os.path.splitext(filename)
    folder = "private/%s/" % (instance.uuid.replace('-', '/'))
    filename = u'master'
    return os.path.join(folder, "%s%s" % (clean_filename(filename).lower(), extension.lower()))


class Importer(object):


    def __init__(self):
        log = logging.getLogger('util.importer.Importer.__init__')

        musicbrainzngs.set_useragent("NRG Processor", "0.01", "http://anorg.net/")
        musicbrainzngs.set_rate_limit(MUSICBRAINZ_RATE_LIMIT)
        
        if MUSICBRAINZ_HOST:
            musicbrainzngs.set_hostname(MUSICBRAINZ_HOST)
        

    def run(self, obj):
        
        log = logging.getLogger('util.importer.Importer.run')
        
        # map
        it = obj.import_tag
        
        print '*****************************'
        print it
        print '*****************************'
        
        if 'mb_track_id' in it:
            log.info('mb_track_id: %s' % (it['mb_track_id']))

        m = Media(name=it['name'])

        # get/create release
        
        # lookup by mb_id
        r = None
        if 'mb_release_id' in it:
            lrs = lookup.release_by_mb_id(it['mb_release_id'])
            #print 'LRS!:'
            #print lrs
            if lrs.count() > 0:
                r = lrs[0]
            
        if not r:
            r, created = Release.objects.get_or_create(name=it['release'])
            # assign mb_relation
            if 'mb_release_id' in it:
                url = 'http://musicbrainz.org/release/%s' % it['mb_release_id']
                print 'musicbrainz_url: %s' % url
                rel = Relation(content_object=r, url=url)
                rel.save()
                
                # complete medatata
                self.complete_release_meta(r, it)
        
        try:
            if r:
                m.release = r 
                
        except Exception, e:
            print e
        
        
        # TODO: move
        if m.release and 'mb_release_id' in it:
            print 'Trying to get tracknumber'
            includes = ["recordings",]
            mb_result = musicbrainzngs.get_release_by_id(id=it['mb_release_id'], includes=includes)
            
            tnumber = None
            
            try:
                for t in mb_result['release']['medium-list'][0]['track-list']:
                    print '*******************'
                    print t['recording']['id']
                    print t['number']
                    
                    if t['recording']['id'] == it['mb_track_id']:
                        print 'NUMBER ASSIGNED!!! %s' % t['number']
                        m.tracknumber = int(t['number'])
                    
            except Exception, e:
                print e
                
            
        
        
        
        
        # get/create artist
        a, created = Artist.objects.get_or_create(name=it['artist'])
        try:
            if a:
                m.artist = a 
        except Exception, e:
            print e
        

        m.status = 1
        m.save()

        status = 1

        folder = "private/%s/" % (m.uuid.replace('-', '/'))
        src = obj.file.path
        filename, extension = os.path.splitext(obj.file.path)
        dst = os.path.join(folder, "master%s" % extension.lower())
        try:
            os.makedirs("%s/%s" % (MEDIA_ROOT, folder))
            shutil.copy(src, "%s/%s" % (MEDIA_ROOT, dst))
            m.master = dst
            
            m.save()
            
        except Exception, e:
            print e
        
        return m, status
    
    def complete_release_meta(self, r, it):
        includes = [
        "artists", "labels", "recordings", "release-groups", "media",
        "artist-credits", "discids", "puids", "isrcs",
        "artist-rels", "label-rels", "recording-rels", "release-rels",
        "release-group-rels", "url-rels", "work-rels", "recording-level-rels",
        "work-level-rels"
        ]
        mb_release = musicbrainzngs.get_release_by_id(id=it['mb_release_id'], includes=includes)

        mbr = mb_release['release']
            
        print '***************************************'
            
        if 'status' in mbr:
            print mbr['status']
            
        if 'title' in mbr:
            print mbr['title']
        
        if 'url-relation-list' in mbr:
            # print mbr['url-relation-list']
            
            for rel in mbr['url-relation-list']:
                print rel
                if rel['type'] == 'discogs':
                    print 'DISCOGS: %s' % rel['target']

                    try:
                        # pass
                        rel = Relation(content_object=r, url=rel['target'])
                        rel.save()
                    except Exception, e:
                        print 'RELATION EXCEPTION'
                        print e
                        
                    try:
                        discogs_image = discogs_image_by_url(rel['target'])
                        img = filer_extra.url_to_file(discogs_image, r.folder)
                        r.main_image = img
                    except:
                        pass
        r.save()
        
        print '***************************************'
        
        
        
        
        
        
        
        
        
        return mb_release
        
        
        
        
    def complete_import_tag(self, import_tag):
        
        print import_tag
        
        if 'artist' in import_tag:
            a = Artist.objects.filter(name=import_tag['artist'])
            print a
            if a.count() == 1:
                print a[0].get_api_url()
                import_tag['alibrary_artist_id'] = a[0].pk
                import_tag['alibrary_artist_resource_uri'] = a[0].get_api_url()
        else:
            print 'no artist name in tag'
        
        if 'release' in import_tag:
            r = Release.objects.filter(name=import_tag['release'])
            print r
            if r.count() == 1:
                print r[0].get_api_url()
                import_tag['alibrary_release_id'] = r[0].pk
                import_tag['alibrary_release_resource_uri'] = r[0].get_api_url()
        else:
            print 'no release name in tag'
        
        
        return import_tag
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        