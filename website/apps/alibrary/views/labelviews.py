from django.views.generic import DetailView, ListView, UpdateView
from django.shortcuts import get_object_or_404, render_to_response

from django.http import HttpResponseRedirect
from django.conf import settings

from django.template import RequestContext

from pure_pagination.mixins import PaginationMixin
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from alibrary.models import Label, Release

#from alibrary.forms import ReleaseForm
from alibrary.forms import LabelForm, LabelActionForm, LabelRelationFormSet

from alibrary.filters import LabelFilter

from tagging.models import Tag

from django.db.models import Q

import reversion

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
        'key': 'updated',
        'name': _('Last modified')
    },
    {
        'key': 'created',
        'name': _('Creation date')
    },
]

class LabelListView(PaginationMixin, ListView):
    
    # context_object_name = "label_list"
    #template_name = "alibrary/release_list.html"
    
    object = Label
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
        context = super(LabelListView, self).get_context_data(**kwargs)
        
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
        #self.extra_context['release_list'] = self.filter
    
        # hard-coded for the moment
        
        self.extra_context['list_style'] = self.request.GET.get('list_style', 'm')
        #self.extra_context['list_style'] = 's'
        
        self.extra_context['get'] = self.request.GET
        
        context.update(self.extra_context)

        return context
    

    def get_queryset(self, **kwargs):

        # return render_to_response('my_app/template.html', {'filter': f})

        kwargs = {}

        self.tagcloud = None

        q = self.request.GET.get('q', None)
        
        qs = Label.objects.active()
        
        if q:
            qs = qs.filter(name__istartswith=q).distinct()
            
            
            
        order_by = self.request.GET.get('order_by', None)
        direction = self.request.GET.get('direction', None)
        
        if order_by and direction:
            if direction == 'descending':
                qs = qs.order_by('-%s' % order_by)
            else:
                qs = qs.order_by('%s' % order_by)
            
            
            
        # special relation filters
        self.relation_filter = []
        
        label_filter = self.request.GET.get('label', None)
        if label_filter:
            qs = qs.filter(media_release__label__slug=label_filter).distinct()
            # add relation filter
            fa = Label.objects.filter(slug=label_filter)[0]
            f = {'item_type': 'label' , 'item': fa, 'label': _('Label')}
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
            ctype = ContentType.objects.get(model='label')
            ids = import_session.importitem_set.filter(content_type=ctype.pk).values_list('object_id',)
            qs = qs.filter(pk__in=ids).distinct()

        # base queryset        
        #qs = Release.objects.all()
        
        # apply filters
        self.filter = LabelFilter(self.request.GET, queryset=qs)
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
        self.filter = LabelFilter(self.request.GET, queryset=qs)
        
        # tagging / cloud generation
        tagcloud = Tag.objects.usage_for_queryset(qs, counts=True, min_count=0)
        #print '** CLOUD: **'
        #print tagcloud
        #print '** END CLOUD **'
        
        self.tagcloud = tagging_extra.calculate_cloud(tagcloud)
        
        #print '** CALCULATED CLOUD'
        #print self.tagcloud
        
        return qs



