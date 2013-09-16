from django.views.generic import DetailView, ListView, FormView, UpdateView, CreateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response
from django import http
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils import simplejson as json
from django.template import RequestContext
from django.db.models import Q
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud
from easy_thumbnails.files import get_thumbnailer

from pure_pagination.mixins import PaginationMixin

from alibrary.models import Playlist
from alibrary.forms import *
from alibrary.filters import PlaylistFilter

from lib.util import tagging_extra

from django.contrib.auth.models import User
from guardian.forms import UserObjectPermissionsForm

ALIBRARY_PAGINATE_BY = getattr(settings, 'ALIBRARY_PAGINATE_BY', (12,24,36,120))
ALIBRARY_PAGINATE_BY_DEFAULT = getattr(settings, 'ALIBRARY_PAGINATE_BY_DEFAULT', 12)


class PlaylistListView(PaginationMixin, ListView):
    
    context_object_name = "playlist_list"
    template_name = "alibrary/playlist_list.html"
    
    paginate_by = ALIBRARY_PAGINATE_BY_DEFAULT
    extra_context = {}
    
    def get_paginate_by(self, queryset):
        
        ipp = self.request.GET.get('ipp', None)
        if ipp:
            try:
                if int(ipp) in ALIBRARY_PAGINATE_BY:
                    return int(ipp)
            except Exception, e:
                pass

        return self.paginate_by

    def get_context_data(self, **kwargs):
        
        
        context = super(PlaylistListView, self).get_context_data(**kwargs)
        
        
        self.extra_context['filter'] = self.filter
        self.extra_context['relation_filter'] = self.relation_filter
        self.extra_context['tagcloud'] = self.tagcloud

        # active tags
        if self.request.GET.get('tags', None):
            tag_ids = []
            for tag_id in self.request.GET['tags'].split(','):
                tag_ids.append(int(tag_id))
            self.extra_context['active_tags'] = tag_ids
        
        self.extra_context['list_style'] = self.request.GET.get('list_style', 'l')
        self.extra_context['get'] = self.request.GET
        
        context.update(self.extra_context)
        
        return context
    

    def get_queryset(self, **kwargs):
        
        
        self.tagcloud = None
        q = self.request.GET.get('q', None)
        
        if q:
            qs = Playlist.objects.filter(Q(name__istartswith=q)\
            | Q(description__icontains=q))\
            .distinct()
        else:
            qs = Playlist.objects.all()
            

            
            
        order_by = self.request.GET.get('order_by', None)
        direction = self.request.GET.get('direction', None)
        
        if order_by and direction:
            if direction == 'descending':
                qs = qs.order_by('-%s' % order_by)
            else:
                qs = qs.order_by('%s' % order_by)
            
            
            
        if 'type' in self.kwargs:
            qs = qs.filter(type=self.kwargs['type'])
            
        if 'user' in self.kwargs:
            user = get_object_or_404(User, username=self.kwargs['user'])
            if 'type' in self.kwargs:
                qs = qs.filter(type=self.kwargs['type'], user=user)
            else:
                 qs = qs.filter(type__in=['playlist', 'broadcast', 'basket'],user=user)
            
        # special relation filters
        self.relation_filter = []
        
        # apply filters
        self.filter = PlaylistFilter(self.request.GET, queryset=qs)
        qs = self.filter.qs
        
        stags = self.request.GET.get('tags', None)
        tstags = []
        if stags:
            stags = stags.split(',')
            for stag in stags:
                tstags.append(int(stag))

        if stags:
            qs = Release.tagged.with_all(tstags, qs)
            
            
        # rebuild filter after applying tags
        self.filter = PlaylistFilter(self.request.GET, queryset=qs)
        
        # tagging / cloud generation
        tagcloud = Tag.objects.usage_for_queryset(qs, counts=True, min_count=0)

        self.tagcloud = tagging_extra.calculate_cloud(tagcloud)
        return qs
    
    """
    def get_queryset(self):
        kwargs = {}
        return Playlist.objects.filter(**kwargs)
    """

class PlaylistDetailView(DetailView):

    context_object_name = "playlist"
    model = Playlist
    
    def render_to_response(self, context):
        return super(PlaylistDetailView, self).render_to_response(context, mimetype="text/html")
        
    def get_context_data(self, **kwargs):

        context = super(PlaylistDetailView, self).get_context_data(**kwargs)
        return context
    

class PlaylistCreateView(CreateView):
    
    model = Playlist
    
    template_name = 'alibrary/playlist_create.html'
    form_class = PlaylistForm
    #success_url = lazy(reverse, str)("feedback-feedback-list")
    


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaylistCreateView, self).dispatch(*args, **kwargs)
        

    def get_context_data(self, **kwargs):
        
        context = super(PlaylistCreateView, self).get_context_data(**kwargs)
        context['action_form'] = ActionForm()        
        return context
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_edit_url())
    
    
class PlaylistEditView(UpdateView):
    
    model = Playlist
    template_name = "alibrary/playlist_edit.html"
    success_url = '#'
    form_class = PlaylistForm
    
    def __init__(self, *args, **kwargs):
        super(PlaylistEditView, self).__init__(*args, **kwargs)
        

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PlaylistEditView, self).dispatch(*args, **kwargs)
        
    def get_initial(self):
        self.initial.update({ 'user': self.request.user })
        return self.initial
        

    def get_context_data(self, **kwargs):
        
        context = super(PlaylistEditView, self).get_context_data(**kwargs)
        
        context['action_form'] = ActionForm()        
        context['releasemedia_form'] = ReleaseMediaFormSet(instance=self.object)
        
        context['user'] = self.request.user
        context['request'] = self.request
        
        context['permission_form'] =  UserObjectPermissionsForm(self.request.user, self.object, self.request.POST or None)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()        
        print 'validation:'
        
        # validation
        if form.is_valid():
            print 'form valid'
            
            self.object.tags = form.cleaned_data['d_tags']
            
            # temporary instance to validate inline forms against
            tmp = form.save(commit=False)
            
            form.save()
            form.save_m2m()
            

            return HttpResponseRedirect('#')
        else:
            return self.render_to_response(self.get_context_data(form=form))
        



def playlist_convert(request, pk, type):
    
    playlist = get_object_or_404(Playlist, pk=pk)
    
    playlist.convert_to(type)
    

    return HttpResponseRedirect(playlist.get_edit_url())

        
"""
def playlist_collect(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)

    ids = request.POST.get('ids', None)
    ct = request.POST.get('ct', None)

    if ids:
        
        ids = ids.split(',')
        playlist.add_items_by_ids(ids, ct)
    
    content = {'session': 'OK!'}
    
    return http.HttpResponse(json.dumps(content), content_type='application/json')        
        
    
def playlist_reorder(request, pk):
    
    playlist = get_object_or_404(Playlist, pk=pk)

    order = request.POST.get('order', None)

    if order:
        order = order.split(',')
        playlist.reorder_items_by_uuids(order)
        
    print order
    
    content = {
               'session': 'OK!',
               'order': order,
               'pk': playlist.pk
    }
    
    return http.HttpResponse(json.dumps(content), content_type='application/json')        
        
    
def playlist_collect__old(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)

    ids = request.POST.get('ids', None)

    if ids:
        
        ids = ids.split(',')
        playlist.add_media_by_ids(ids)
    
    content = {'session': 'OK!'}
    
    return http.HttpResponse(json.dumps(content), content_type='application/json')
    
"""