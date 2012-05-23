from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response

from django import http
from django.http import HttpResponseForbidden, Http404

from django.template import RequestContext
from alabel.models import Artist, Label, Release, Profession, Media

    
class ReleaseAjaxListView(ListView):
    
    print "*****************************"
    print 'in ajax'
    
    # context_object_name = "artist_list"
    template_name = "alabel/ajax/release_list.html"
    
    def get_queryset(self):

        kwargs = {}
        
        # check for get variables
        profession = self.request.GET.get('profession', False)
        if profession:
            kwargs[ 'professions' ] = get_object_or_404(Profession, name__iexact=profession)
        
        return Release.objects.filter(**kwargs)

    
    