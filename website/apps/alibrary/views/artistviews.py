from django.views.generic import DetailView, ListView, FormView, UpdateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response
from django import http
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils import simplejson as json
from django.template import RequestContext
from django.db.models import Q
from django.conf import settings

from tagging.models import Tag, TaggedItem
from tagging.utils import calculate_cloud
from easy_thumbnails.files import get_thumbnailer

from pure_pagination.mixins import PaginationMixin

from alibrary.models import Artist
from alibrary.forms import *
# from alibrary.filters import ArtistFilter

from lib.util import tagging_extra


ALIBRARY_PAGINATE_BY = getattr(settings, 'ALIBRARY_PAGINATE_BY', (12,24,36,120))
ALIBRARY_PAGINATE_BY_DEFAULT = getattr(settings, 'ALIBRARY_PAGINATE_BY_DEFAULT', 12)


class ArtistListView(ListView):
    
    # context_object_name = "artist_list"
    # template_name = "alibrary/artist_list.html"
    
    def get_queryset(self):
        kwargs = {}
        return Artist.objects.all().filter(**kwargs)
    
    
class ArtistDetailView(DetailView):

    context_object_name = "artist"
    model = Artist

    def get_context_data(self, **kwargs):
        context = super(ArtistDetailView, self).get_context_data(**kwargs)
        context['release_list'] = Release.objects.all()
        return context
