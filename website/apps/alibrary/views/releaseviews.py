from django.views.generic import DetailView, ListView, UpdateView
from django.shortcuts import get_object_or_404, render_to_response
from django import http
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils import simplejson as json
from django.conf import settings
from django.template import RequestContext
from sendfile import sendfile

from pure_pagination.mixins import PaginationMixin
from alibrary.models import Artist, Label, Release
from ashop.util.base import get_download_permissions


#from alibrary.forms import ReleaseForm
from alibrary.forms import *

from alibrary.filters import ReleaseFilter

from tagging.models import Tag

from django.db.models import Q

from lib.util import tagging_extra
from lib.util import change_message

import reversion

ALIBRARY_PAGINATE_BY = getattr(settings, 'ALIBRARY_PAGINATE_BY', (12,24,36,120))
ALIBRARY_PAGINATE_BY_DEFAULT = getattr(settings, 'ALIBRARY_PAGINATE_BY_DEFAULT', 12)


ORDER_BY = [
    {
        'key': 'name',
        'name': _('Name')
    },
    #{
    #    'key': 'votes',
    #    'name': _('Most rated')
    #},
    #{
    #    'key': 'votes__vote',
    #    'name': _('Rating')
    #},
    {
        'key': 'releasedate',
        'name': _('Releasedate')
    },
    {
        'key': 'publish_date',
        'name': _('Publishing date')
    },
    {
        'key': 'updated',
        'name': _('Last modified')
    },
    {
        'key': 'created',
        'name': _('Creation date')
    },
]


class ReleaseListView(PaginationMixin, ListView):
    
    # context_object_name = "artist_list"
    #template_name = "alibrary/release_list.html"
    
    object = Release
    paginate_by = ALIBRARY_PAGINATE_BY_DEFAULT
    
    model = Release
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
        context = super(ReleaseListView, self).get_context_data(**kwargs)
        
        self.extra_context['filter'] = self.filter
        self.extra_context['special_filters'] = ['releasedate',]
        self.extra_context['relation_filter'] = self.relation_filter
        self.extra_context['tagcloud'] = self.tagcloud
        # for the ordering-box
        self.extra_context['order_by'] = ORDER_BY

        # active tags
        if self.request.GET.get('tags', None):
            tag_ids = []
            for tag_id in self.request.GET['tags'].split(','):
                tag_ids.append(int(tag_id))
            self.extra_context['active_tags'] = tag_ids
        #self.extra_context['release_list'] = self.filter
    
        # hard-coded for the moment
        
        self.extra_context['list_style'] = self.request.GET.get('list_style', 'l')
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
            qs = Release.objects.filter(Q(name__istartswith=q)\
            | Q(media_release__name__icontains=q)\
            | Q(media_release__artist__name__icontains=q)\
            | Q(label__name__icontains=q))\
            .distinct()
        else:
            qs = Release.objects.select_related('label','media','license').all()
            
            
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
            
            #qs = qs.filter(media_release__artist__slug=artist_filter).distinct()
            # incl album_artists
            qs = qs.filter(Q(media_release__artist__slug=artist_filter) | Q(album_artists__slug=artist_filter)).distinct()
            
            # add relation filter
            fa = Artist.objects.filter(slug=artist_filter)[0]
            f = {'item_type': 'artist' , 'item': fa, 'label': _('Artist')}
            self.relation_filter.append(f)
            
        label_filter = self.request.GET.get('label', None)
        if label_filter:
            qs = qs.filter(label__slug=label_filter).distinct()
            # add relation filter
            fa = Label.objects.filter(slug=label_filter)[0]
            f = {'item_type': 'label' , 'item': fa, 'label': _('Label')}
            self.relation_filter.append(f)


        # filter by import session
        import_session = self.request.GET.get('import', None)
        if import_session:
            from importer.models import Import
            from django.contrib.contenttypes.models import ContentType
            import_session = get_object_or_404(Import, pk=int(import_session))
            ctype = ContentType.objects.get(model='release')
            ids = import_session.importitem_set.filter(content_type=ctype.pk).values_list('object_id',)
            qs = qs.filter(pk__in=ids).distinct()

        # filter by user
        creator_filter = self.request.GET.get('creator', None)
        if creator_filter:
            from django.contrib.auth.models import User
            creator = get_object_or_404(User, username='%s' % creator_filter)
            qs = qs.filter(creator=creator).distinct()
            f = {'item_type': 'release' , 'item': creator, 'label': _('Added by')}
            self.relation_filter.append(f)

        # filter by promo flag
        promo_filter = self.request.GET.get('promo', None)
        if promo_filter and promo_filter.isnumeric() and int(promo_filter) == 1:
            from django.db.models import F
            qs = qs.filter(releasedate__gte=F('publish_date')).distinct()
            f = {'item_type': 'release' , 'item': _('Promotional releases'), 'label': 'Filter'}
            self.relation_filter.append(f)


        # "extra-filters" (to provide some arbitary searches)
        extra_filter = self.request.GET.get('extra_filter', None)
        """
        if extra_filter:
            if extra_filter == 'no_cover':
                qs = qs.filter(main_image=None).distinct()
                # add relation filter
                #fa = Release.objects.filter(slug=release_filter)[0]
                #f = {'item_type': 'release' , 'item': fa, 'label': _('Release')}
                #self.relation_filter.append(f)
            if extra_filter == 'has_cover':
                qs = qs.exclude(main_image=None).distinct()
                # add relation filter
                #fa = Release.objects.filter(slug=release_filter)[0]
                #f = {'item_type': 'release' , 'item': fa, 'label': _('Release')}
                #self.relation_filter.append(f)
        """




        # base queryset        
        #qs = Release.objects.all()
        
        # apply filters
        self.filter = ReleaseFilter(self.request.GET, queryset=qs)
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
            qs = Release.tagged.with_all(tstags, qs)
            
            
        # rebuild filter after applying tags
        self.filter = ReleaseFilter(self.request.GET, queryset=qs)
        
        # tagging / cloud generation
        tagcloud = Tag.objects.usage_for_queryset(qs, counts=True, min_count=2)
        #print '** CLOUD: **'
        #print tagcloud
        #print '** END CLOUD **'
        
        self.tagcloud = tagging_extra.calculate_cloud(tagcloud)
        
        #print '** CALCULATED CLOUD'
        #print self.tagcloud
        
        return qs



