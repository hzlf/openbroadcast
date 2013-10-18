from django.contrib.auth.models import User
from django.db.models import Count
from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.contrib.sites.models import Site

import datetime

import json

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache
from tastypie.utils import trailing_slash
from tastypie.exceptions import ImmediateHttpResponse

from abcast.models import Station, Channel, Emission
from abcast.util import notify

from easy_thumbnails.files import get_thumbnailer

class StationResource(ModelResource):
    
    # label = fields.ForeignKey('alibrary.api.LabelResource', 'label', null=True, full=True, max_depth=2)

    class Meta:
        queryset = Station.objects.order_by('name').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/station'
        excludes = ['updated',]
        #include_absolute_url = True
        authentication =  MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication(), Authentication())
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        #cache = SimpleCache(timeout=120)
        

    def dehydrate(self, bundle):
        
        if(bundle.obj.main_image):
            opt = dict(size=(70, 70), crop=True, bw=False, quality=80)
            try:
                main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass

        return bundle

class ChannelResource(ModelResource):
    
    station = fields.ForeignKey('abcast.api.StationResource', 'station', null=True, full=True, max_depth=2)

    class Meta:
        queryset = Channel.objects.order_by('name').all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/channel'
        excludes = ['updated',]
        #include_absolute_url = True
        authentication =  Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        #cache = SimpleCache(timeout=120)
        

    """ stream:
    file: "private/8acfe075/bcb7/11e2/a24c/b8f6b11a3aed/master.mp3"
    rtmp_app: "alibrary"
    rtmp_host: "rtmp://localhost:1935/"
    uri: "/content/library/tracks/tracks/8acfe075-bcb7-11e2-a24c-b8f6b11a3aed/stream_html5/base.mp3"
    uuid: "8acfe075-bcb7-11e2-a24c-b8f6b11a3aed"
    """

    def dehydrate(self, bundle):
        
        if(bundle.obj.station and bundle.obj.station.main_image):
            opt = dict(size=(70, 70), crop=True, bw=False, quality=80)
            try:
                main_image = get_thumbnailer(bundle.obj.station.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                bundle.data['main_image'] = None
        else:
            bundle.data['main_image'] = None


        """
        Generate stream settings
        """
        stream = {
                  'file': 'lala',
                  'rtmp_app': 'lala',
                  'rtmp_host': 'lala',
                  #'uri': 'http://pypo:8000/obp-dev-256.mp3',
                  'uri': bundle.obj.get_stream_url(),
                  'uuid': bundle.obj.uuid,
                  }
        bundle.data['stream'] = stream
        bundle.data['stream_url'] = bundle.obj.get_stream_url()
        bundle.data['images'] = []
        bundle.data['media'] = None

        return bundle
    
    # additional methods
    def prepend_urls(self):
        
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/on-air%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_now_playing'), name="playlist_api_get_now_playing"),
        ]



    def get_now_playing(self, request, **kwargs):
        
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        c = Channel.objects.get(**self.remove_api_resource_names(kwargs))
        
        bundle = self.build_bundle(obj=c, request=request)
        bundle = self.full_dehydrate(bundle)
        

        """
        search for current emission & map item times
        """
        now = datetime.datetime.now()
        
        es = Emission.objects.filter(time_start__lte=now, time_end__gte=now)
        print
        print 'get_now_playing:'
        print es
        
        now_playing = []
        start_next = False
        items = []
        
        
        
        if es.count() == 1:
            e = es[0]
            print e
            print 'Got scheduled emission!'
            

            e_start = e.time_start
            offset = 0
            items = e.content_object.get_items()
            for item in items:
                co = item.content_object
                item.time_start = e_start + datetime.timedelta(milliseconds=offset)
                item.time_end = e_start + datetime.timedelta(milliseconds=offset + co.get_duration() - (item.cue_in + item.cue_out + item.fade_cross))
                
                # check if playing
                if item.time_start < now and item.time_end > now:
                    item.is_playing = True
                    # map item for quick access
                    now_playing = {
                                   'emission': e.get_api_url(),
                                   'item': item.content_object.get_api_url(),
                                   'time_start': item.time_start,
                                   'time_end': item.time_end,
                                   }
                    
                    start_next = (item.time_end - now).total_seconds()
                    
                    print (item.time_end - now).total_seconds()
                    
                else:
                    item.is_playing = False
                
                print '## item'
                print 
                print 'start:      %s' % item.time_start
                print 'end:        %s' % item.time_end
                print 'is playing: %s' % item.is_playing
                # print item.content_object
                
                """
                compose media data
                """


                
                offset += ( co.get_duration() - (item.cue_in + item.cue_out) )
                
        else:
            # no emission in timeframe
            es = Emission.objects.filter(time_start__gte=now).order_by('time_start')
            print 'Nothing playing right now... future:'
            if es.count() > 0:
                e = es[0]
                start_next = (e.time_start - now).total_seconds()
            
            
            

        bundle = {
                  'start_next': start_next,
                  'playing': now_playing,
                  }

        self.log_throttled_access(request)
        return self.create_response(request, bundle)
        

