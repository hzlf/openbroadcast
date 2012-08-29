from django.views.generic import DetailView, ListView, FormView, UpdateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response

from django import http
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils import simplejson as json


from django.template import RequestContext

from pure_pagination.mixins import PaginationMixin

from alibrary.models import Artist, Label, Release, Profession, Media, License

from sendfile import sendfile

from ashop.util.base import get_download_permissions

#from alibrary.forms import ReleaseForm
from alibrary.forms import *

from alibrary.filters import ReleaseFilter

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud

from django.db.models import Q

from easy_thumbnails.files import get_thumbnailer


from lib.util import tagging_extra


PAGINATE_BY = (12,24,36,120)
PAGINATE_BY_DEFAULT = 12


class ArtistListView(ListView):
    
    # context_object_name = "artist_list"
    # template_name = "alibrary/artist_list.html"
    
    def get_queryset(self):

        kwargs = {}



        return Artist.objects.listed().filter(**kwargs)
    
class ReleaseListView(PaginationMixin, ListView):
    
    # context_object_name = "artist_list"
    #template_name = "alibrary/release_list.html"
    
    object = Release
    paginate_by = PAGINATE_BY_DEFAULT
    
    
    model = Release
    
    extra_context = {}
    
    def get_paginate_by(self, queryset):
        
        ipp = self.request.GET.get('ipp', None)
        if ipp:
            try:
                if int(ipp) in PAGINATE_BY:
                    return int(ipp)
            except Exception, e:
                pass

        
        
        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super(ReleaseListView, self).get_context_data(**kwargs)
        
        self.extra_context['filter'] = self.filter
        self.extra_context['relation_filter'] = self.relation_filter
        self.extra_context['tagcloud'] = self.tagcloud
        #self.extra_context['release_list'] = self.filter
    
        # hard-coded for the moment
        self.extra_context['list_style'] = 's'
        
        # print self.request.GET
        
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
            qs = Release.objects.all()
            
            
            
        # special relation filters
        self.relation_filter = []
        
        artist_filter = self.request.GET.get('artist', None)
        if artist_filter:
            qs = qs.filter(media_release__artist__slug=artist_filter).distinct()
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


class MediaListView(ListView):

    def get_queryset(self):
        return Media.objects.all()






class ArtistDetailView(DetailView):

    context_object_name = "artist"
    model = Artist

    def get_context_data(self, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(**kwargs)
        context['release_list'] = Release.objects.all()
        return context

class ReleaseDetailView(DetailView):

    context_object_name = "release"
    model = Release
    
    def render_to_response(self, context):
        return super(ReleaseDetailView, self).render_to_response(context, mimetype="text/html")
        
        

    
    def get_context_data(self, **kwargs):
        
        #mimetype="application/xhtml+xml",
        context = super(ReleaseDetailView, self).get_context_data(**kwargs)

        # context['products'] = context['release'].releaseproduct.all() # obsolete - handled via release.get_products()

        # static here for the moment
        format = 'mp3'
        version = 'base'

        downloads = []
        order = None
        """
        #for product in context['release'].releaseproduct.filter(downloadrelease__active=True): # choose to sell digital releases separately
        for product in context['release'].releaseproduct.filter(active=True): # users who purchase hardware can download the software part as well

            if get_download_permissions(self.request, product, format, version):
                downloads.append(product)

        print downloads
        """
        
        images = []

        context['downloads'] = downloads
        context['images'] = images
        #context['all_items'] = Release.objects.all()
        
        
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
        
        context = super(ReleaseEditView, self).get_context_data(**kwargs)
        
        context['releasemedia_form'] = ReleaseMediaFormSet(instance=self.object)
        context['relation_form'] = ReleaseRelationFormSet(instance=self.object)
        
        context['user'] = self.request.user
        context['request'] = self.request
        
        return context
    


    """"""
    def form_valid(self, form):
        context = self.get_context_data()
        # get the inline forms
        releasemedia_form = context['releasemedia_form']
        relation_form = context['relation_form']
        
        print 'validation:'

        # validation
        if form.is_valid():
            print 'form valid'
            
            self.object.tags = form.cleaned_data['d_tags']
            
            # temporary instance to validate inline forms against
            tmp = form.save(commit=False)
        
            releasemedia_form = ReleaseMediaFormSet(self.request.POST, instance=tmp)
            print "releasemedia_form valid?",
            print releasemedia_form.is_valid()
        
        
            relation_form = ReleaseRelationFormSet(self.request.POST, instance=tmp)
            print "relation_form.cleaned_data:",
            print relation_form.is_valid()
            print relation_form.errors
        
            if relation_form.is_valid():

                
                relation_form.save()
        
        
            
        
            if releasemedia_form.is_valid():
                print "releasemedia_form.cleaned_data:",
                print releasemedia_form.cleaned_data
                
                for te in releasemedia_form.cleaned_data:
                    print te['artist']
                    if not te['artist'].pk:
                        print "SAVE ARTIST"
                        te['artist'].save()
                
                
                releasemedia_form.save()

                form.save()
                form.save_m2m()
            else:
                print releasemedia_form.errors
                

            print "VALLIDIO"

            return HttpResponseRedirect('#')
        else:
            print releasemedia_form.errors
            
            
            
            print "NNNOOOTTT VALLIDIO"
            return self.render_to_response(self.get_context_data(form=form, releasemedia_form=releasemedia_form))
    
    
# autocompleter views

def release_autocomplete(request):
    
    

    q = request.GET.get('q', None)
    
    result = []
    
    if q and len(q) > 2:
        
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
    
    
class MediaDetailView(DetailView):

    model = Media

    def get_context_data(self, **kwargs):
        context = super(MediaDetailView, self).get_context_data(**kwargs)
        return context
  



class LicenseDetailView(DetailView):

    context_object_name = "license"
    model = License
 


 


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

    stream_permission = True

    if not stream_permission:
        raise Http403
    
    return sendfile(request, media.get_default_stream_file().path)






def release_playlist(request, slug, format, version):
    
    object = get_object_or_404(Release, slug=slug)

    if format in ['mp3']:
        pass
    else:
        raise Http404

    return render_to_response('alibrary/xml/rss_playlist.xml', { 'object': object }, context_instance=RequestContext(request))
    # return render_to_response('alibrary/xml/rss_playlist.xml', data, mimetype="application/xhtml+xml")
