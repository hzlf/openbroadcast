from djangorestframework.resources import ModelResource
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from cms.admin.placeholderadmin import PlaceholderAdmin

from easy_thumbnails.files import get_thumbnailer

from settings import *
from alabel.models import Release, Media, Artist, Label

from lib.templatetags.truncate import *

from filer.models.filemodels import *
from filer.models.foldermodels import *
from filer.models.audiomodels import *
from filer.models.imagemodels import *

class APIBaseMixin():
    
    
    
    def permalink(self, instance):
        return instance.get_absolute_url
    
    
    def images(self, instance):

        images = []
        domain = Site.objects.get_current().domain

        # main image (select in admin)
        if instance.main_image:

            main_image = []
            sized_image = {}
            for k in IMAGE_BASE_SIZES:
                v = IMAGE_BASE_SIZES[k]
                # print k, v

                opt = dict(size=(v, v), crop=True, bw=False, quality=80)
                image = get_thumbnailer(instance.main_image).get_thumbnail(opt)
            
                sized_image[k] = 'http://' + domain + image.url

            images.append(sized_image)

        # images from objects 'picture' folder
        if instance.folder:
            
            
            folder = instance.get_folder('pictures')
            folder_images = folder.files.instance_of(Image)

            
            for folder_image in folder_images:

                main_image = []
                sized_image = {}
                for k in IMAGE_BASE_SIZES:
                    v = IMAGE_BASE_SIZES[k]
                    # print k, v
    
                    opt = dict(size=(v, v), crop=True, bw=False, quality=80)
                    image = get_thumbnailer(folder_image).get_thumbnail(opt)
                
                    if image is not instance.main_image:
                        sized_image[k] = 'http://' + domain + image.url
    
                images.append(sized_image)

                
                

            
        if len(images) < 1:
            return False
        
        return images



class MediaResource(ModelResource):
    model = Media
    fields = ('name', 'media', 'description', 'url')
    exclude = ('master', 'extra_artists', 'release', 'folder')
    ordering = ('name',)

    def media(self, instance):
        
        media = Media.objects.filter(release=instance)

        entry_list = []

        entry = parse_media(instance)
        entry_list.append(entry)

        
        return entry_list



class ReleaseResource(ModelResource, APIBaseMixin):
    
    model = Release
    fields = ('name', 'media', 'images', 'url')
    exclude = ('label', 'folder', 'placeholder_1')
    ordering = ('created',)
    
    
    def media(self, instance):
        
        media = Media.objects.filter(release=instance)
        # media = Media.objects.all() # just for testing...
        
        entry_list = []
        i = 0
        for item in media:
            entry = parse_media(item)
            entry_list.append(entry)
            i += 1
        
        return entry_list
    

    

class ArtistResource(ModelResource, APIBaseMixin):
    model = Artist
    fields = ('uuid', 'name', 'url', 'images', 'pics', 'permalink')
    ordering = ('created',)
    
    def name(self, instance):
        return truncate_chars_inner(instance.name, 30)
    
    def releases(self, instance):
        pass
    
    
    
def parse_media(media):
    
    entry = {}
    
    try:
        entry['name'] = truncate_chars_inner(media.name, 24)
    except Exception, e:
        entry['name'] = False
    
    try:
        entry['artist_url'] = media.artist.get_absolute_url
    except Exception, e:
        entry['artist_url'] = '/'
    
    try:
        entry['release_url'] = media.release.get_absolute_url
    except Exception, e:
        entry['release_url'] = '/'
    
    try:
        entry['uuid'] = media.uuid
    except Exception, e:
        entry['uuid'] = False
        
    try:
        api_url = reverse('artist-resource-detail', None, kwargs={'uuid': media.artist.uuid})
        print api_url
        entry['artist'] = { 'name': truncate_chars_inner(media.artist.name, 30), 'permalink': media.artist.get_absolute_url, 'url': api_url }
    except Exception, e:
        entry['artist'] = False
        
    try:
        #thumbnail_options = dict(size=(480, 49), crop=True, bw=False, quality=100, replace_alpha=False)
        #waveform = get_thumbnailer(media.get_waveform_image()).get_thumbnail(thumbnail_options)
        #entry['waveform'] = waveform.url
        entry['waveform'] = media.get_waveform_image().url
    except Exception, e:
        print e
        entry['waveform'] = False
        
    """
    test with: rtsp://localhost:1935/vod/mp3:/2011/11/23/troforma_05_beg_1.mp3 (eg VLC)
    """
    try:
        entry['stream'] = { 
                           #'file': media.master.file, 
                           'file': media.get_stream_file('mp3', 'base'), 
                           #'media_id': media.id, 
                           'uri': '/tracks/' + media.uuid + '/stream_html5/',
                           'rtmp_host': 'rtmp://' + RTMP_HOST + ':' + RTMP_PORT + '/', 
                           'rtmp_app': RTMP_APP,
                           'uuid' : media.uuid,
                           'token' : 'E3IUD24FG4HJKL6LKJHGF45678IJH45',
                            }
    except Exception, e:
        print 'stream error:',
        print e
        entry['stream'] = False
        
    return entry
