import os
import logging

from easy_thumbnails.files import get_thumbnailer

from alibrary.util.relations import uuid_by_object

log = logging.getLogger(__name__)

class Process(object):

    def inject_metadata(self, path, media):


        self.metadata_mutagen(path, media)
        #self.metadata_audiotools(path, media)

        return




    def metadata_mutagen(self, path, media):

        from mutagen.id3 import ID3, TRCK, TIT2, TPE1, TALB, TCON, TXXX, UFID, TSRC, TPUB, TMED, TRCK, TDRC

        tags = ID3(path)

        # reset tags
        tags.delete()

        # track-level metadata
        tags.add(TIT2(encoding=3, text=u'%s' % media.name))
        tags.add(UFID(encoding=3, owner='http://openbroadcast.ch', data=u'%s' % media.uuid))
        # remove genre
        tags.add(TCON(encoding=3, text=u''))
        tags.add(TMED(encoding=3, text=u'Digital Media'))
        if media.tracknumber:
            tags.add(TRCK(encoding=3, text=u'%s' % media.tracknumber))
        if media.isrc:
            tags.add(TSRC(encoding=3, text=u'%s' % media.isrc))

        if uuid_by_object(media, 'musicbrainz'):
            tags.add(UFID(encoding=3, owner='http://musicbrainz.org', data=u'%s' % uuid_by_object(media, 'musicbrainz')))

        # release-level metadata
        if media.release:
            tags.add(TALB(encoding=3, text=u'%s' % media.release.name))
            if media.release.catalognumber:
                tags.add(TXXX(encoding=3, desc='CATALOGNUMBER', text=u'%s' % media.release.catalognumber))
            if media.release.releasedate:
                tags.add(TDRC(encoding=3, text=u'%s' % media.release.releasedate.year))
            if media.release.release_country:
                tags.add(TXXX(encoding=3, desc='MusicBrainz Album Release Country', text=u'%s' % media.release.release_country.iso2_code))
            if media.release.totaltracks and media.tracknumber:
                tags.add(TRCK(encoding=3, text=u'%s/%s' % (media.tracknumber, media.release.totaltracks)))
            if media.release.releasedate:
                tags.add(TDRC(encoding=3, text=u'%s' % media.release.releasedate.year))

            if uuid_by_object(media.release, 'musicbrainz'):
                tags.add(TXXX(encoding=3, desc='MusicBrainz Album Id', text=u'%s' % uuid_by_object(media.release, 'musicbrainz')))

        # artist-level metadata
        if media.artist:
            tags.add(TPE1(encoding=3, text=u'%s' % media.artist.name))
            if uuid_by_object(media.artist, 'musicbrainz'):
                tags.add(TXXX(encoding=3, desc='MusicBrainz Artist Id', text=u'%s' % uuid_by_object(media.artist, 'musicbrainz')))

        # label-level metadata
        if media.release and media.release.label:
            tags.add(TPUB(encoding=3, text=u'%s' % media.release.label.name))



        tags.save(v1=0)

        print 'MUTAGEN DONE'


        return



    def metadata_audiotools(self, path, media):

        from audiotools import MetaData
        import audiotools

        meta = MetaData()

        # release-level metadata
        if media.release and media.release.main_image:

            if meta.supports_images() and os.path.exists(media.release.main_image.path):
                opt = dict(size=(200, 200), crop=True, bw=False, quality=80)
                image = get_thumbnailer(media.release.main_image).get_thumbnail(opt)
                meta.add_image(get_raw_image(image.path, 0))




        audiotools.open(path).update_metadata(meta)

        return



def get_raw_image(filename, type):


    import audiotools

    try:
        f = open(filename, 'rb')
        data = f.read()
        f.close()

        return audiotools.Image.new(data, u'', type)
    except IOError:
        raise audiotools.InvalidImage(u'Unable to open file')