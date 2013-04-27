import os

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

from abcast.models import Jingle


from sendfile import sendfile


def waveform(request, uuid):
    
    obj = get_object_or_404(Jingle, uuid=uuid)

    if obj.get_cache_file('png', 'waveform'):
        waveform_file = obj.get_cache_file('png', 'waveform')
    else:
        waveform_file = os.path.join(settings.STATIC_ROOT, 'img/base/defaults/waveform.png')

    return sendfile(request, waveform_file)