from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
import locale
import acoustid
import requests

from xml.etree import ElementTree as ET
import simplejson

import musicbrainzngs

from lib.util import pesterfish


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
            
        return res
            
            
        """
        http://musicbrainz.org/ws/2/recording/3ba40ab9-fcfa-450c-8318-e0de8247948c?inc=artist-credits%2Breleases
        """
        
        #r = requests.get('http://musicbrainz.org/ws/2/recording/3ba40ab9-fcfa-450c-8318-e0de8247948c?inc=artist-credits%2Breleases')
        
        #print r.text
        
        #tree = ET.fromstring(r.text)
        
        
        #print tree
        #print pesterfish.to_pesterfish(tree)
        
        
    def get_musicbrainz(self, obj):

        results = []
        
        musicbrainzngs.set_useragent("NRG Processor", "0.01", "http://anorg.net/")
        includes = ['releases', "artist-rels", "label-rels", "recording-rels", "release-rels","release-group-rels", "url-rels", "work-rels"]
        
        
        for e in obj.results_acoustid:
            media_id = e['id']
        
            # media_id = '9ca385f4-4082-494a-974a-b1a8aa997838'
            result = musicbrainzngs.get_recording_by_id(id=media_id, includes=includes)
            results.append(result)
            
        results = self.complete_musicbrainz(results)    
        
        return results
    
    
    def complete_musicbrainz(self, results):
        
        completed_results = []
        
        for r in results:
            print
            print 'RESULT'
            
            
            releases = []
            
            recording = r['recording']
            for release in recording['release-list']:
                
                print release['id']
                
                release = musicbrainzngs.get_release_by_id(id=release['id'], includes=['url-rels', 'work-rels', 'release-groups'])
                
                print 'RELEASE!:::::::::::::::::::::::::::::::::::::::::::::::::'
                print release
                
                relations = []
                
                for relation in release['release']['url-relation-list']:
                    print "Relation: target: %s - url: %s" % (relation['type'], relation['target'])
                    relations.append(relation)
                
                release['relations'] = relations
                    
                releases.append(release)
                
            
            r['release-list'] = releases 
            #r['releases'] = releases 
            
            completed_results.append(r)
            
                    
        return completed_results
        

        

        
        
        
        