class ReleaseDetailView(DetailView):

    model = Release
    context_object_name = "release"
    extra_context = {}
    
    def render_to_response(self, context):
        return super(ReleaseDetailView, self).render_to_response(context, mimetype="text/html")
        
    def get_context_data(self, **kwargs):
        
        context = super(ReleaseDetailView, self).get_context_data(**kwargs)
        obj = kwargs.get('object', None)
        
        self.extra_context['history'] = obj.get_versions()
        context.update(self.extra_context)
        
        return context

    
    
class ReleaseEditView(UpdateView):
    model = Release
    template_name = "alibrary/release_edit.html"
    success_url = '#'
    form_class = ReleaseForm
    
    def __init__(self, *args, **kwargs):
        #self.user = self.request.user
        
        self.user = User.objects.get(pk=1)
        
        super(ReleaseEditView, self).__init__(*args, **kwargs)
        
    def get_initial(self):
        self.initial.update({ 'user': self.request.user })
        return self.initial
        

    def get_context_data(self, **kwargs):

        print 'GET CONTEXT DATA'
        print kwargs
        
        context = super(ReleaseEditView, self).get_context_data(**kwargs)
        
        # 
        context['release_bulkedit_form'] = ReleaseBulkeditForm(instance=self.object)
        context['action_form'] = ReleaseActionForm(instance=self.object)
        
        #context['releasemedia_form'] = ReleaseMediaFormSet(instance=self.object)

        context['releasemedia_form'] = kwargs.get('releasemedia_form', ReleaseMediaFormSet(instance=self.object))


        context['relation_form'] = ReleaseRelationFormSet(instance=self.object)
        context['albumartist_form'] = AlbumartistFormSet(instance=self.object)

        context['user'] = self.request.user
        context['request'] = self.request
        
        return context
    


    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('alibrary.edit_release'):
            return HttpResponseForbidden()
        return super(ReleaseEditView, self).dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        context = self.get_context_data()
        # get the inline forms
        releasemedia_form = context['releasemedia_form']
        relation_form = context['relation_form']


        valid = False


        if form.is_valid():

            self.object.tags = form.cleaned_data['d_tags']

            # temporary instance to validate inline forms against
            tmp = form.save(commit=False)
            releasemedia_form = ReleaseMediaFormSet(self.request.POST, instance=tmp)
            relation_form = ReleaseRelationFormSet(self.request.POST, instance=tmp)
            albumartist_form = AlbumartistFormSet(self.request.POST, instance=tmp)

        if relation_form.is_valid():
            relation_form.save()

        if albumartist_form.is_valid():
            albumartist_form.save()

        if releasemedia_form.is_valid():

            valid = True

            print "releasemedia_form.cleaned_data:",
            print releasemedia_form.cleaned_data

            releasemedia_form.save()

            for te in releasemedia_form.cleaned_data:

                print te['artist']
                if not te['artist'].pk:
                    print 'no artist yet - create: %s' % te['artist']
                    te['artist'].save()
                    te['id'].artist = te['artist']
                    te['id'].save()


            """
            handle publish action
            """
            action_form = ReleaseActionForm(self.request.POST)
            publish = False
            if action_form.is_valid():
                publish = action_form.cleaned_data['publish']


            """"""
            msg = change_message.construct(self.request, form, [relation_form, releasemedia_form])
            with reversion.create_revision():
                obj = form.save()
                if publish:
                    msg = '%s. \n %s' %('Published release', msg)
                reversion.set_comment(msg)
            form.save_m2m()


            if publish:
                print 'publish:'
                print publish
                from datetime import datetime
                obj.publish_date = datetime.now()
                obj.publisher = self.request.user

                obj.save()




        if valid:
            return HttpResponseRedirect('#')
        else:
            print '!!! ERRORS!!!!!!!!!!!!!!!!!!!!!!!!'
            print releasemedia_form.errors

            return self.render_to_response(self.get_context_data(form=form, releasemedia_form=releasemedia_form))


    

    
