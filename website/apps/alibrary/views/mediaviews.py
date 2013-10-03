import os

from django.views.generic import DetailView, ListView, FormView, UpdateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response
from django import http
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseRedirect

from django.core.exceptions import PermissionDenied

from django.utils import simplejson as json
from django.template import RequestContext
from django.db.models import Q
from django.conf import settings

from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud
from easy_thumbnails.files import get_thumbnailer

from pure_pagination.mixins import PaginationMixin

from alibrary.models import Media, Playlist, PlaylistItem, Artist, Release
from alibrary.forms import MediaForm, MediaActionForm, MediaRelationFormSet, ExtraartistFormSet
from alibrary.filters import MediaFilter

from lib.util import tagging_extra
from lib.util import change_message

import reversion

from sendfile import sendfile
import audiotranscode


ALIBRARY_PAGINATE_BY = getattr(settings, 'ALIBRARY_PAGINATE_BY', (12,24,36,120))
ALIBRARY_PAGINATE_BY_DEFAULT = getattr(settings, 'ALIBRARY_PAGINATE_BY_DEFAULT', 12)


class MediaListView(PaginationMixin, ListView):
    
    # context_object_name = "artist_list"
    #template_name = "alibrary/release_list.html"
    
    object = Media
    paginate_by = ALIBRARY_PAGINATE_BY_DEFAULT
    
    model = Media
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
        context = super(MediaListView, self).get_context_data(**kwargs)
        
        self.extra_context['filter'] = self.filter
        self.extra_context['relation_filter'] = self.relation_filter
        self.extra_context['tagcloud'] = self.tagcloud

        # active tags
        if self.request.GET.get('tags', None):
            tag_ids = []
            for tag_id in self.request.GET['tags'].split(','):
                tag_ids.append(int(tag_id))
            self.extra_context['active_tags'] = tag_ids
        #self.extra_context['release_list'] = self.filter
    
        # hard-coded for the moment
        
        self.extra_context['list_style'] = self.request.GET.get('list_style', 's')
        #self.extra_context['list_style'] = 's'
        
        self.extra_context['get'] = self.request.GET
        
        context.update(self.extra_context)

        return context
    

    def get_queryset(self, **kwargs):

        # return render_to_response('my_app/template.html', {'filter': f})

        kwargs = {}

        self.tagcloud = None

        q = self.request.GET.get('q', None)
        
        if q:
            qs = Media.objects.filter(Q(name__icontains=q)\
            | Q(release__name__icontains=q)\
            | Q(artist__name__icontains=q))\
            .distinct()
        else:
            qs = Media.objects.all()
            
            
        order_by = self.request.GET.get('order_by', None)
        direction = self.request.GET.get('direction', None)
        
        if order_by and direction:
            if direction == 'descending':
                qs = qs.order_by('-%s' % order_by)
            else:
                qs = qs.order_by('%s' % order_by)
            
            
            
        # special relation filters
        self.relation_filter = []
        
        artist_filter = self.request.GET.get('artist', None)
        if artist_filter:
            qs = qs.filter(artist__slug=artist_filter).distinct()
            # add relation filter
            fa = Artist.objects.filter(slug=artist_filter)[0]
            f = {'item_type': 'artist' , 'item': fa, 'label': _('Artist')}
            self.relation_filter.append(f)
            
        release_filter = self.request.GET.get('release', None)
        if release_filter:
            qs = qs.filter(release__slug=release_filter).distinct()
            # add relation filter
            fa = Release.objects.filter(slug=release_filter)[0]
            f = {'item_type': 'release' , 'item': fa, 'label': _('Release')}
            self.relation_filter.append(f)
            
        # filter by import session
        import_session = self.request.GET.get('import', None)
        if import_session:
            from importer.models import Import
            from django.contrib.contenttypes.models import ContentType
            import_session = get_object_or_404(Import, pk=int(import_session))
            ctype = ContentType.objects.get(model='media')
            ids = import_session.importitem_set.filter(content_type=ctype.pk).values_list('object_id',)
            qs = qs.filter(pk__in=ids).distinct()




        # "extra-filters" (to provide some arbitary searches)
        extra_filter = self.request.GET.get('extra_filter', None)

        print 'EXTRA FILTER!!!!!!!!!!!!!!!!!!!'
        print extra_filter
        print '-------'

        if extra_filter:

            if extra_filter == 'unassigned':

                qs = qs.filter(release=None).distinct()
                # add relation filter
                #fa = Release.objects.filter(slug=release_filter)[0]
                #f = {'item_type': 'release' , 'item': fa, 'label': _('Release')}
                #self.relation_filter.append(f)
            

        # base queryset        
        #qs = Release.objects.all()
        
        # apply filters
        self.filter = MediaFilter(self.request.GET, queryset=qs)
        # self.filter = ReleaseFilter(self.request.GET, queryset=Release.objects.active().filter(**kwargs))
        
        qs = self.filter.qs
        
        
        
        
        stags = self.request.GET.get('tags', None)
        #print "** STAGS:"
        #print stags
        tstags = []
        if stags:
            stags = stags.split(',')
            for stag in stags:
                #print int(stag)
                tstags.append(int(stag))
        
        #print "** TSTAGS:"
        #print tstags
        
        #stags = ('Techno', 'Electronic')
        #stags = (4,)
        if stags:
            qs = Media.tagged.with_all(tstags, qs)
            
            
        # rebuild filter after applying tags
        self.filter = MediaFilter(self.request.GET, queryset=qs)
        
        # tagging / cloud generation
        tagcloud = Tag.objects.usage_for_queryset(qs, counts=True, min_count=0)
        #print '** CLOUD: **'
        #print tagcloud
        #print '** END CLOUD **'
        
        self.tagcloud = tagging_extra.calculate_cloud(tagcloud)
        
        #print '** CALCULATED CLOUD'
        #print self.tagcloud
        
        return qs
    
    
    
    
    
