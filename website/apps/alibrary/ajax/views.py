from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response

from django import http
from django.http import HttpResponseForbidden, Http404

from django.template import RequestContext

# needed models
from alibrary.models import Artist, Label, Release, Profession, Media
   
class ReleaseAjaxListView(ListView):

    template_name = "alibrary/ajax/release_list.html"
    def get_queryset(self):
        return Release.objects.active()

class ArtistAjaxListView(ListView):

    template_name = "alibrary/ajax/artist_list.html"
    def get_queryset(self):
        return Artist.objects.listed()
