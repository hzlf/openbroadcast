import os
import re
import locale
import pprint
import logging

from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from django.conf import settings
import acoustid
import requests

import musicbrainzngs
from lib.util import pesterfish
from lib.util.sha1 import sha1_by_file
from base import discogs_image_by_url

log = logging.getLogger(__name__)


AC_API_KEY = getattr(settings, 'AC_API_KEY', 'ZHKcJyyV')
MUSICBRAINZ_HOST = getattr(settings, 'MUSICBRAINZ_HOST', None)
MUSICBRAINZ_RATE_LIMIT = getattr(settings, 'MUSICBRAINZ_RATE_LIMIT', True)


METADATA_SET = {
                # media
                'obp_media_uuid': None,
                'media_name': None,
                'media_mb_id': None,
                'media_tracknumber': None,
                'media_totaltracks': None,
                # artist
                'artist_name': None,
                'artist_mb_id': None,
                'performer_name': None,
                # release
                'release_name': None,
                'release_mb_id': None,
                'release_date': None,
                'release_releasecountry': None,
                'release_catalognumber': None,
                'release_type': None,
                'release_status': None,
                # label
                'label_name': None,
                'label_mb_id': None,
                'label_code': None,
                # disc
                'disc_number': None,
                # media mixed
                'media_genres' : [],
                'media_tags' : [],
                'media_copyright': None,
                'media_comment': None,
                'media_bpm': None,
                }

