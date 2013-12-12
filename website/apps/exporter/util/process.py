import logging

from audiotools import MetaData
import audiotools
from easy_thumbnails.files import get_thumbnailer

log = logging.getLogger(__name__)

class Process(object):

    def __init__(self):
        log = logging.getLogger('util.process.Process.__init__')


    def inject_metadata(self, path, media):
        
        log = logging.getLogger('util.process.Process.inject_metadata')
        log.debug('inject metadata to: %s' % (path))
        log.debug('source: %s' % (media))

        """
        audiotools.MetaData
        http://audiotools.sourceforge.net/programming/audiotools.html?highlight=set_metadata#audiotools.MetaData
        class audiotools.MetaData([track_name][, track_number][, track_total][, album_name][, artist_name]
        [, performer_name][, composer_name][, conductor_name][, media][, ISRC][, catalog][, copyright]
        [, publisher][, year][, data][, album_number][, album_total][, comment][, images])
        """
        meta = MetaData()


        """
        prepare metadata object
        """
        # track-level metadata
        meta.track_name = media.name
        meta.track_number = media.tracknumber
        meta.media = 'DIGITAL'
        meta.isrc = media.isrc
        meta.genre = 2
    
        
        # release-level metadata
        if media.release:
            meta.album_name = media.release.name
            meta.catalog = media.release.catalognumber
            meta.track_total = len(media.release.media_release.all())
            
            if media.release.releasedate:
                try:
                    meta.year = str(media.release.releasedate.year)
                    meta.date = str(media.release.releasedate)
                    
                except Exception, e:
                    print e
            
            try:
                
                cover_image = media.release.cover_image if media.release.cover_image else media.release.main_image
                
                if meta.supports_images() and cover_image:
                    for i in meta.images():
                        meta.delete_image(i)
                        
                    opt = dict(size=(200, 200), crop=True, bw=False, quality=80)
                    image = get_thumbnailer(cover_image).get_thumbnail(opt)
                    meta.add_image(get_raw_image(image.path, 0))
                    
            except Exception, e:
                print e
                
            
        # artist-level metadata
        if media.artist:
            meta.artist_name = media.artist.name
                    
        # label-level metadata
        if media.release.label:
            pass
        
        
        audiotools.open(path).set_metadata(meta)
        
        return





def get_raw_image(filename, type):
    try:
        f = open(filename, 'rb')
        data = f.read()
        f.close()

        return audiotools.Image.new(data, u'', type)
    except IOError:
        raise audiotools.InvalidImage(u'Unable to open file')