class LabelDetailView(DetailView):

    context_object_name = "label"
    model = Label
    extra_context = {}

    
    def render_to_response(self, context):
        return super(LabelDetailView, self).render_to_response(context, mimetype="text/html")
    

        
    def get_context_data(self, **kwargs):
        
        obj = kwargs.get('object', None)

        context = super(LabelDetailView, self).get_context_data(**kwargs)

        
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
        
        """
        page_num = self.request.GET.get('m_page', 1)
        media_list = Media.objects.filter(label=obj)
        p = Paginator(media_list, m_ipp, request=self.request, query_param_prefix='m_')
        m_list = p.page(page_num)

        self.extra_context['media'] = m_list
        """
        
        """
        page_num = self.request.GET.get('r_page', 1)
        release_list = Release.objects.filter(label=obj).distinct()
        p = Paginator(release_list, m_ipp, request=self.request, query_param_prefix='r_')
        r_list = p.page(page_num)
        """


        releases = Release.objects.filter(label=obj).order_by('-releasedate').distinct()[:8]
        self.extra_context['releases'] = releases
        
        
        
        """
        testing top-flop
        """
        """
        m_top = []
        media_top = Media.objects.filter(label=obj, votes__vote__gt=0).order_by('-votes__vote')
        if media_top.count() > 0:
            media_top = media_top[0:10]
            for media in media_top:
                m_top.append(media)
                
        self.extra_context['m_top'] = m_top
        
        m_flop = []
        media_flop = Media.objects.filter(label=obj, votes__vote__lt=0).order_by('votes__vote')
        if media_flop.count() > 0:
            media_flop = media_flop[0:10]
            for media in media_flop:
                m_flop.append(media)
                
        self.extra_context['m_flop'] = m_flop
        

        m_contrib = Media.objects.filter(extra_labels=obj)
        self.extra_context['m_contrib'] = m_contrib
        """

        context.update(self.extra_context)

        self.extra_context['history'] = obj.get_versions()

        return context

    


 
 
 
 
 
 
 
 
 
 
 
 
    
class LabelEditView(UpdateView):
    model = Label
    template_name = "alibrary/label_edit.html"
    success_url = '#'
    form_class = LabelForm
    
    def __init__(self, *args, **kwargs):
        super(LabelEditView, self).__init__(*args, **kwargs)
        
    """"""
    def get_initial(self):
        self.initial.update({ 'user': self.request.user })
        return self.initial
     

    def get_context_data(self, **kwargs):
        
        context = super(LabelEditView, self).get_context_data(**kwargs)
        
        context['action_form'] = LabelActionForm(instance=self.object)
        context['relation_form'] = LabelRelationFormSet(instance=self.object)
        context['user'] = self.request.user
        context['request'] = self.request

        return context

    def form_valid(self, form):
    
        context = self.get_context_data()

        relation_form = context['relation_form']

        # validation
        if form.is_valid():
            print 'form valid'
            
            self.object.tags = form.cleaned_data['d_tags']
            
            # temporary instance to validate inline forms against
            tmp = form.save(commit=False)

            # bloody hack
            
            print self.request.POST
            
            aliases_text = self.request.POST.get('aliases_text', None)
            aliases = self.request.POST.get('aliases', None)
        
            print "***"
            print aliases_text
            print aliases
        
            relation_form = LabelRelationFormSet(self.request.POST, instance=tmp)
            print "relation_form.cleaned_data:",
            print relation_form.is_valid()
            print relation_form.errors
        
            if relation_form.is_valid():                
                relation_form.save()


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
def label_autocomplete(request):

    q = request.GET.get('q', None)
    
    result = []
    
    if q and len(q) > 1:
        
        releases = Release.objects.filter(Q(name__istartswith=q)\
            | Q(media_release__name__icontains=q)\
            | Q(media_release__label__name__icontains=q)\
            | Q(label__name__icontains=q))\
            .distinct()
        for release in releases:
            item = {}
            item['release'] = release
            medias = []
            labels = []
            labels = []
            for media in release.media_release.filter(name__icontains=q).distinct():
                if not media in medias:
                    medias.append(media)
            for media in release.media_release.filter(label__name__icontains=q).distinct():
                if not media.label in labels:
                    labels.append(media.label)
                
            if not len(labels) > 0:
                labels = None
            if not len(medias) > 0:
                medias = None
            if not len(labels) > 0:
                labels = None

            item['labels'] = labels
            item['medias'] = medias
            item['labels'] = labels
            
            result.append(item)
        
    
    #return HttpResponse(json.dumps(list(result)))
    return render_to_response("alibrary/element/autocomplete.html", { 'query': q, 'result': result }, context_instance=RequestContext(request))
    


    
    
    
    
    
