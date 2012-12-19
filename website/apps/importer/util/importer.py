from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

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
        musicbrainzngs.set_hostname("172.16.82.130:5000")
        musicbrainzngs.set_rate_limit(False)
        

    def run(self, obj):
        
        log = logging.getLogger('util.importer.Importer.run')
        
        # map
        it = obj.import_tag
        
        log.info('mb_track_id: %s' % (it['mb_track_id']))

        m = Media(name=it['name'])

        # get/create release
        
        # lookup by mb_id
        r = None
        if it['mb_release_id']:
            lrs = lookup.release_by_mb_id(it['mb_release_id'])
            print 'LRS!:'
            print lrs
            if lrs.count() > 0:
                r = lrs[0]
            
        if not r:
            r, created = Release.objects.get_or_create(name=it['release'])
            # assign mb_relation
            if it['mb_release_id']:
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
                        pass
                        #rel = Relation(content_object=r, url=rel['target'])
                        #rel.save()
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        