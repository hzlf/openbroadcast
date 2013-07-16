import os
import string
import unicodedata
import pprint
import re
import time

import locale
import acoustid
import requests

from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag
from alibrary.models import Relation, Release, Artist, Media, Label, MediaExtraartists, Profession, ArtistMembership


from lib.util import filer_extra

from alibrary.util import lookup

from settings import MEDIA_ROOT

import musicbrainzngs
import discogs_client as discogs

import shutil


from base import discogs_image_by_url, discogs_id_by_url

import logging
log = logging.getLogger(__name__)


MUSICBRAINZ_HOST = getattr(settings, 'MUSICBRAINZ_HOST', None)
MUSICBRAINZ_RATE_LIMIT = getattr(settings, 'MUSICBRAINZ_RATE_LIMIT', True)

# promt for continuation
DEBUG_WAIT = False


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
        log = logging.getLogger('util.importer.__init__')

        musicbrainzngs.set_useragent("NRG Processor", "0.01", "http://anorg.net/")
        musicbrainzngs.set_rate_limit(MUSICBRAINZ_RATE_LIMIT)
        
        if MUSICBRAINZ_HOST:
            musicbrainzngs.set_hostname(MUSICBRAINZ_HOST)
            
        self.pp = pprint.PrettyPrinter(indent=4)
        
        self.pp.pprint = lambda d: None
        
        
        self.mb_completed = []
        
        
    def run(self, obj):
        
        log = logging.getLogger('util.importer.run')
        it = obj.import_tag
        rt = obj.results_tag
        

        print '*****************************'
        self.pp.pprint(it)
        self.pp.pprint(rt)
        print '*****************************'
        
        
        """
        get import settings
        """
        
        # media
        name = None
        tracknumber = None
        filename = obj.filename
        alibrary_media_id = None
        mb_track_id = None
        
        if 'name' in it and it['name']:
            name = it['name']
        
        if 'media_tracknumber' in rt and rt['media_tracknumber']:
            tracknumber = rt['media_tracknumber']

        if 'alibrary_media_id' in it and it['alibrary_media_id']:
            alibrary_media_id = it['alibrary_media_id']
        
        if 'mb_track_id' in it and it['mb_track_id']:
            mb_track_id = it['mb_track_id']
        
        # release
        release = None
        alibrary_release_id = None
        mb_release_id = None
        force_release = False
        
        if 'release' in it and it['release']:
            release = it['release']
        
        if 'alibrary_release_id' in it and it['alibrary_release_id']:
            alibrary_release_id = it['alibrary_release_id']
        
        if 'mb_release_id' in it and it['mb_release_id']:
            mb_release_id = it['mb_release_id']
        
        if 'force_release' in it and it['force_release']:
            force_release = it['force_release']
        
        # artist
        artist = None
        alibrary_artist_id = None
        mb_artist_id = None
        force_artist = False
        
        if 'artist' in it and it['artist']:
            artist = it['artist']
        
        if 'alibrary_artist_id' in it and it['alibrary_artist_id']:
            alibrary_artist_id = it['alibrary_artist_id']
        
        if 'mb_artist_id' in it and it['mb_artist_id']:
            mb_artist_id = it['mb_artist_id']
        
        if 'force_artist' in it and it['force_artist']:
            force_artist = it['force_artist']
            

        # label
        label = None
        alibrary_label_id = None
        mb_label_id = None
        force_label = False
        
        if 'label' in it and it['label']:
            label = it['label']
        
        if 'alibrary_label_id' in it and it['alibrary_label_id']:
            alibrary_label_id = it['alibrary_label_id']
        
        if 'mb_label_id' in it and it['mb_label_id']:
            mb_label_id = it['mb_label_id']
        
        if 'force_label' in it and it['force_label']:
            force_label = it['force_label']
            

            
        
        print
        print '***************************************************************'
        print '*   import settings                                           *'
        print '***************************************************************'
        print
        print '* media *******************************************************'
        print
        print '  name:                 %s' % name
        print '  tracknumber:          %s' % tracknumber
        print '  filename:             %s' % filename
        print '  alibrary_media_id:    %s' % alibrary_media_id
        print '  mb_track_id:          %s' % mb_track_id
        print
        print '* release *****************************************************'
        print
        print '  release:              %s' % release
        print '  alibrary_release_id:  %s' % alibrary_release_id
        print '  mb_release_id:        %s' % mb_release_id
        print '  force_release:        %s' % force_release
        print
        print '* artist *****************************************************'
        print
        print '  artist:              %s' % artist
        print '  alibrary_artist_id:  %s' % alibrary_artist_id
        print '  mb_artist_id:        %s' % mb_artist_id
        print '  force_artist:        %s' % force_artist
        print
        print '* label *****************************************************'
        print
        print '  label:              %s' % label
        print '  alibrary_label_id:  %s' % alibrary_label_id
        print '  mb_label_id:        %s' % mb_label_id
        print '  force_label:        %s' % force_label
        print
        print '***************************************************************'
        
        
        time.sleep(1)

        if DEBUG_WAIT:
            raw_input("Press Enter to continue...")
        
        
        """
        create media
        always executed, as duplicates are handled before this step
        """        
        m = None
        m_created = False
        log.info('media, force creation: %s' % name)
        m = Media(name=name)
        m.filename = filename
        if tracknumber:
            m.tracknumber = tracknumber
        m.save()
        m_created = True
        
        """
        get or create release
        get release by:
         - mb_id
         - internal_id
         - or force creation
        """
        
        
        """
        Section to search / create / lookup release information
        """
        
        r = None
        r_created = False 
        
        # look in imports importitems if release is already here
        # (case where same item is 'forced' several times - so we have to avoid recreation)
        try:
            ctype = ContentType.objects.get(app_label="alibrary", model="release")
            ii_ids = obj.import_session.get_importitem_ids(ctype)
            print 'ii_ids: '
            print ii_ids
            ir = Release.objects.filter(pk__in=ii_ids, name=release)
            #print ir
            #log.info('found release in import session: %s' % ir)
        except:
            ir = None
        
        if ir and ir.count > 0:
            r = ir[0]
        
        
        # create release if forced
        if force_release and not r:
            log.info('release, force creation: %s' % release)

            r = Release(name=release)
            r.save()
            r_created = True
            
            
        # try to get release by alibrary_id
        if alibrary_release_id and not r:
            log.debug('release, lookup by alibrary_release_id: %s' % alibrary_release_id)
            try:
                r = Release.objects.get(pk=alibrary_release_id)
                log.debug('got release: %s by alibrary_release_id: %s' % (r.pk, alibrary_release_id))
            except Exception, e:
                # print e
                log.debug('could not get release by alibrary_release_id: %s' % alibrary_release_id)
            
            
        # try to get release by mb_id
        if mb_release_id and not r:
            log.debug('release, lookup by mb_release_id: %s' % mb_release_id)
            try:
                lrs = lookup.release_by_mb_id(mb_release_id)
                r = lrs[0]
                log.debug('got release: %s by mb_release_id: %s' % (r.pk, mb_release_id))
            except Exception, e:
                # print e
                log.debug('could not get release by mb_release_id: %s' % mb_release_id)
                

        # no luck yet, so create the release
        if not r:
            log.info('no release yet, so create it: %s' % release)
            r = Release(name=release)
            r.save()
            r_created = True
                 
            
            
            
        # attach item to current import
        if r:
            log.info('release here, add it to importitems: %s' % r)
            ii = obj.import_session.add_importitem(r)
            log.info('importitem created: %s' % ii)
            
            # assign
            m.release = r
        
        
        """
        Section to search / create / lookup artist information
        """
        
        a = None
        a_created = False 
        
        # look in imports importitems if artist is already here
        # (case where same item is 'forced' several times - so we have to avoid recreation)
        try:
            ctype = ContentType.objects.get(app_label="alibrary", model="artist")
            ii_ids = obj.import_session.get_importitem_ids(ctype)
            print 'ii_ids: '
            print ii_ids
            ia = Artist.objects.filter(pk__in=ii_ids, name=artist)
            #print ia
            #log.info('found artist in import session: %s' % ia)
        except:
            ia = None
        
        if ia and ia.count > 0:
            a = ia[0]
        
        
        # create artist if forced
        if force_artist and not a:
            log.info('artist, force creation: %s' % artist)

            a = Artist(name=artist)
            a.save()
            a_created = True
            
            
        # try to get artist by alibrary_id
        if alibrary_artist_id and not a:
            log.debug('artist, lookup by alibrary_artist_id: %s' % alibrary_artist_id)
            try:
                a = Artist.objects.get(pk=alibrary_artist_id)
                log.debug('got artist: %s by alibrary_artist_id: %s' % (a.pk, alibrary_artist_id))
            except Exception, e:
                # print e
                log.debug('could not get artist by alibrary_artist_id: %s' % alibrary_artist_id)
            
            
        # try to get artist by mb_id
        if mb_artist_id and not a:
            log.debug('artist, lookup by mb_artist_id: %s' % mb_artist_id)
            try:
                las = lookup.artist_by_mb_id(mb_artist_id)
                a = las[0]
                log.debug('got artist: %s by mb_artist_id: %s' % (a.pk, mb_artist_id))
            except Exception, e:
                # print e
                log.debug('could not get artist by mb_artist_id: %s' % mb_artist_id)
                

        # no luck yet, so create the artist
        if not a:
            log.info('no artist yet, so create it: %s' % artist)
            a = Artist(name=artist)
            a.save()
            a_created = True
                 
            
            
        # attach item to current import
        if a:
            log.info('artist here, add it to importitems: %s' % a)
            ii = obj.import_session.add_importitem(a)
            log.info('importitem created: %s' % ii)
            
            # assign
            m.artist = a
            
        
        
        
        
        # for debugging completeion, place here
        # m = self.mb_complete_media(m, mb_track_id)
                 
        # try to complete release metadata
        if r_created:
            log.info('release created, try to complete: %s' % r)
            r.creator = obj.import_session.user
            r = self.mb_complete_release(r, mb_release_id)
     
        # try to complete artist metadata
        if a_created:
            log.info('artist created, try to complete: %s' % a)
            a.creator = obj.import_session.user
            a = self.mb_complete_artist(a, mb_artist_id)
        

        
        # try to complete media metadata
        # comes after artist creation ,to prevent duplicates!
        if m_created:
            log.info('media created, try to complete: %s' % m)
            m.creator = obj.import_session.user
            m = self.mb_complete_media(m, mb_track_id, mb_release_id,  excludes=(mb_artist_id,))
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # save assignments
        m.save()
        
        obj.import_session.add_importitem(m)
        
        # add file
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
        
        
        
        
        return m, 1
    
    
    
    
    
    def mb_complete_media(self, obj, mb_id, mb_release_id, excludes=()):
        
        log = logging.getLogger('util.importer.mb_complete_media')
        log.info('complete media, m: %s | mb_id: %s' % (obj.name, mb_id))
        
        #raw_input("Press Enter to continue...")
        time.sleep(1.1)
        
        inc = ('artists', 'url-rels', 'aliases', 'tags', 'recording-rels', 'artist-rels', 'work-level-rels', 'artist-credits')
        url = 'http://%s/ws/2/recording/%s/?fmt=json&inc=%s' % (MUSICBRAINZ_HOST, mb_id, "+".join(inc))

        r = requests.get(url)
        result = r.json()

        print '*****************************************************************'
        print url
        print '*****************************************************************'

        # get release based information (to map track- and disc-number)
        inc = ('recordings',)
        url = 'http://%s/ws/2/release/%s/?fmt=json&inc=%s' % (MUSICBRAINZ_HOST, mb_release_id, "+".join(inc))

        r = requests.get(url)
        result_release = r.json()
        print '*****************************************************************'
        print url
        print '*****************************************************************'
        
        print(result)

        print

        print(result_release)


        print '*****************************************************************'

        if DEBUG_WAIT:
            raw_input("Press Enter to continue...")



        # loop release recordings, trying to get our track...
        if 'media' in result_release:
            disc_index = 0
            media_index = 0
            media_offset = 0
            for disc in result_release['media']:

                for m in disc['tracks']:

                    x_mb_id = m['recording']['id']
                    x_pos = m['number']

                    if x_mb_id == mb_id:
                        print 'id:  %s' % x_mb_id
                        print 'pos: %s' % x_pos
                        print 'disc_index: %s' % disc_index
                        print 'media_offset: %s' % media_offset
                        print 'final pos: %s' % (int(media_offset) + int(x_pos))

                        obj.tracknumber = (int(media_offset) + int(x_pos))
                        obj.mediamumber = int(disc_index)

                    media_index =+ 1

                disc_index += 1
                media_offset += int(disc['track-count'])











        if DEBUG_WAIT:
            raw_input("Press Enter to continue...")








        # self.pp.pprint(result)
        if 'relations' in result:
            for relation in result['relations']:
    
                
                # map artists
                if 'artist' in relation:
                    print 'artist: %s' % relation['artist']['name']
                    print 'mb_id:   %s' % relation['artist']['id']
                    print 'role:   %s' % relation['type']
                    print
                    time.sleep(0.1)
                    l_as = lookup.artist_by_mb_id(relation['artist']['id'])
                    l_a = None

                    
                    #if len(l_as) < 1 and relation['artist']['id'] not in self.mb_completed:
                    if len(l_as) < 1 and relation['artist']['id'] not in excludes:
                        self.mb_completed.append(relation['artist']['id'])
                        l_a = Artist(name=relation['artist']['name'])
                        l_a.save()
                            
                        url = 'http://musicbrainz.org/artist/%s' % relation['artist']['id']
                        print 'musicbrainz_url: %s' % url
                        rel = Relation(content_object=l_a, url=url)
                        rel.save()
                        
                        print 'artist created'
                    if len(l_as) == 1:
                        print 'got artist!'
                        l_a = l_as[0]
                        print l_as[0]
                        
                    profession = None
                    if 'type' in relation:
                        profession, created = Profession.objects.get_or_create(name=relation['type'])
                        
                        
                    """"""
                    if l_a:
                        mea, created = MediaExtraartists.objects.get_or_create(artist=l_a, media=obj, profession=profession)
                        l_a = self.mb_complete_artist(l_a, relation['artist']['id'])
                    #self.pp.pprint(relation['artist']['name'])
                    
        tags = result.get('tags', ())
        for tag in tags:
            log.debug('got tag: %s' % (tag['name']))
            Tag.objects.add_tag(obj, '"%s"' % tag['name'])
            

                    
        # add mb relation
        mb_url = 'http://musicbrainz.org/recording/%s' % (mb_id)
        try:
            rel = Relation.objects.get(object_id=obj.pk, url=mb_url)
        except:
            log.debug('relation not here yet, add it: %s' % (mb_url))
            rel = Relation(content_object=obj, url=mb_url)
            rel.save()
        
        
        return obj
    
    
    
    def mb_complete_release(self, obj, mb_id):
        
        log = logging.getLogger('util.importer.mb_complete_release')
        log.info('complete release, r: %s | mb_id: %s' % (obj.name, mb_id))
        
        inc = ('artists', 'url-rels', 'aliases', 'tags', 'recording-rels', 'work-rels', 'work-level-rels', 'artist-credits', 'labels', 'label-rels', 'release-groups')
        url = 'http://%s/ws/2/release/%s/?fmt=json&inc=%s' % (MUSICBRAINZ_HOST, mb_id, "+".join(inc))
        
        r = requests.get(url)
        result = r.json()
        
        self.pp.pprint(result)
        
        rg_id = None
        release_group = result.get('release-group', None)
        if release_group:
            rg_id = release_group.get('id', None)
            
        log.debug('release-group id: %s' % rg_id)
        
        discogs_url = None
        discogs_master_url = None
        discogs_image = None
        # try to get relations
        if 'relations' in result:
            for relation in result['relations']:
                
                if relation['type'] == 'discogs':
                    log.debug('got discogs url for release: %s' % relation['url'])
                    discogs_url = relation['url']
                    
                    # obj.save()
                    
                if relation['type'] == 'purchase for download':
                    log.debug('got purchase url for release: %s' % relation['url'])

                    try:
                        rel = Relation.objects.get(object_id=obj.pk, url=relation['url'])
                    except:
                        rel = Relation(content_object=obj, url=relation['url'])
                        rel.save()
                        
        

            
        if rg_id:
            # try to get discogs master url
            inc = ('url-rels',)
            url = 'http://%s/ws/2/release-group/%s/?fmt=json&inc=%s' % (MUSICBRAINZ_HOST, rg_id, "+".join(inc))
            
            r = requests.get(url)
            rg_result = r.json()
            
            print "*******************************************************************"
            self.pp.pprint(rg_result)

            # try to get relations from master
            if 'relations' in rg_result:
                for relation in rg_result['relations']:
                    
                    if relation['type'] == 'discogs':
                        log.debug('got discogs master-url for release: %s' % relation['url'])
                        discogs_master_url = relation['url']

                        
                    if relation['type'] == 'wikipedia':
                        log.debug('got wikipedia url for release: %s' % relation['url'])
    
                        try:
                            rel = Relation.objects.get(object_id=obj.pk, url=relation['url'])
                        except:
                            rel = Relation(content_object=obj, url=relation['url'])
                            rel.save()

                        
                    if relation['type'] == 'lyrics':
                        log.debug('got lyrics url for release: %s' % relation['url'])
    
                        try:
                            rel = Relation.objects.get(object_id=obj.pk, url=relation['url'])
                        except:
                            rel = Relation(content_object=obj, url=relation['url'])
                            rel.save()

                        
                    if relation['type'] == 'allmusic':
                        log.debug('got allmusic url for release: %s' % relation['url'])
    
                        try:
                            rel = Relation.objects.get(object_id=obj.pk, url=relation['url'])
                        except:
                            rel = Relation(content_object=obj, url=relation['url'])
                            rel.save()

                        
                    if relation['type'] == 'review':
                        log.debug('got review url for release: %s' % relation['url'])
    
                        try:
                            rel = Relation.objects.get(object_id=obj.pk, url=relation['url'])
                        except:
                            rel = Relation(content_object=obj, url=relation['url'])
                            rel.save()
        
        
        if discogs_url:
            
            try:
                rel = Relation.objects.get(object_id=obj.pk, url=discogs_url)
            except:
                rel = Relation(content_object=obj, url=discogs_url)
                rel.save()
                
            # try to get image
            try:
                discogs_image = discogs_image_by_url(discogs_url, 'resource_url')
                log.debug('discogs image located at: %s' % discogs_image)
            except:
                pass
            
        if discogs_master_url:
            
            try:
                rel = Relation.objects.get(object_id=obj.pk, url=discogs_master_url)
            except:
                rel = Relation(content_object=obj, url=discogs_master_url)
                rel.save()
                
            # try to get image from master
            if not discogs_image:
                try:
                    discogs_image = discogs_image_by_url(discogs_master_url, 'resource_url')
                    log.debug('discogs image located at: %s' % discogs_master_url)
                except:
                    pass
            
            
            
        # try to load & assign image
        if discogs_image:
            try:
                img = filer_extra.url_to_file(discogs_image, obj.folder)
                obj.main_image = img
                obj.save()
            except:
                log.info('unable to assign discogs image')
                
        else:
            # try at coverartarchive...
            url = 'http://coverartarchive.org/release/%s' % mb_id
            try:    
                r = requests.get(url)
                ca_result = r.json()
                ca_url = ca_result['images'][0]['image']
                img = filer_extra.url_to_file(ca_url, obj.folder)
                obj.main_image = img
                obj.save()
            except:
                pass
            
            
        # try to get some additional information from discogs
        if discogs_url:
            discogs_id = None
            try:
                discogs_id = re.findall(r'\d+', discogs_url)[0]
                log.info('extracted discogs id: %s' % discogs_id)
            except:
                pass
            
            if discogs_id:
                url = 'http://api.discogs.com/releases/%s' % discogs_id
                r = requests.get(url)
                dgs_result = r.json()
                    
                styles = dgs_result.get('styles', None)
                for style in styles:
                    log.debug('got style: %s' % (style))
                    Tag.objects.add_tag(obj, '"%s"' % style)
                    
                genres = dgs_result.get('genres', None)
                for genre in genres:
                    log.debug('got genre: %s' % (genre))
                    Tag.objects.add_tag(obj, '"%s"' % genre)
                    
                notes = dgs_result.get('notes', None)
                if notes:
                    obj.description = notes
                    
        if discogs_master_url:
            discogs_id = None
            try:
                discogs_id = re.findall(r'\d+', discogs_master_url)[0]
                log.info('extracted discogs id: %s' % discogs_id)
            except:
                pass
            
            if discogs_id:
                url = 'http://api.discogs.com/masters/%s' % discogs_id
                r = requests.get(url)
                dgs_result = r.json()
                    
                styles = dgs_result.get('styles', None)
                for style in styles:
                    log.debug('got style: %s' % (style))
                    Tag.objects.add_tag(obj, '"%s"' % style)
                    
                genres = dgs_result.get('genres', None)
                for genre in genres:
                    log.debug('got genre: %s' % (genre))
                    Tag.objects.add_tag(obj, '"%s"' % genre)
                    
                notes = dgs_result.get('notes', None)
                if notes:
                    obj.description = notes
                

                    
        tags = result.get('tags', ())
        for tag in tags:
            log.debug('got tag: %s' % (tag['name']))
            Tag.objects.add_tag(obj, '"%s"' % tag['name'])
            
        status = result.get('status', None)
        if status:
            log.debug('got status: %s' % (status))
            obj.releasestatus = status
            
        country = result.get('country', None)
        if country:
            log.debug('got country: %s' % (country))
            obj.release_country = country
            
        date = result.get('date', None)
        if date:
            log.debug('got date: %s' % (date))
            # TODO: rework field
            if len(date) == 4:
                date = '%s-00-00' % (date)
            elif len(date) == 7:
                date = '%s-00' % (date)
            elif len(date) == 10:
                date = '%s' % (date)
                
            re_date = re.compile('^\d{4}-\d{2}-\d{2}$')
            if re_date.match(date) and date != '0000-00-00':
                obj.releasedate_approx = '%s' % date
            
            
        asin = result.get('asin', None)
        if asin:
            log.debug('got asin: %s' % (asin))
            obj.asin = asin
            
        barcode = result.get('barcode', None)
        if barcode:
            log.debug('got barcode: %s' % (barcode))
            # obj.barcode = barcode
            
                    
        # add mb relation
        mb_url = 'http://musicbrainz.org/release/%s' % (mb_id)
        try:
            rel = Relation.objects.get(object_id=obj.pk, url=mb_url)
        except:
            log.debug('relation not here yet, add it: %s' % (mb_url))
            rel = Relation(content_object=obj, url=mb_url)
            rel.save()

        obj.save()
        
        
        return obj
    
    
    def mb_complete_artist(self, obj, mb_id):
        
        log = logging.getLogger('util.importer.mb_complete_artist')
        log.info('complete artist, a: %s | mb_id: %s' % (obj.name, mb_id))
        
        self.mb_completed.append(mb_id)
        
        inc = ('url-rels', 'tags')
        url = 'http://%s/ws/2/artist/%s/?fmt=json&inc=%s' % (MUSICBRAINZ_HOST, mb_id, "+".join(inc))
        
        r = requests.get(url)
        result = r.json()
        
        
        
        print '#########################################################################'
        self.pp.pprint(result)
        
        
        discogs_url = None
        discogs_image = None
        
        valid_relations = ('wikipedia', 'allmusic', 'BBC Music page', 'social network', 'official homepage', 'youtube', 'myspace',)
        
        relations = result.get('relations', ())

        for relation in relations:
            
            if relation['type'] == 'discogs':
                log.debug('got discogs url for artist: %s' % relation['url'])
                discogs_url = relation['url']
                
            if relation['type'] in valid_relations:
                log.debug('got %s url for artist: %s' % (relation['type'], relation['url']))
                

                try:
                    rel = Relation.objects.get(object_id=obj.pk, url=relation['url'])
                except:
                    rel = Relation(content_object=obj, url=relation['url'])
                    
                    if relation['type'] == 'official homepage':
                        rel.service = 'official'
                    
                    rel.save()

            
            
            
        if discogs_url:
            
            try:
                rel = Relation.objects.get(object_id=obj.pk, url=discogs_url)
            except:
                rel = Relation(content_object=obj, url=discogs_url)
                rel.save()
                
            # try to get image
            try:
                discogs_image = discogs_image_by_url(discogs_url, 'resource_url')
                log.debug('discogs image located at: %s' % discogs_image)
            except:
                pass
            
            
        # try to load & assign image
        if discogs_image:
            try:
                img = filer_extra.url_to_file(discogs_image, obj.folder)
                obj.main_image = img
                obj.save()
            except:
                log.info('unable to assign discogs image')
                
                
        if discogs_url:

            discogs_id = None
            try:
                # TODO: not sure if always working
                discogs_id = discogs_id_by_url(discogs_url)
                log.info('extracted discogs id: %s' % discogs_id)
            except:
                pass
            
            if discogs_id:
                url = 'http://api.discogs.com/artists/%s' % discogs_id
                r = requests.get(url)
                dgs_result = r.json()
                
                self.pp.pprint(dgs_result)
  
                """                  
                styles = dgs_result.get('styles', ())
                for style in styles:
                    log.debug('got style: %s' % (style))
                    Tag.objects.add_tag(obj, '"%s"' % style)
                """ 
                profile = dgs_result.get('profile', None)
                if profile:
                    obj.biography = profile
                    
                realname = dgs_result.get('realname', None)
                if realname:
                    obj.real_name = realname
                    
                """
                verry hackish part here, just as proof-of-concept
                """
                aliases = dgs_result.get('aliases', ())
                for alias in aliases:
                    try:
                        log.debug('got alias: %s' % alias['name'])
                        # TODO: improve! handle duplicates!
                        time.sleep(1.1)
                        r = requests.get(alias['resource_url'])
                        aa_result = r.json()
                        aa_discogs_url = aa_result.get('uri', None)
                        aa_name = aa_result.get('name', None)
                        aa_profile = aa_result.get('profile', None)
                        if aa_discogs_url and aa_name:
                            
                            l_as = lookup.artist_by_relation_url(aa_discogs_url)
                            l_a = None
                                
                            if len(l_as) < 1:
                                l_a = Artist(name=aa_name, biography=aa_profile)
                                l_a.save()
    
                                rel = Relation(content_object=l_a, url=aa_discogs_url)
                                rel.save()
                                
                            if len(l_as) == 1:
                                l_a = l_as[0]
                                print l_as[0]
                                
                            if l_a:
                                obj.aliases.add(l_a)
                    except:
                        pass
                    
                """
                verry hackish part here, just as proof-of-concept
                """
                members = dgs_result.get('members', ())
                for member in members:
                    try:
                        log.debug('got member: %s' % member['name'])
                        # TODO: improve! handle duplicates!
                        time.sleep(1.1)
                        r = requests.get(member['resource_url'])
                        ma_result = r.json()
                        ma_discogs_url = ma_result.get('uri', None)
                        ma_name = ma_result.get('name', None)
                        ma_profile = ma_result.get('profile', None)
                        if ma_discogs_url and ma_name:
                            
                            l_as = lookup.artist_by_relation_url(ma_discogs_url)
                            l_a = None
                                
                            if len(l_as) < 1:
                                l_a = Artist(name=ma_name, biography=ma_profile)
                                l_a.save()
    
                                rel = Relation(content_object=l_a, url=ma_discogs_url)
                                rel.save()
                                
                            if len(l_as) == 1:
                                l_a = l_as[0]
                                print l_as[0]
                                
                            if l_a:                                
                                ma = ArtistMembership.objects.get_or_create(parent=obj, child=l_a)
                                
                    except:
                        pass
                        
                
            
        type = result.get('type', None)
        if type:
            log.debug('got type: %s' % (type))
            obj.type = type
            
        disambiguation = result.get('disambiguation', None)
        if disambiguation:
            log.debug('got disambiguation: %s' % (disambiguation))
            obj.disambiguation = disambiguation
                    
        tags = result.get('tags', ())

        for tag in tags:
            log.debug('got tag: %s' % (tag['name']))
            Tag.objects.add_tag(obj, '"%s"' % tag['name'])
            
                    
        # add mb relation
        mb_url = 'http://musicbrainz.org/artist/%s' % (mb_id)
        try:
            rel = Relation.objects.get(object_id=obj.pk, url=mb_url)
        except:
            log.debug('relation not here yet, add it: %s' % (mb_url))
            rel = Relation(content_object=obj, url=mb_url)
            rel.save()
        
        obj.save()
        
        
        return obj
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
    def complete_import_tag(self, obj):
        log = logging.getLogger('util.importer.complete_import_tag')
        
        
        import_tag = obj.import_tag
        results_musicbrainz = obj.results_musicbrainz
        
        
        """
        Apply musicbrainz tags if unique
        """
        
        if len(results_musicbrainz) > 0:
            log.debug('got musicbrainz result -> apply it')
            mb = results_musicbrainz[0]
            
            
            # media
            if not 'name' in import_tag or not import_tag['name']:
                import_tag['name'] = mb['media']['name']
                
            if not 'mb_track_id' in import_tag or not import_tag['mb_track_id']:
                import_tag['mb_track_id'] = mb['media']['mb_id']
            
            
            # release
            if not 'release' in import_tag or not import_tag['release']:
                import_tag['release'] = mb['name']
                
            if not 'mb_release_id' in import_tag or not import_tag['mb_release_id']:
                import_tag['mb_release_id'] = mb['mb_id']
            
            # artist
            if not 'artist' in import_tag or not import_tag['artist']:
                import_tag['artist'] = mb['artist']['name']
                
            if not 'mb_artist_id' in import_tag or not import_tag['mb_artist_id']:
                import_tag['mb_artist_id'] = mb['artist']['mb_id']

            
        
        
        
        if 'artist' in import_tag:
            a = Artist.objects.filter(name=import_tag['artist'])
            print a
            #if a.count() == 1:
            if a.count() > 0:
                print a[0].get_api_url()
                import_tag['alibrary_artist_id'] = a[0].pk
                import_tag['alibrary_artist_resource_uri'] = a[0].get_api_url()
        else:
            print 'no artist name in tag'
        
        if 'release' in import_tag:
            r = Release.objects.filter(name=import_tag['release'])
            print r
            #if r.count() == 1:
            if r.count() > 0:
                print r[0].get_api_url()
                import_tag['alibrary_release_id'] = r[0].pk
                import_tag['alibrary_release_resource_uri'] = r[0].get_api_url()
        else:
            print 'no release name in tag'
        
        
        return import_tag
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    def run__(self, obj):
        
        log = logging.getLogger('util.importer.run')
        
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
                    #print '*******************'
                    #print t['recording']['id']
                    #print t['number']
                    
                    if t['recording']['id'] == it['mb_track_id']:
                        #print 'NUMBER ASSIGNED!!! %s' % t['number']
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        