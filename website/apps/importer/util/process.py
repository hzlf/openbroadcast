from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
import locale
import acoustid
import requests

from xml.etree import ElementTree as ET
import simplejson

import musicbrainzngs
import discogs_client as discogs

from lib.util import pesterfish

from base import discogs_image_by_url 

import logging
log = logging.getLogger(__name__)


AC_API_KEY = 'ZHKcJyyV'

METADATA_SET = {
                # media
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
        musicbrainzngs.set_hostname("172.16.82.130:5000")
        musicbrainzngs.set_rate_limit(False)
    
    
    
    def get_echoprint(self, file):
        from ep.API import fp
        from lib.analyzer.echoprint import Echoprint
        e = Echoprint()
        code, version, duration, echoprint = e.echoprint_from_path(file.path, offset=10, duration=100)
        
        
        # print code
        # code = fp.decode_code_string(code)

        try:
            res = fp.best_match_for_query(code_string=code)
            
            print 'ECHOPRINT!!!!!!!!!!'
            
            print 'TRID'
            print res.TRID
            print 'END TRID'
            
            if res.match():
            
                print res.message()
                print res.match()
                print res.score
                print res.TRID
                #ids = [int(res.TRID),]
                
                return int(res.TRID)
            
        except Exception, e:
            print e
            pass
            
            
        print 'ECHOPRINT!!!!!!!!!!'
        return None
    
    
    def extract_metadata(self, file):
        enc = locale.getpreferredencoding()
        
        try:
            meta = EasyID3(file.path)
        except Exception, e:
            meta = MutagenFile(file.path)

        
        dataset = dict(METADATA_SET)

        """
        Mapping
        """
        
        # Media
        try:
            dataset['media_name'] = meta['title'][0]
        except Exception, e:
            print e
            
        try:
            dataset['media_mb_id'] = meta['musicbrainz_trackid'][0]
        except Exception, e:
            print e
            
        try:

            try:
                dataset['media_tracknumber'] = int(meta['tracknumber'][0])
            except Exception, e:
                print e
                
            try:
                tn = meta['tracknumber'][0].split('/')
                dataset['media_tracknumber'] = int(tn[0])
                dataset['media_totaltracks'] = int(tn[1])
            except Exception, e:
                print e
                
            # TODO: extract tracknumber from filename if not found
        

        except Exception, e:
            print e
           
           
            
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
                print e
            
        except Exception, e:
            print e
            
        try:
            dataset['label_code'] = meta['labelno'][0]
        except Exception, e:
            print e
            
            
            
        # Misc
        try:
            dataset['media_copyright'] = meta['copyright'][0]
        except Exception, e:
            print e
            
        try:
            dataset['media_comment'] = meta['comment'][0]
        except Exception, e:
            print e
            
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

        """
        print
        print
        print "******************************************************************"
        for k in dataset:
            m = dataset[k]
            print "%s:   %s" % (k, m)
        print "******************************************************************"
        print
        print
        """
        
        return dataset
    
    
    def get_aid(self, file):
        
        data = acoustid.match(AC_API_KEY, file.path)
        
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
            res.append(t)
            i += 1
            

        
        print
        print '### ACOUSTID LOOKUP ###'
        
        print res
        
        print
        print
            
        return res

        
    """
    get all 'recordings' from musicbrainz
    """
    def get_musicbrainz(self, obj):

        results = []

        includes = ['releases','artists']
        
        for e in obj.results_acoustid:
            media_id = e['id']

            try:
                result = musicbrainzngs.get_recording_by_id(id=media_id, includes=includes)
                results.append(result)
            except Exception, e:
                pass
            
        # pass results to have them filled up
        results = self.complete_musicbrainz(results)    
        
        return results
    
    
    
    
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
            
            
            result = musicbrainzngs.get_release_group_by_id(id=id, includes=['releases'])
            
            releases = result['release-group']['release-list']
            
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
            result = musicbrainzngs.get_release_by_id(id=first_release['id'], includes=['labels', 'url-rels',])

            res = {}
            res['release'] = result['release']
            res['recording'] = r
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
    def format_master_releases(self, res):
        
        
        
        releases = []
        
        for re in res:
            
            release = re['release']
            recording = re['recording']
            
            print release
            
            print 'recording:'
            print recording
            
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
                relations = release['url-relation-list']
                print
                print 'RELATIONS'
                print relations
                print
                print
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
    
    

    
    
    
    def complete_musicbrainz__(self, results):
        
        completed_results = []
        
        i = 0
        
        for r in results:
            
            if i > 3:
                #pass
                break
            
            i+=1
            
            print
            print 'RESULT'
            
            
            releases = []
            
            recording = r['recording']
            for release in recording['release-list']:
                
                #print release['id']
                
                release = musicbrainzngs.get_release_by_id(id=release['id'], includes=['url-rels', 'release-groups'])
                
                #print 'RELEASE!:::::::::::::::::::::::::::::::::::::::::::::::::'
                #print release
                
                relations = []
                
                try:
                    for relation in release['release']['url-relation-list']:
                        #print "Relation: target: %s - url: %s" % (relation['type'], relation['target'])
                        relations.append(relation)
                        
                except Exception, e:
                    #print e
                    pass
                
                release['relations'] = relations
                    
                releases.append(release)
                

            # order releases by date
            releases = self.mb_order_by_releasedate(releases)
            
            r['release-list'] = releases 
            
            completed_results.append(r)
            
                    
        return completed_results
        

    def mb_order_by_releasedate(self, releases):
        
        print
        print
        print "mb_order_by_releasedate"
        print
        
        for release in releases:
            print release
        
        
        return releases
        

        
        
        
        