# autocompleter views
def release_autocomplete(request):

    q = request.GET.get('q', None)
    
    result = []
    
    if q and len(q) > 1:
        
        releases = Release.objects.filter(Q(name__istartswith=q)\
            | Q(media_release__name__icontains=q)\
            | Q(media_release__artist__name__icontains=q)\
            | Q(label__name__icontains=q))\
            .distinct()
        for release in releases:
            item = {}
            item['release'] = release
            medias = []
            artists = []
            labels = []
            for media in release.media_release.filter(name__icontains=q).distinct():
                if not media in medias:
                    medias.append(media)
            for media in release.media_release.filter(artist__name__icontains=q).distinct():
                if not media.artist in artists:
                    artists.append(media.artist)
                
            if not len(artists) > 0:
                artists = None
            if not len(medias) > 0:
                medias = None
            if not len(labels) > 0:
                labels = None

            item['artists'] = artists
            item['medias'] = medias
            item['labels'] = labels
            
            result.append(item)
        
    
    #return HttpResponse(json.dumps(list(result)))
    return render_to_response("alibrary/element/autocomplete.html", { 'query': q, 'result': result }, context_instance=RequestContext(request))
    



class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        
        ret = {}
        
        release = context['release']
        
        ret['name'] = release.name
        ret['status'] = True
        
        ret['media'] = {};
        
        for media in release.get_media():
            ret['media'][media.id] = {
                                      'name': media.name,
                                      'tracknumber': media.tracknumber,
                                      'url': media.master.url
                                      }
            print media.name
        
        
        
        return json.dumps(ret)
    
class JSONReleaseDetailView(JSONResponseMixin, ReleaseDetailView):
    pass



def release_download(request, slug, format, version):
    
    release = get_object_or_404(Release, slug=slug)
    
    version = 'base' 
    
    """
    check permissions
    """
    download_permission = False
    for product in release.releaseproduct.filter(downloadrelease__format__format=format, active=True): # users who purchase hardware can download the software part as well
        if get_download_permissions(request, product, format, version):
            download_permission = True
        if product.unit_price == 0:
            download_permission = True
    
    if not download_permission:
        return HttpResponseForbidden('forbidden')
    
    """
    check if valid
    TODO: use formats defined in settings
    """
    if format in ['mp3', 'flac', 'wav']:
        cache_file = release.get_cache_file(format, version)
    else:
        raise Http404
    
    
    if release.catalognumber:
        filename = '[%s] - %s [%s]' % (release.catalognumber.encode('ascii', 'ignore'), release.name.encode('ascii', 'ignore'), format.upper())
    else:
        filename = '%s [%s]' % (release.name.encode('ascii', 'ignore'), format.upper())
    
    filename = '%s.%s' % (filename, 'zip')
    
    return sendfile(request, cache_file, attachment=True, attachment_filename=filename)










def release_playlist(request, slug, format, version):
    
    object = get_object_or_404(Release, slug=slug)

    if format in ['mp3']:
        pass
    else:
        raise Http404

    return render_to_response('alibrary/xml/rss_playlist.xml', { 'object': object }, context_instance=RequestContext(request))
    # return render_to_response('alibrary/xml/rss_playlist.xml', data, mimetype="application/xhtml+xml")
    


    

