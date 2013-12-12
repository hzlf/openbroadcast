import logging

from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.views.generic.detail import TemplateResponseMixin
from  django.views.generic.edit import FormMixin, ProcessFormView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django import http
from django.utils import simplejson as json
from sendfile import sendfile

from exporter.models import *
from exporter.forms import *
log = logging.getLogger(__name__)


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
        
        return json.dumps(context['result'])


class ExportListView(ListView):
    
    model = Export
    
    def get_queryset(self):
        kwargs = {}
        return Export.objects.filter(user=self.request.user)
    


class ExportDeleteView(DeleteView):
    
    model = Export
    success_url = lazy(reverse, str)("exporter-export-list")
    
    def get_queryset(self):
        kwargs = {}
        return Export.objects.filter(user=self.request.user)




"""
NOT WORKING!!
"""
class ExportModifyView(JSONResponseMixin, UpdateView):
    
    model = Export
  
    def get_queryset(self):
        kwargs = {}
        return Export.objects.filter(user=self.request.user)
    
    def get(self, cls, **kwargs):
        cls.object = cls.get_object()
        kwargs.update({"object": cls.object})
        return cls, kwargs
    
    def render_to_response(self, context):
    # Look for a 'format=json' GET argument
        meta = self.request.META
        if meta.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' or "json" in meta.get("CONTENT_TYPE") or 1 == 1:
            context['result'] = {'status' : True }
            
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return HttpResponseForbidden()



class __nomod__ExportCreateView(ProcessFormView, FormMixin, TemplateResponseMixin):
    
    model = Export
    
    template_name = 'exporter/export_create.html'
    form_class = ExportCreateForm
    #success_url = lazy(reverse, str)("feedback-feedback-list")
    
    def post(self, request, *args, **kwargs):
        
        print kwargs
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            i = Export(user=request.user)
            i.save()
            self.success_url = i.get_absolute_url()            
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

"""
Model version, adding some extra fields to the import session
"""
class ExportCreateView(CreateView):
    
    model = Export
    
    template_name = 'exporter/import_create.html'
    form_class = ExportCreateModelForm
    #success_url = lazy(reverse, str)("feedback-feedback-list")
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class ExportUpdateView(UpdateView):
    
    model = Export
    template_name = 'exporter/import_form_jquery.html'
    #template_name = 'exporter/import_form_backbone.html'
    #template_name = 'exporter/import_form_rework.html'
    def get_queryset(self):
        kwargs = {}
        return Export.objects.filter(user=self.request.user)
    
    
    
@login_required
def export_download(request, uuid, token):
    
    log = logging.getLogger('exporter.views.export_download')
    log.info('Download Request by: %s' % (request.user.username))
    

        
    export = get_object_or_404(Export, uuid=uuid)
    #version = 'base' 

    print 'EXPORT: %s' % export

    download_permission = False
    
    if request.user == export.user and token == export.token:
        download_permission = True
    
    if not download_permission:
        return HttpResponseForbidden('forbidden')
    

    filename = '%s.%s' % (export.filename, 'zip')

    export.set_downloaded()
    
    return sendfile(request, export.file.path, attachment=True, attachment_filename=filename)





