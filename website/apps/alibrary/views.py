from django.views.generic import DetailView, ListView, FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response

from django import http
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.utils import simplejson as json

from django.template import RequestContext

from pure_pagination.mixins import PaginationMixin

from alibrary.models import Artist, Label, Release, Profession, Media

from sendfile import sendfile

from ashop.util.base import get_download_permissions

from alibrary.forms import ReleaseForm

from alibrary.filters import ReleaseFilter

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud

from django.db.models import Q

from easy_thumbnails.files import get_thumbnailer


class ArtistListView(ListView):
    
    # context_object_name = "artist_list"
    # template_name = "alibrary/artist_list.html"
    
    def get_queryset(self):

        kwargs = {}
        
        # check for get variables
        profession = self.request.GET.get('profession', False)
        if profession:
            kwargs[ 'professions' ] = get_object_or_404(Profession, name__iexact=profession)


        return Artist.objects.listed().filter(**kwargs)
    
class ReleaseListView(PaginationMixin, ListView):
    
    # context_object_name = "artist_list"
    #template_name = "alibrary/release_list.html"
    
    object = Release
    paginate_by = 14
    
    model = Release
    
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ReleaseListView, self).get_context_data(**kwargs)
        
        self.extra_context['filter'] = self.filter
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

        # base queryset        
        #qs = Release.objects.all()
        
        # apply filters
        self.filter = ReleaseFilter(self.request.GET, queryset=qs)
        # self.filter = ReleaseFilter(self.request.GET, queryset=Release.objects.active().filter(**kwargs))
        
        qs = self.filter.qs
        
        
        
        
        stags = self.request.GET.get('tags', None)
        print "** STAGS:"
        print stags
        tstags = []
        if stags:
            stags = stags.split(',')
            for stag in stags:
                print int(stag)
                tstags.append(int(stag))
        
        print "** TSTAGS:"
        print tstags
        
        #stags = ('Techno', 'Electronic')
        #stags = (4,)
        if stags:
            qs = Release.tagged.with_all(tstags, qs)
        
        # tagging / cloud generation
        tagcloud = Tag.objects.usage_for_queryset(qs, counts=True)
        print '** CLOUD: **'
        print tagcloud
        print '** END CLOUD **'
        
        self.tagcloud = calculate_cloud(tagcloud)
        
        print '** CALCULATED CLOUD'
        print self.tagcloud
        
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
                medias.append(media)
            for media in release.media_release.filter(artist__name__icontains=q).distinct():
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
  




class ReleaseEditView(FormView):
    model = Release
    template_name = "alibrary/release_edit.html"
    form_class = ReleaseForm

    def get_context_data(self, **kwargs):
        context = super(ReleaseEditView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


 


 


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
