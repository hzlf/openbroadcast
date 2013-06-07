from django.views.generic import DetailView, ListView, FormView, UpdateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response

from django.db.models import Avg

from django import http
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils import simplejson as json
from django.conf import settings
from django.shortcuts import redirect
from django.core import serializers
from django.utils.translation import ugettext as _
import json

from django.template import RequestContext

from abcast.models import Emission
from alibrary.models import Playlist

#from abcast.filters import EmissionFilter

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud

import datetime

from jsonview.decorators import json_view
import jsonview


from easy_thumbnails.files import get_thumbnailer

from django.db.models import Q
from lib.util import tagging_extra

# logging
import logging
logger = logging.getLogger(__name__)


SCHEDULER_PPH = getattr(settings, 'SCHEDULER_PPH', 42)
SCHEDULER_PPD = getattr(settings, 'SCHEDULER_PPD', 110)
# how long ahead should the schedule be locked
SCHEDULER_LOCK_AHEAD = getattr(settings, 'SCHEDULER_LOCK_AHEAD', 60 * 60)


def schedule(request):
        
    log = logging.getLogger('abcast.schedulerviews.schedule')

    data = {}
    data['list_style'] = request.GET.get('list_style', 's')    
    data['days_offset'] = request.GET.get('days_offset', 0)        
    data['get'] = request.GET
    
    days = []
    today = datetime.datetime.now() 
    offset = datetime.timedelta(days=-today.weekday() + int(data['days_offset']))
    for day in range(7):
        date = today + offset
        #date = date.strftime("%a, %d %b %Y %H:%M:%S +0000")
        days.append( date )
        offset += datetime.timedelta(days=1)
        
    
    data['today'] = today
    data['days'] = days
        
        
    # look for a selected playlist in session
    playlist_id = request.session.get('scheduler_selected_playlist_id', None)
    if playlist_id:
        data['selected_playlist'] = Playlist.objects.get(pk=playlist_id)
    
    
    log.debug('schedule offset: %s' % offset)
    log.debug('schedule today: %s' % today)
    log.debug('schedule playlist_id: %s' % playlist_id)
    
    
    return render_to_response('abcast/schedule.html', data, context_instance=RequestContext(request))



class EmissionListView(ListView):
    
    model = Emission
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(EmissionListView, self).get_context_data(**kwargs)
        
        self.extra_context['list_style'] = self.request.GET.get('list_style', 's')        
        self.extra_context['get'] = self.request.GET
        

        days = []
        today = datetime.datetime.now() 
        offset = datetime.timedelta(days=-today.weekday())
        for day in range(7):
            date = today + offset
            #date = date.strftime("%a, %d %b %Y %H:%M:%S +0000")
            days.append( date )
            offset += datetime.timedelta(days=1)
        
        self.extra_context['today'] = today
        self.extra_context['days'] = days
        
        context.update(self.extra_context)

        return context
    

    def get_queryset(self, **kwargs):

        # return render_to_response('my_app/template.html', {'filter': f})

        kwargs = {}

        self.tagcloud = None

        q = self.request.GET.get('q', None)
        
        if q:
            qs = Emission.objects.filter(Q(name__istartswith=q))\
            .distinct()
        else:
            qs = Emission.objects.all()
    
        
        return qs



class EmissionDetailView(DetailView):

    # context_object_name = "emission"
    model = Emission
    extra_context = {}

    
    def render_to_response(self, context):
        return super(EmissionDetailView, self).render_to_response(context, mimetype="text/html")
    

        
    def get_context_data(self, **kwargs):
        
        obj = kwargs.get('object', None)

        context = super(EmissionDetailView, self).get_context_data(**kwargs)
        

        context.update(self.extra_context)

        return context

    


 
 


"""
views for playlist / emission selection
"""
#@json_view
def select_playlist(request):
    
    log = logging.getLogger('abcast.schedulerviews.select_playlist')
    
    playlist_id = request.GET.get('playlist_id', None) 
    next = request.GET.get('next', None)
    
    if not playlist_id:
        request.session['scheduler_selected_playlist_id'] = None
        
    
    try:
        playlist = Playlist.objects.get(pk=playlist_id)
    except Playlist.DoesNotExist:
        log.warning('playlist does not exists. (id: %s)' % playlist_id)
        raise Http404   
    
    request.session['scheduler_selected_playlist_id'] = playlist.pk

    log.debug('nex: %s' % next)
    log.debug('playlist_id: %s' % playlist_id)
    
    if next:
        return redirect(next)

    data = {
            'status': True,
            'playlist_id': playlist.id
            }
    #return data
    data = json.dumps(data)
    return HttpResponse(data, mimetype='application/json')



"""
put object to schedule
"""
@json_view
def schedule_object(request):
    
    log = logging.getLogger('abcast.schedulerviews.schedule_object')
    
    ct = request.POST.get('ct', None) 
    obj_id = request.POST.get('obj_id', None)
    top = request.POST.get('top', None)
    left = request.POST.get('left', None)
    range_start = request.POST.get('range_start', None)
    range_end = request.POST.get('range_end', None)
    
    log.debug('content type: %s' % ct)
    
    if ct == 'playlist':
        obj = Playlist.objects.get(pk=int(obj_id))
        log.debug('object to schedule: %s' % obj.name)
    
    
    pph = SCHEDULER_PPH
    ppd = SCHEDULER_PPD
    
    
    top = float(top) / pph * 60
    offset_min = int(15 * round(float(top)/15))
    
    left = float(left) / ppd
    offset_d = int(round(float(left)))
    
        
    log.debug('minutes (offset): %s' % offset_min)
    log.debug('days (offset): %s' % offset_d)
    
    # calculate actual date/time for position
    schedule_start = datetime.datetime.strptime('%s 00:00' % range_start, '%Y-%m-%d %H:%M')
    # add offsets
    time_start = schedule_start + datetime.timedelta(minutes=offset_min)
    time_start = time_start + datetime.timedelta(days=offset_d)
    time_end = time_start + datetime.timedelta(milliseconds=obj.get_duration())
    
    log.debug('time_start: %s' % time_start)
    log.debug('time_end: %s' % time_end)
    
    # check if in past
    now = datetime.datetime.now()
    lock_end = now + datetime.timedelta(seconds=SCHEDULER_LOCK_AHEAD)
    if lock_end > time_start:
        return { 'message': _('You cannot schedule things in the past!') }
    
    # check if slot is free
    es = Emission.objects.filter(time_end__gt=time_start, time_start__lt=time_end)
    if es.count() > 0:
        return { 'message': _('Sorry, but the desired time does not seem to be available.') }
    
    
    # if no errors so far -> create emission and attach object
    e = Emission(content_object=obj, time_start=time_start, user=request.user)
    e.save()
    
    
    
    data = {
            'status': True,
            'obj_id': obj_id
            }
    
    return data
    #data = json.dumps(data)
    #return HttpResponse(data, mimetype='application/json')
 
 
 
 
 
 
 


    
    
    
    
    