class MediaDetailView(DetailView):

    model = Media
    extra_context = {}

    def get_context_data(self, **kwargs):
        
        context = super(MediaDetailView, self).get_context_data(**kwargs)
        obj = kwargs.get('object', None)
        
        # change history
        self.extra_context['history'] = obj.get_versions()
        
        # foreign appearance
        ps = []
        try:
            pis = PlaylistItem.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))
            ps = Playlist.objects.filter(items__in=pis)
        except:
            pass
        
        self.extra_context['appearance'] = ps
        
        context.update(self.extra_context)
        
        return context
    
    
    
    
 
 
 
 
    
class MediaEditView(UpdateView):
    model = Media
    template_name = "alibrary/media_edit.html"
    success_url = '#'
    form_class = MediaForm
    
    def __init__(self, *args, **kwargs):
        super(MediaEditView, self).__init__(*args, **kwargs)
        
    """"""
    def get_initial(self):
        self.initial.update({ 'user': self.request.user })
        return self.initial
     

    def get_context_data(self, **kwargs):
        
        context = super(MediaEditView, self).get_context_data(**kwargs)
        
        context['action_form'] = MediaActionForm(instance=self.object)
        context['relation_form'] = MediaRelationFormSet(instance=self.object)
        context['extraartist_form'] = ExtraartistFormSet(instance=self.object)
        context['user'] = self.request.user
        context['request'] = self.request

        return context

    """"""
    def form_valid(self, form):
    
        context = self.get_context_data()
        relation_form = context['relation_form']





        
        if form.is_valid():

            self.object.tags = form.cleaned_data['d_tags']
            
            # temporary instance to validate inline forms against
            tmp = form.save(commit=False)

            relation_form = MediaRelationFormSet(self.request.POST, instance=tmp)
            extraartist_form = ExtraartistFormSet(self.request.POST, instance=tmp)




            if extraartist_form.is_valid():
                extraartist_form.save()

        
            if relation_form.is_valid():        
                        
                relation_form.save()

                msg = change_message.construct(self.request, form, [relation_form])
                with reversion.create_revision():
                    obj = form.save()
                    reversion.set_comment(msg)
                
                
                if not obj.artist.pk:
                    obj.artist.creator = context['request'].user
                
                obj.artist.save()
                obj.artist = obj.artist
                
                if not obj.release.pk:
                    obj.release.creator = context['request'].user
                
                obj.release.save()
                obj.release = obj.release
                obj.save()
                
                #form.save_m2m()
                print '----------------------------------------------'
            
                

            return HttpResponseRedirect('#')
        else:
            return self.render_to_response(self.get_context_data(form=form, relation_form=relation_form))
     
    
    
    
    


def media_download(request, slug, format, version):
    
    media = get_object_or_404(Media, slug=slug)
    version = 'base' 


    download_permission = False
    for product in media.mediaproduct.filter(active=True): # users who purchase hardware can download the software part as well
        if get_download_permissions(request, product, format, version):
            download_permission = True
        if product.unit_price == 0:
            download_permission = True
    
    if not download_permission:
        return HttpResponseForbidden('forbidden')
    
    if format in ['mp3', 'flac', 'wav']:
        cache_file = media.get_cache_file(format, version).path
    else:
        raise Http404
    
    
    filename = '%02d %s - %s' % (media.tracknumber, media.name.encode('ascii', 'ignore'), media.artist.name.encode('ascii', 'ignore'))
    
    filename = '%s.%s' % (filename, format)
    
    return sendfile(request, cache_file, attachment=True, attachment_filename=filename)


def stream_html5(request, uuid):
    
    media = get_object_or_404(Media, uuid=uuid)

    stream_permission = False

    #if request.user and request.user.has_perm('alibrary.play_media'):
    if request.user:
        stream_permission = True

    # check if unrestricted license
    if not stream_permission:
        if media.license and media.license.restricted == False:
            stream_permission = True

    if not stream_permission:
        raise PermissionDenied
    
    try:
        from atracker.util import create_event
        create_event(request.user, media, None, 'stream')
    except:
        pass
    
    return sendfile(request, media.get_cache_file('mp3', 'base'))



def __encode(path, bitrate, format):
    at = audiotranscode.AudioTranscode()
    for data in at.transcode_stream(path, format, bitrate=bitrate):
        # do something with chuck of data
        # e.g. sendDataToClient(data)
        yield data

def encode(request, uuid, bitrate=128, format='mp3'):

    media = get_object_or_404(Media, uuid=uuid)

    stream_permission = False

    if request.user and request.user.has_perm('alibrary.play_media'):
        stream_permission = True

    # check if unrestricted license
    if not stream_permission:
        if media.license and media.license.restricted == False:
            stream_permission = True

    if not stream_permission:
        raise PermissionDenied

    try:
        from atracker.util import create_event
        create_event(request.user, media, None, 'stream')
    except:
        pass




    return HttpResponse(__encode(media.master.path, bitrate, format), mimetype='audio/mpeg')

    #return sendfile(request, media.get_cache_file('mp3', 'base'))


def waveform(request, uuid):
    
    media = get_object_or_404(Media, uuid=uuid)

    if media.get_cache_file('png', 'waveform'):
        waveform_file = media.get_cache_file('png', 'waveform')
    else:
        waveform_file = os.path.join(settings.STATIC_ROOT, 'img/base/defaults/waveform.png')


    return sendfile(request, waveform_file)