"""
api mapping for airtime / pypo

required resources are:
 - 
 
"""



class BaseResource(Resource):
    
    base_url = Site.objects.get_current().domain

    class Meta:
        #queryset = ImportFile.objects.all()
        list_allowed_methods = ['get',]
        detail_allowed_methods = ['get',]
        resource_name = 'abcast/base'
        # excludes = ['type','results_musicbrainz']
        excludes = ['type',]
        authentication =  MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), Authentication())
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'import_session': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }

    
    # additional methods
    def prepend_urls(self):
        
        return [
            url(r"^(?P<resource_name>%s)/version%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('api_version'),
                name="base_api_version"),
            
            url(r"^(?P<resource_name>%s)/register-component%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('register_component'),
                name="base_api_register_component"),
            
            url(r"^(?P<resource_name>%s)/get-stream-parameters%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_stream_parameters'),
                name="base_api_get_stream_parameters"),
            
            url(r"^(?P<resource_name>%s)/get-stream-settings%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_stream_settings'),
                name="base_api_get_stream_settings"),
                
            url(r"^(?P<resource_name>%s)/update-stream-settings%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('update_stream_settings'),
                name="base_api_update_stream_settings"),
                
            url(r"^(?P<resource_name>%s)/update-liquidsoap-status%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('update_liquidsoap_status'),
                name="base_api_update_liquidsoap_status"),
                
            url(r"^(?P<resource_name>%s)/notify-media-item-start-play%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('notify_start_play'),
                name="base_api_notify_start_play"),
                
            url(r"^(?P<resource_name>%s)/get-bootstrap-info%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_bootstrap_info'),
                name="base_api_get_bootstrap_info"),
                
            url(r"^(?P<resource_name>%s)/recorded-shows%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('recorded_shows'),
                name="base_api_recorded_shows"),
                
            url(r"^(?P<resource_name>%s)/get-schedule%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_schedule'),
                name="base_api_get_schedule"),
                
            url(r"^(?P<resource_name>%s)/on-air%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_now_playing'),
                name="base_api_get_now_playing'"),
        ]
        
        

    def api_version(self, request, **kwargs):

        data = {"version":"2.4.1"}
        return self.json_response(request, data)
    

    def register_component(self, request, **kwargs):

        data = {"status": True}
        return self.json_response(request, data)

    def get_stream_parameters(self, request, **kwargs):

        data = {"stream_params":{"s1":{"enable":"true","output":"icecast","type":"mp3","bitrate":"256","host":"ubuntu","port":"8000","user":"","pass":"donthackme","admin_user":"admin","admin_pass":"donthackme","mount":"airtime_128","url":"http:\/\/airtime.sourcefabric.org","description":"Airtime Radio! Stream #1","genre":"genre","name":"Airtime!","channels":"stereo","liquidsoap_error":"OK"},"s2":{"enable":"false","output":"icecast","type":"","bitrate":"","host":"","port":"","user":"","pass":"","admin_user":"","admin_pass":"","mount":"","url":"","description":"","genre":"","name":"","channels":"stereo"},"s3":{"enable":"false","output":"icecast","type":"","bitrate":"","host":"","port":"","user":"","pass":"","admin_user":"","admin_pass":"","mount":"","url":"","description":"","genre":"","name":"","channels":"stereo"}}}
        return self.json_response(request, data)

    def update_stream_settings(self, request, **kwargs):
        
        print '** update_stream_settings **'
        print request.POST

        data = {"stream_params":{"s1":{"enable":"true","output":"icecast","type":"ogg","bitrate":"128","host":"ubuntu","port":"8000","user":"","pass":"donthackme","admin_user":"admin","admin_pass":"donthackme","mount":"airtime_128","url":"http:\/\/airtime.sourcefabric.org","description":"Airtime Radio! Stream #1","genre":"genre","name":"Airtime!","channels":"stereo","liquidsoap_error":"OK"},"s2":{"enable":"false","output":"icecast","type":"","bitrate":"","host":"","port":"","user":"","pass":"","admin_user":"","admin_pass":"","mount":"","url":"","description":"","genre":"","name":"","channels":"stereo"},"s3":{"enable":"false","output":"icecast","type":"","bitrate":"","host":"","port":"","user":"","pass":"","admin_user":"","admin_pass":"","mount":"","url":"","description":"","genre":"","name":"","channels":"stereo"}}}
        return self.json_response(request, data)

    def get_stream_settings(self, request, **kwargs):
        
        print '** get_stream_settings **'
        print request.GET
        channel_uuid = request.GET.get('channel_id', None)

        try:
            channel = Channel.objects.get(uuid=channel_uuid)
        except Exception, e:
            print e
            channel = None
            
        settings = []
        if channel:
            from abcast.util.liquidsoap import generate_settings
            settings = generate_settings(channel)

        data = {'settings': settings}
        return self.json_response(request, data)

    def update_liquidsoap_status(self, request, **kwargs):
        
        print '** update_liquidsoap_status **'
        print request.POST
        
        data = {'status': 'session!'}
        return self.json_response(request, data)

    def notify_start_play(self, request, **kwargs):
        
        print '** notify_start_play **'
        media_uuid = request.GET.get('media_id', None)
        channel_uuid = request.GET.get('channel_id', None)
        
        print 'request user!!'
        print request.user
        
        if media_uuid and channel_uuid:
            print 'media_uuid  : %s' % media_uuid
            print 'channel_uuid: %s' % channel_uuid
            
            from alibrary.models import Media 
            
            item = Media.objects.get(uuid=media_uuid)
            try:
                channel = Channel.objects.get(uuid=channel_uuid)
            except:
                channel = None
                
            # call notification
            notify.start_play(item, channel, request.user)
            
            
            print 'item: %s' % item.name
            print 'channel: %s' % channel.name
            
        data = {'status': 'session!'}
        return self.json_response(request, data)

    def get_bootstrap_info(self, request, **kwargs):

        data = {"switch_status":{"live_dj":"off","master_dj":"off","scheduled_play":"on"},"station_name":"","stream_label":"","transition_fade":"00.000000"}
        return self.json_response(request, data)

    def recorded_shows(self, request, **kwargs):

        data = {"shows":[],"is_recording":False,"server_timezone":"America\/Los_Angeles"}
        return self.json_response(request, data)
    

    def recorded_shows(self, request, **kwargs):

        data = {"shows":[],"is_recording":False,"server_timezone":"America\/Los_Angeles"}
        return self.json_response(request, data)
    

    def get_schedule(self, request, **kwargs):
        
        """
        get schedule data and put it into airtime format
        TODO: maybe refactor airtime/pypo to match api format
        """
        
        media = {}
        
        es = Emission.objects.future()
        print es
        
        for e in es:
            e_start = e.time_start
            offset = 0
            items = e.content_object.get_items()
            for item in items:
                co = item.content_object
                i_start = e_start + datetime.timedelta(milliseconds=offset)
                i_end = e_start + datetime.timedelta(milliseconds=offset + co.get_duration())
                
                i_start_str = i_start.strftime('%Y-%m-%d-%H-%M-%S')
                i_end_str = i_end.strftime('%Y-%m-%d-%H-%M-%S')
                
                print '## item'
                print 'cue_in:     %s' % item.cue_in
                print 'cue_out:    %s' % item.cue_out
                print 'fade_in:    %s' % item.fade_in
                print 'fade_out:   %s' % item.fade_out
                print 'fade_cross: %s' % item.fade_cross
                print 'id:         %s' % co.pk
                print 
                print '## timing'
                print 'start:      %s' % i_start
                print 'start str:  %s' % i_start_str
                print 'end:        %s' % i_end
                print 'end str:    %s' % i_end_str
                print item.content_object
                
                """
                compose media data
                """
                data = {
                        #'id': co.pk, 
                        'id': co.uuid,     
                        'cue_in': float(item.cue_in) / 1000,  
                        'cue_out': float(co.get_duration() - item.cue_out) / 1000,   
                        'fade_in': item.fade_in,              
                        'fade_out': item.fade_out,
                        #'fade_cross': item.fade_cross,
                        'fade_cross': 0,
                        'replay_gain': 0,
                        'independent_event': False,
                        'start': "%s" % i_start_str,
                        'end': "%s" % i_end_str,
                        'show_name': "%s" % e.name,
                        'uri': "http://%s%s" % (self.base_url, co.get_stream_url()),
                        'row_id': co.uuid,
                        'type': "file",
                        
                        }
                
                media['%s' % i_start_str] = data
                
                offset += ( co.get_duration() - (item.cue_in + item.cue_out) )
         

        print media

        data = {'media': media}
        #data = {"media":{"2013-05-24-08-20-00":{"id":3,"type":"file","row_id":10,"uri":"\/srv\/airtime\/stor\/imported\/1\/Swell Sounds\/[chase 056] - Swell Sounds - SK-8 Ep\/2-Eidolan-320kbps.mp3","fade_in":500,"fade_out":500,"cue_in":0.1,"cue_out":316.3,"start":"2013-05-24-08-20-00","end":"2013-05-24-08-25-16","show_name":"Untitled Show","replay_gain":-9,"independent_event":False},"2013-05-24-08-25-16":{"id":2,"type":"file","row_id":11,"uri":"\/srv\/airtime\/stor\/imported\/1\/Swell Sounds\/[chase 056] - Swell Sounds - SK-8 Ep\/4-I Feel-320kbps.mp3","fade_in":500,"fade_out":500,"cue_in":18.3,"cue_out":249.5,"start":"2013-05-24-08-25-16","end":"2013-05-24-08-29-07","show_name":"Untitled Show","replay_gain":-8.76,"independent_event":False},"2013-05-24-08-29-07":{"id":4,"type":"file","row_id":12,"uri":"\/srv\/airtime\/stor\/imported\/1\/Swell Sounds\/[chase 056] - Swell Sounds - SK-8 Ep\/3-Luminance-320kbps.mp3","fade_in":500,"fade_out":500,"cue_in":0,"cue_out":254.7,"start":"2013-05-24-08-29-07","end":"2013-05-24-08-33-22","show_name":"Untitled Show","replay_gain":-9.35,"independent_event":False},"2013-05-24-08-33-22":{"id":1,"type":"file","row_id":13,"uri":"\/srv\/airtime\/stor\/imported\/1\/Swell Sounds\/[chase 056] - Swell Sounds - SK-8 Ep\/1-Sk-8-320kbps.mp3","fade_in":500,"fade_out":500,"cue_in":0.1,"cue_out":398,"start":"2013-05-24-08-33-22","end":"2013-05-24-08-40-00","show_name":"Untitled Show","replay_gain":-8.52,"independent_event":False}}}
        return self.json_response(request, data)
    
    
    
    def get_now_playing(self, request, **kwargs):
        """
        search for current emission & map item times
        """
        now = datetime.datetime.now()
        
        es = Emission.objects.filter(time_start__lte=now, time_end__gte=now)
        print
        print 'get_now_playing:'
        print es
        
        now_playing = []
        start_next = False
        items = []
        
        
        
        if es.count() == 1:
            e = es[0]
            print e
            print 'Got scheduled emission!'
            

            e_start = e.time_start
            offset = 0
            items = e.content_object.get_items()
            for item in items:
                co = item.content_object
                item.time_start = e_start + datetime.timedelta(milliseconds=offset)
                item.time_end = e_start + datetime.timedelta(milliseconds=offset + co.get_duration() - (item.cue_in + item.cue_out + item.fade_cross))
                
                # check if playing
                if item.time_start < now and item.time_end > now:
                    item.is_playing = True
                    # map item for quick access
                    now_playing = {
                                   'emission': e.get_api_url(),
                                   'item': item.content_object.get_api_url(),
                                   'time_start': item.time_start,
                                   'time_end': item.time_end,
                                   }
                    
                    start_next = (item.time_end - now).total_seconds()
                    
                    print (item.time_end - now).total_seconds()
                    
                else:
                    item.is_playing = False
                
                print '## item'
                print 
                print 'start:      %s' % item.time_start
                print 'end:        %s' % item.time_end
                print 'is playing: %s' % item.is_playing
                # print item.content_object
                
                """
                compose media data
                """


                
                offset += ( co.get_duration() - (item.cue_in + item.cue_out) )
                
        else:
            # no emission in timeframe
            es = Emission.objects.filter(time_start__gte=now).order_by('time_start')
            print 'Nothing playing right now... future:'
            if es.count() > 0:
                e = es[0]
                start_next = (e.time_start - now).total_seconds()
            
            
            

        bundle = {
                  'start_next': start_next,
                  'playing': now_playing,
                  }

        self.log_throttled_access(request)
        return self.create_response(request, bundle)
        
        """
        data = {"now_playing": now_playing,"items": []}
        return self.json_response(request, data)
        """


    """
    response wrappers
    """
    def base_response(self, request, bundle):
        
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        
        return self.create_response(request, bundle)

    def json_response(self, request, data):
        
        self.method_check(request, allowed=['get', 'post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        self.log_throttled_access(request)
        
        return HttpResponse(json.dumps(data),
                            content_type = 'application/json; charset=utf8')
    
    
    
    
    
    
    
    
    
    
    
    
    