class Process(object):


    def __init__(self):
        log = logging.getLogger('util.process.Process.__init__')

        musicbrainzngs.set_useragent("NRG Processor", "0.01", "http://anorg.net/")
        musicbrainzngs.set_rate_limit(MUSICBRAINZ_RATE_LIMIT)
        
        self.pp = pprint.PrettyPrinter(indent=4)
        self.pp.pprint = lambda d: None
        
        if MUSICBRAINZ_HOST:
            musicbrainzngs.set_hostname(MUSICBRAINZ_HOST)
    
    """
    look for a duplicate by sha1
    """
    def id_by_sha1(self, file):
        sha1 = sha1_by_file(file)
        print 'SHA1: %s' % sha1
        try:
            from alibrary.models import Media
            return Media.objects.filter(master_sha1=sha1)[0].pk
        except Exception, e:
            print "SHA1 EXCEPTION:"
            print e
            return None
    
    """
    look for a duplicate by fingerprint
    """
    def id_by_echoprint(self, file):

        log = logging.getLogger()

        from ep.API import fp
        from lib.analyzer.echoprint import Echoprint
        e = Echoprint()
        code, version, duration, echoprint = e.echoprint_from_path(file.path, offset=10, duration=100)

        try:
            res = fp.best_match_for_query(code_string=code)

            if res.match():
                log.info('echoprint match - score: %s trid: %s' % (res.score, res.TRID))
                #print res.message()
                #print res.match()
                #print res.score
                #print res.TRID
                return int(res.TRID)
            
        except Exception, e:
            log.warning('echoprint error: %s' % (e))


        return None
    
    
    def extract_metadata(self, file):
        

        log = logging.getLogger('importer.process.extract_metadata')
        log.info('Extracting metadata for: %s' % (file.path))
        
        enc = locale.getpreferredencoding()
        try:
            meta = EasyID3(file.path)
            log.debug('using EasyID3')
        except Exception, e:
            meta = MutagenFile(file.path)
            log.debug('using MutagenFile')

        
        dataset = dict(METADATA_SET)

        """
        Mapping
        """


        # try to get obp identifyer

        from mutagen.id3 import ID3
        id3 = ID3(file.path)
        print '//////////////////// META /////////////////////////'
        print id3
        print '//////////////////// META /////////////////////////'
        obp_media_uuid = id3["UFID:http://openbroadcast.ch"].data.decode('ascii')
        if obp_media_uuid:
            print '*****************************'
            print 'GOT OWN ID: %s' % obp_media_uuid
            print '*****************************'

            dataset['obp_media_uuid'] = obp_media_uuid



        
        # Media

        try:
            dataset['media_name'] = meta['title'][0]
        except Exception, e:
            log.info('metadata missing "media_name": %s' % (e))
            
        try:
            dataset['media_mb_id'] = meta['musicbrainz_trackid'][0]
        except Exception, e:
            log.debug('metadata missing "media_mb_id": %s' % (e))
            
        try:

            try:
                dataset['media_tracknumber'] = int(meta['tracknumber'][0])
            except Exception, e:
                log.debug('metadata missing "media_tracknumber": %s' % (e))
                
            try:
                tn = meta['tracknumber'][0].split('/')
                dataset['media_tracknumber'] = int(tn[0])
                dataset['media_totaltracks'] = int(tn[1])
            except Exception, e:
                pass
                #print e

        except Exception, e:
            print e
           
           
           
        # try to extract tracknumber from filename
        if 'media_tracknumber' in dataset and not dataset['media_tracknumber']:
            
            t_num = None
            
            path, filename = os.path.split(file.path)
            log.info('Looking for number in filename: %s' % filename)

            
            match = re.search("\A\d+", filename)
            
            try:
                if match:
                    t_num = int(match.group(0))
            except:
                pass
            
            dataset['media_tracknumber'] = t_num
           
            
        # Artist
        try:
            dataset['artist_name'] = meta['artist'][0]
        except Exception, e:
            print e
            
        try:
            dataset['artist_mb_id'] = meta['musicbrainz_artistid'][0]
        except Exception, e:
            print e
            
        try:
            dataset['performer_name'] = meta['performer'][0]
        except Exception, e:
            print e



        # Release
        try:
            dataset['release_name'] = meta['album'][0]
        except Exception, e:
            print e
            
        try:
            dataset['release_mb_id'] = meta['musicbrainz_albumid'][0]
        except Exception, e:
            print e
            
        try:
            dataset['release_date'] = meta['date'][0]
        except Exception, e:
            print e
            
        try:
            dataset['release_releasecountry'] = meta['releasecountry'][0]
        except Exception, e:
            print e
            
        try:
            dataset['release_status'] = meta['musicbrainz_albumstatus'][0]
        except Exception, e:
            print e
            
            
            
         # Label
        try:
            try:
                dataset['label_name'] = meta['organization'][0]
            except Exception, e:
                print e
                
            try:
                dataset['label_name'] = meta['label'][0]
            except Exception, e:
                pass
            
        except Exception, e:
            print e
            
        try:
            dataset['label_code'] = meta['labelno'][0]
        except Exception, e:
            pass
            
            
            
        # Misc
        try:
            dataset['media_copyright'] = meta['copyright'][0]
        except Exception, e:
            print e
            
        try:
            dataset['media_comment'] = meta['comment'][0]
        except Exception, e:
            pass
            
        try:
            dataset['media_bpm'] = meta['bpm'][0]
        except Exception, e:
            print e

        # debug
        if meta:
            for k in meta:
                m = meta[k]
                if k[0:13] != 'PRIV:TRAKTOR4':
                    pass        
                    #print "%s:   %s" % (k, m)



        """"""
        print
        print
        print "******************************************************************"
        print "* Aquired metadata"
        print "******************************************************************"
        for k in dataset:
            m = dataset[k]
            try:
                print "%s:   %s" % (k, m)
            except:
                # encoding problem.. don't care
                pass
        print "******************************************************************"
        print
        print

        
        return dataset
    
    """
    acoustid lookup
    returns musicbrainz "recording" ids
    """
    def get_aid(self, file):

        log = logging.getLogger('importer.process.get_aid')
        log.info('Lookup acoustid for: %s' % (file.path))

        data = acoustid.match(AC_API_KEY, file.path)

        print 'AID data:'
        print data
        print '---'
        
        res = []
        i = 0
        for d in data:
            selected = False
            if i == 0:
                selected = True
            t = {
                 'score': d[0],
                 'id': d[1],
                 'selected': selected,
                 }

            log.info('acoustid: got result - score: %s | mb id: %s' % (d[0], d[1]))
            if i < 5:
                res.append(t)
            i += 1

        return res

       
    def get_musicbrainz(self, obj):
        
        log = logging.getLogger('importer.process.get_musicbrainz')
        log.info('Lookup musicbrainz for importfile id: %s' % obj.pk)


        """
        trying to get the tracknumber
        """
        tracknumber = None
        releasedate = None
        
        """
        try loading settings
        """
        skip_tracknumber = obj.settings.get('skip_tracknumber', False)

        try:
            tracknumber = obj.results_tag['media_tracknumber']
            log.debug('Got tracknumber: %s' % tracknumber)
        except Exception, e:
            log.debug('Unable to get tracknumber') 
            
        try:
            releasedate = obj.results_tag['release_date']
            log.debug('Got releasedate: %s' % releasedate)
        except Exception, e:
            log.debug('Unable to get releasedate') 

        
        """
         - loop recording ids
         - query by it and tracknumber (if available)
         - sort releases by date
         
        release entry looks as following:
         
        {
            id: "12a0eabc-28ee-3ac6-834d-390861f0f20c",
            title: "Live!",
            status: "Official",
            release-group: {
                id: "90eb5951-1225-35bc-9ef0-0845ac3c81aa",
                primary-type: "Album",
                secondary-types: [
                    "Live"
                ]
            },
            date: "1995",
            country: "GB",
            track-count: 30,
            media: [
                {
                    position: 2,
                    format: "CD",
                    track: [
                        {
                            number: "3",
                            title: "Walking in Your Footsteps",
                            length: 295000
                        }
                    ],
                    track-count: 15,
                    track-offset: 2
                }
            ]
        }
        
        """
        releases = []
        for e in obj.results_acoustid:
            recording_id = e['id']
            print 'recording mb_id: %s' % recording_id
        
            """
            search query e.g.:
            http://www.musicbrainz.org/ws/2/recording/?query=rid:1e701b4e-2b6e-4509-af29-b8df2cdc8225%20AND%20number:3&fmt=json
            """
            
            url = 'http://%s/ws/2/recording/?fmt=json&query=rid:%s' % (MUSICBRAINZ_HOST, recording_id)
            
            if tracknumber and not skip_tracknumber:
                url = '%s%s%s' % (url, '%20AND%20number:', tracknumber)
            
            """    
            if releasedate:
                url = '%s%s%s' % (url, '%20AND%20date:', releasedate)
            """
            
            log.info('API url for request: %s' % url)
            r = requests.get(url)
            
            result = r.json()

            if 'recording' in result:
                print 'got recording: %s' % recording_id
                if len(result['recording']) > 0:
                    if 'releases' in result['recording'][0]:
                        
                        
                        """
                        fix missing dates
                        """
                        for r in result['recording'][0]['releases']:
                            # dummy-date - sorry, none comes first else.
                            if 'date' not in r:
                                r['date'] = '9999'
                                
                        
                        """
                        try to get the first one, by date
                        """
                        try:
                            sorted_releases = sorted(result['recording'][0]['releases'], key=lambda k: k['date'])
                            release = sorted_releases[0]
                            log.debug('Sorting OK!')
                            # reset dummy-date
                            if release['date'] == '9999':
                                release['date'] = None
                            log.debug('First Date: %s' % release['date'])
                        except Exception, e:
                            log.warning('Unable to sort by date: %s' % e)

                            
                            sorted_releases = result['recording'][0]['releases']
                            
                            
                        selected_releases = []
                        if len(sorted_releases) > 1:
                            
                            """
                            Append releases with unique names
                            """
                            count = 0
                            current_names = []
                            for t_rel in sorted_releases:
                                if not t_rel['title'] in current_names and count < 5:
                                    #print 'FRESH NAME: %s' % t_rel['title']
                                    current_names.append(t_rel['title'])
                                    selected_releases.append(t_rel)
                                    count += 1
                                #else:
                                    #print 'NAME ALREADY HERE: %s' % t_rel['title']
                                    
                            
                            """
                            if len(sorted_releases) > 3:
                                limit = 3
                            else:
                                limit = len(sorted_releases) 
                            for i in range(limit):
                                selected_releases.append(sorted_releases[i])
                            """ 
                                
                        else:
                            selected_releases.append(sorted_releases[0])
                            
                              
                              
                        for selected_release in selected_releases:
                            
                            selected_release['artist'] = result['recording'][0]['artist-credit'][0]['artist']
                            selected_release['recording'] = result['recording'][0]
                            try:
                                selected_release['recording']['releases'] = None
                            except Exception, e:
                                print e
                            
                            
                            if releasedate and 1 == 2:
                                print 'HAVE RELEASEDATE: %s' % releasedate
                                s_rd = releasedate[0:4]
                                t_rd = selected_release['date'][0:4]
                                
                                print 'dates: %s | %s' % (s_rd, t_rd)
                                
                                if s_rd == t_rd:
                                    releases.append(selected_release)
                                else:
                                    print 'DATE MISMATCH'
                            
                            else:
                                releases.append(selected_release)
                              
                
                        """
                        release['artist'] = result['recording'][0]['artist-credit'][0]['artist']
                        release['recording'] = result['recording'][0]
                        try:
                            release['recording']['releases'] = None
                        except Exception, e:
                            print e
                                                
                        releases.append(release)
                        
                        
                        if recording_id == '2b650c75-f24b-4988-be92-bde220277488':
                            print '###############################################'
                            self.pp.pprint(selected_release)
                            print '###############################################'
                        """

            
            

        print "PRE COMPLETE"
        releases = self.complete_releases(releases)
        print "POST COMPLETE"
        releases = self.format_releases(releases)

        
        self.pp.pprint(releases)
        
        return releases


        
        
    def complete_releases(self, releases):
        

        log = logging.getLogger('importer.process.complete_releases')
        log.info('Got %s releases to complete' % len(releases))
        
        completed_releases = []
        
        for release in releases:
            if release['id'] in completed_releases:
                log.debug('already completed release with id: %s' % release['id'])
                releases.remove(release)
                
            else:
                log.debug('complete release with id: %s' % release['id'])
                
                r_id = release['id']
                rg_id = release['release-group']['id']
                
                print 'r_id: %s' % r_id
                print 'rg_id: %s' % rg_id
                
                
                release['label'] = None
                release['catalog-number'] = None
                release['discogs_url'] = None
                release['discogs_master_url'] = None
                release['discogs_image'] = None
                
                
                """
                get release details
                """
                inc = ('labels', 'artists', 'url-rels', 'label-rels',)
                url = 'http://%s/ws/2/release/%s/?fmt=json&inc=%s' % (MUSICBRAINZ_HOST, r_id, "+".join(inc))
                
                r = requests.get(url)
                result = r.json()
                #self.pp.pprint(result)

                # only apply label info if unique
                if 'label-info' in result and len(result['label-info']) == 1:
                    if 'label' in result['label-info'][0]:
                        release['label'] = result['label-info'][0]['label']
                    if 'catalog-number' in result['label-info'][0]:
                        release['catalog-number'] = result['label-info'][0]['catalog-number']
                    
                # try to get discogs url
                if 'relations' in result:
                    for relation in result['relations']:
                        if relation['type'] == 'discogs':
                            log.debug('got discogs url from release: %s' % relation['url'])
                            release['discogs_url'] = relation['url']['resource']
                
                
                
                """
                get release-group details
                """
                inc = ('url-rels',)
                url = 'http://%s/ws/2/release-group/%s/?fmt=json&inc=%s' % (MUSICBRAINZ_HOST, rg_id, "+".join(inc))
                
                r = requests.get(url)
                result = r.json()
                #self.pp.pprint(result)
                    
                # try to get discogs master-url
                if 'relations' in result:
                    for relation in result['relations']:
                        if relation['type'] == 'discogs':
                            log.debug('got discogs url from release: %s' % relation['url'])
                            release['discogs_master_url'] = relation['url']['resource']
                        
                        
                        
                        
                """
                assign cover image (if available)
                """
                if release['discogs_url']:
                    try:
                        release['discogs_image'] = discogs_image_by_url(release['discogs_url'], 'uri150')
                    except:
                        pass
                    
                if not release['discogs_image']:
                    try:
                        release['discogs_image'] = discogs_image_by_url(release['discogs_master_url'], 'uri150')
                    except:
                        pass
                """
                finally try to get image from coverartarchive.org
                """
                if not release['discogs_image']:
                    url = 'http://coverartarchive.org/release/%s' % r_id
                    try:    
                        r = requests.get(url)
                        result = r.json()
                        release['discogs_image'] = result['images'][0]['image']
                    except:
                        pass
                    

                
                completed_releases.append(release['id'])
            
        
        
        return releases
    
    
    """
    formatting method, to have easy to use variables on client side
    """
    def format_releases(self, releases):

        log = logging.getLogger('importer.process.format_releases')
        log.info('Got %s releases to complete' % len(releases))
        
        formatted_releases = []
        
        completed_releases = []
        
        
        for release in releases:
            
            if release['id'] in completed_releases:
                log.debug('already formated release with id: %s' % release['id'])
                
            else:
            
                log.debug('formating release with id: %s' % release['id'])
                completed_releases.append(release['id'])
                
                self.pp.pprint(release)
                
                # release
                r = {}
                r['mb_id'] = None
                r['name'] = None
                r['status'] = None
                r['releasedate'] = None
                r['catalognumber'] = None
                r['country'] = None
                r['asin'] = None
                r['barcode'] = None
                
                if 'id' in release:
                    r['mb_id'] = release['id']
                
                if 'title' in release:
                    r['name'] = release['title']
                
                if 'status' in release:
                    r['status'] = release['status']
                
                if 'date' in release:
                    r['releasedate'] = release['date']
                
                if 'country' in release:
                    r['country'] = release['country']
                
                if 'catalog-number' in release:
                    r['catalognumber'] = release['catalog-number']
                
                
                # media
                m = {}
                m['mb_id'] = None
                m['name'] = None
                m['duration'] = None
                
                if 'recording' in release and release['recording']:
                    
                    if 'title' in release['recording']:
                        m['name'] = release['recording']['title']
                        
                    if 'id' in release['recording']:
                        m['mb_id'] = release['recording']['id']
                        
                    if 'length' in release['recording']:
                        m['duration'] = release['recording']['length']
                
                
                
                
                # artist
                a = {}
                a['mb_id'] = None
                a['name'] = None
                
                if 'artist' in release and release['artist']:
                    
                    if 'name' in release['artist']:
                        a['name'] = release['artist']['name']
                        
                    if 'id' in release['artist']:
                        a['mb_id'] = release['artist']['id']
    
                
                
                
                # label
                l = {}
                l['mb_id'] = None
                l['name'] = None
                l['code'] = None
                
                
                if 'label' in release and release['label']:
                    
                    if 'name' in release['label']:
                        l['name'] = release['label']['name']
                        
                    if 'id' in release['label']:
                        l['mb_id'] = release['label']['id']
                        
                    if 'label-code' in release['label']:
                        l['code'] = release['label']['label-code']
                
    
                
                
    
                
                
                # relation mapping
                rel = {}
                rel['discogs_url'] = None
                rel['discogs_image'] = None
                
                if 'discogs_image' in release and release['discogs_image']:
                    rel['discogs_image'] = release['discogs_image']
                
                if 'discogs_url' in release and release['discogs_url']:
                    rel['discogs_url'] = release['discogs_url']
                    
                elif 'discogs_master_url' in release and release['discogs_master_url']:
                    rel['discogs_url'] = release['discogs_master_url']
                
                
                
                
                r['media'] = m
                r['artist'] = a
                r['label'] = l
                r['relations'] = rel
    
    
                formatted_releases.append(r)
            
            
        return formatted_releases
    
    
    
    
    
    def complete_musicbrainz(self, results):
    
        release_group_ids = []
        
        rgs = []
        
        master_releases = []
    
        # get all release-group-ids
        i = 0
        for r in results:

            if i > 3:
                break
            i+=1
            
            for release in r['recording']['release-list']:
                
                mb_release = musicbrainzngs.get_release_by_id(id=release['id'], includes=['release-groups'])
                release_group_id = mb_release['release']['release-group']['id']
                
                            
                res = {}
                res['release_group_id'] = release_group_id
                res['recording'] = r
                
                
                if release_group_id not in release_group_ids:
                    release_group_ids.append(release_group_id)
                
                if res not in rgs:
                    rgs.append(res)
            
            
            
            
        #for id in release_group_ids:
        for rg in rgs:
            
            id = rg['release_group_id']
            r = rg['recording']
            
            
            result = musicbrainzngs.get_release_group_by_id(id=id, includes=['releases', 'url-rels'])
            
            releases = result['release-group']['release-list']
            
            try:
                relations = result['release-group']['url-relation-list']
                print
                print
                print '""""""""""""""""""""""""""""""""""""""""""""""""""'
                print relations
                print '""""""""""""""""""""""""""""""""""""""""""""""""""'
                print
                print
            except:
                relations = None
            
            
            try:
                sorted_releases = sorted(releases, key=lambda k: k['date']) 
            except Exception, e:
                print "SORTING ERROR"
                sorted_releases = releases
                print e
            
            # sorted_releases.reverse()
            
            first_release = sorted_releases[0]
            
            print 'releases:'
            print releases
            
            print 'first release'
            print first_release
            
            # look up details for the first release
            result = musicbrainzngs.get_release_by_id(id=first_release['id'], includes=['labels', 'url-rels', 'recordings'])

            res = {}
            res['release'] = result['release']
            res['recording'] = r
            res['relations'] = relations
            master_releases.append(res)
            
            
            
        master_releases = self.format_master_releases(master_releases)
            
        print
        print
        print "MASTER RELEASES"
        print master_releases
        print
        print
        
        
        
        return master_releases
    
    
    """
    pre-apply some formatting & structure to provide straighter trmplateing
    """
    def format_master_releases(self, master_releases):
        
        
        print
        print '***************************************************'
        print 'format_master_releases'
        print
        print master_releases
        print
        print '***************************************************'
        print
        
        
        releases = []
        
        for re in master_releases:
            
            release = re['release']
            recording = re['recording']
            relations = re['relations']
            
            print release
            
            print 'recording:'
            print recording
            
            print 'relations:'
            print relations
            
            r = {}
            
            r['mb_id'] = None
            r['name'] = None
            r['releasedate'] = None
            r['asin'] = None
            r['barcode'] = None
            r['status'] = None
            r['country'] = None

            # mapping
            try:
                r['mb_id'] = release['id']
            except:
                pass
            
            try:
                r['name'] = release['title']
            except:
                pass
            
            try:
                r['releasedate'] = release['date']
            except:
                pass
            
            try:
                r['asin'] = release['asin']
            except:
                pass
            
            try:
                r['barcode'] = release['barcode']
            except:
                pass
            
            try:
                r['status'] = release['status']
            except:
                pass
            
            try:
                r['country'] = release['country']
            except:
                pass
            
            
            # track mapping
            m = {}
            m['mb_id'] = None
            m['name'] = None
            m['duration'] = None
        
            try:
                m['mb_id'] = recording['recording']['id']
            except:
                pass

            try:
                m['name'] = recording['recording']['title']
            except:
                pass
            
            try:
                m['duration'] = recording['recording']['length']
            except:
                pass
            
            
            # try to get media position
            if 'medium-list' in release:
                print
                print 'got medium list'
                print '*************************************************************'
                print release['medium-list']
                print '*************************************************************'
                for el in release['medium-list'][0]['track-list']:
                    print
                    print el
                    print
                print '*************************************************************'
                print '*************************************************************'
            
            
            r['media'] = m
            
            # artist mapping
            a = {}
            a['mb_id'] = None
            a['name'] = None
            
            try:
                artist = recording['recording']['artist-credit'][0]['artist']
                print artist
                
                try:
                    a['mb_id'] = artist['id']
                except:
                    pass
                
                try:
                    a['name'] = artist['name']
                except:
                    pass
            except:
                pass
            
            
            r['artist'] = a
            
            
            # label related mapping
            l = {}
            l['mb_id'] = None
            l['name'] = 'Unknown'
            l['code'] = None
            l['catalognumber'] = None
            
            try:
                label = release['label-info-list'][0]['label']
                print label
                
                try:
                    l['mb_id'] = label['id']
                except:
                    pass
                
                try:
                    l['name'] = label['name']
                except:
                    pass
                
                try:
                    l['code'] = label['label-code']
                except:
                    pass
                
                try:
                    l['catalognumber'] = release['label-info-list'][0]['catalog-number']
                except:
                    pass
                
            except Exception, e:
                print e
                pass
            
            
            
            r['label'] = l
            
            
            # relation mapping
            rel = {}
            rel['discogs_url'] = None
            rel['discogs_image'] = None
            
            try:
                try:
                    for relation in relations:
                        if relation['type'] == 'discogs':
                            rel['discogs_url'] = relation['target']
                            rel['discogs_image'] = discogs_image_by_url(relation['target'], 'uri150')
                            
                    
                except Exception, e:
                    print e
                    pass
                
            except Exception, e:
                print e
                pass
            
            r['relations'] = rel

            

            if r not in releases:
                releases.append(r)
        
        
        return releases


    def mb_order_by_releasedate(self, releases):
        
        print
        print
        print "mb_order_by_releasedate"
        print
        
        for release in releases:
            print release
        
        
        return releases
        

        
if __name__ == '__main__':
    print "Hello World again from %s!" % __name__
        
        