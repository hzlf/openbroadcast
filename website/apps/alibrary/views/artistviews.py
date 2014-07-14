from django.views.generic import DetailView, ListView, UpdateView
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template import RequestContext
from django.utils.translation import ugettext as _
from pure_pagination.mixins import PaginationMixin
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from braces.views import PermissionRequiredMixin, LoginRequiredMixin

from alibrary.models import Artist, Label, Release, Media, NameVariation
from alibrary.forms import ArtistForm, ArtistActionForm, ArtistRelationFormSet, MemberFormSet, AliasFormSet
from alibrary.filters import ArtistFilter

from tagging.models import Tag
import reversion
from django.db.models import Q
from lib.util import tagging_extra
from lib.util import change_message





ALIBRARY_PAGINATE_BY = getattr(settings, 'ALIBRARY_PAGINATE_BY', (12,24,36,120))
ALIBRARY_PAGINATE_BY_DEFAULT = getattr(settings, 'ALIBRARY_PAGINATE_BY_DEFAULT', 12)

ORDER_BY = [
    {
        'key': 'name',
        'name': _('Name')
    },
    {
        'key': 'date_start',
        'name': _('Date of formation / date of birth')
    },
    {
        'key': 'date_end',
        'name': _('Date of breakup / date of death')
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


class ArtistListView(PaginationMixin, ListView):
    
    # context_object_name = "artist_list"
    #template_name = "alibrary/release_list.html"
    
    object = Artist
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
        context = super(ArtistListView, self).get_context_data(**kwargs)
        
        self.extra_context['filter'] = self.filter
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
    
        self.extra_context['list_style'] = self.request.GET.get('list_style', 'l')
        
        self.extra_context['get'] = self.request.GET
        context.update(self.extra_context)

        return context
    

    def get_queryset(self, **kwargs):

        # return render_to_response('my_app/template.html', {'filter': f})

        kwargs = {}

        self.tagcloud = None

        q = self.request.GET.get('q', None)
        
        if q:
            qs = Artist.objects.filter(name__istartswith=q)\
            .distinct()
        else:
            #qs = Artist.objects.all()
            # only display artists with tracks a.t.m.
            qs = Artist.objects.filter(media_artist__isnull=False).select_related('license','media_artist').prefetch_related('media_artist').distinct()

            
        order_by = self.request.GET.get('order_by', 'created')
        direction = self.request.GET.get('direction', 'descending')
        
        if order_by and direction:
            if direction == 'descending':
                qs = qs.order_by('-%s' % order_by)
            else:
                qs = qs.order_by('%s' % order_by)
            
            
            
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

        date_start_filter = self.request.GET.get('date_start', None)
        if date_start_filter:

            qs = qs.filter(date_start__lte='%s-12-31' % date_start_filter, date_start__gte='%s-00-00' % date_start_filter).distinct()
            # add relation filter
            f = {'item_type': 'label' , 'item': '%s-12-31' % date_start_filter, 'label': _('Date start')}
            self.relation_filter.append(f)
            
            


        # filter by import session
        import_session = self.request.GET.get('import', None)
        if import_session:
            from importer.models import Import
            from django.contrib.contenttypes.models import ContentType
            import_session = get_object_or_404(Import, pk=int(import_session))
            ctype = ContentType.objects.get(model='artist')
            ids = import_session.importitem_set.filter(content_type=ctype.pk).values_list('object_id',)
            qs = qs.filter(pk__in=ids).distinct()

        # base queryset        
        #qs = Release.objects.all()
        
        # apply filters
        self.filter = ArtistFilter(self.request.GET, queryset=qs)
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
        self.filter = ArtistFilter(self.request.GET, queryset=qs)
        
        # tagging / cloud generation
        tagcloud = Tag.objects.usage_for_queryset(qs, counts=True, min_count=0)
        #print '** CLOUD: **'
        #print tagcloud
        #print '** END CLOUD **'
        
        self.tagcloud = tagging_extra.calculate_cloud(tagcloud)
        
        #print '** CALCULATED CLOUD'
        #print self.tagcloud
        
        return qs



class ArtistDetailView(DetailView):

    context_object_name = "artist"
    model = Artist
    extra_context = {}

    
    def render_to_response(self, context):
        return super(ArtistDetailView, self).render_to_response(context, mimetype="text/html")
    

        
    def get_context_data(self, **kwargs):
        
        obj = kwargs.get('object', None)

        context = super(ArtistDetailView, self).get_context_data(**kwargs)

        
        # media sub query
        
        m_ipp = self.request.GET.get('m_ipp', ALIBRARY_PAGINATE_BY_DEFAULT)
        if m_ipp:
            try:
                if int(m_ipp) in ALIBRARY_PAGINATE_BY:
                    m_ipp = int(m_ipp)
                else:
                    m_ipp = int(m_ipp)
            except Exception, e:
                pass
        
        page_num = self.request.GET.get('m_page', 1)
        media_list = Media.objects.filter(artist=obj)
        p = Paginator(media_list, m_ipp, request=self.request, query_param_prefix='m_')
        m_list = p.page(page_num)

        self.extra_context['media'] = m_list
        
        
        
        page_num = self.request.GET.get('r_page', 1)
        release_list = Release.objects.filter(Q(media_release__artist=obj)\
            | Q(album_artists=obj))\
            .distinct()
        p = Paginator(release_list, m_ipp, request=self.request, query_param_prefix='r_')
        r_list = p.page(page_num)
        self.extra_context['releases'] = r_list
        
        
        
        """
        testing top-flop
        """
        m_top = []
        media_top = Media.objects.filter(artist=obj, votes__vote__gt=0).order_by('-votes__vote').distinct()
        if media_top.count() > 0:
            media_top = media_top[0:10]
            for media in media_top:
                m_top.append(media)
                
        self.extra_context['m_top'] = m_top
        
        m_flop = []
        media_flop = Media.objects.filter(artist=obj, votes__vote__lt=0).order_by('votes__vote').distinct()
        if media_flop.count() > 0:
            media_flop = media_flop[0:10]
            for media in media_flop:
                m_flop.append(media)
                
        self.extra_context['m_flop'] = m_flop
        

        m_contrib = Media.objects.filter(extra_artists=obj)
        self.extra_context['m_contrib'] = m_contrib

        self.extra_context['history'] = obj.get_versions()
        

        context.update(self.extra_context)

        return context

    


 
 
 
 
 
 
 
 
 
 
 
 
    
class ArtistEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Artist
    template_name = "alibrary/artist_edit.html"
    success_url = '#'
    form_class = ArtistForm

    permission_required = 'alibrary.edit_artist'
    raise_exception = True
    
    def __init__(self, *args, **kwargs):
        super(ArtistEditView, self).__init__(*args, **kwargs)
        
    """"""
    def get_initial(self):
        self.initial.update({ 'user': self.request.user })
        return self.initial
     

    def get_context_data(self, **kwargs):
        
        context = super(ArtistEditView, self).get_context_data(**kwargs)
        
        context['action_form'] = ArtistActionForm(instance=self.object)
        context['relation_form'] = ArtistRelationFormSet(instance=self.object)
        context['member_form'] = MemberFormSet(instance=self.object)
        context['alias_form'] = AliasFormSet(instance=self.object)
        context['user'] = self.request.user
        context['request'] = self.request

        return context

    def form_valid(self, form):
    
        context = self.get_context_data()

        relation_form = context['relation_form']

        # validation
        if form.is_valid():

            self.object.tags = form.cleaned_data['d_tags']
            
            # temporary instance to validate inline forms against
            tmp = form.save(commit=False)

            aliases_text = self.request.POST.get('aliases_text', None)
            aliases = self.request.POST.get('aliases', None)

            # hack
            self.object.namevariations.all().delete()
            namevariations_text = form.cleaned_data['namevariations']
            if namevariations_text:
                variations = namevariations_text.split(',')
                for v in variations:
                    nv = NameVariation(name=v.strip(), artist=self.object)
                    nv.save()

            member_form = MemberFormSet(self.request.POST, instance=tmp)
            if member_form.is_valid():
                member_form.save()

            alias_form = AliasFormSet(self.request.POST, instance=tmp)
            if alias_form.is_valid():
                alias_form.save()
            else:
                print 'ALIAS FORM NOT VALID!!!'
                print alias_form.errors
        
            relation_form = ArtistRelationFormSet(self.request.POST, instance=tmp)
            if relation_form.is_valid():                
                relation_form.save()

               # obj = form.save()

                msg = change_message.construct(self.request, form, [relation_form,])
                with reversion.create_revision():
                    obj = form.save()
                    reversion.set_comment(msg)

                form.save_m2m()


            return HttpResponseRedirect('#')
        else:
            return self.render_to_response(self.get_context_data(form=form, relation_form=relation_form))
     
 
 
 
 
    

    
# autocompleter views
# TODO: write!
def artist_autocomplete(request):

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
    


    
    
    
    
    
