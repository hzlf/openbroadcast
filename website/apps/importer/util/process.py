from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
import locale
import acoustid
import requests

from xml.etree import ElementTree as ET
import simplejson

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
        
        for d in data:
            t = {
                 'score': d[0],
                 'id': d[1],
                 }
            res.append(t)
            
        return res
            
            
        """
        http://musicbrainz.org/ws/2/recording/3ba40ab9-fcfa-450c-8318-e0de8247948c?inc=artist-credits%2Breleases
        """
        
        #r = requests.get('http://musicbrainz.org/ws/2/recording/3ba40ab9-fcfa-450c-8318-e0de8247948c?inc=artist-credits%2Breleases')
        
        #print r.text
        
        #tree = ET.fromstring(r.text)
        
        
        #print tree
        #print pesterfish.to_pesterfish(tree)
        
        
        
        
        