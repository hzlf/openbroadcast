from django.template import RequestContext
from django.views.generic import DetailView, ListView, FormView, UpdateView, CreateView, DeleteView

from django.views.generic.detail import SingleObjectTemplateResponseMixin, TemplateResponseMixin
from  django.views.generic.edit import FormMixin, ProcessFormView
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson

from django import http
from django.utils import simplejson as json

from importer.models import *
from importer.forms import *



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


class ImportListView(ListView):
    
    model = Import
    
    def get_queryset(self):
        kwargs = {}
        return Import.objects.filter(user=self.request.user)
    


class ImportDeleteView(DeleteView):
    
    model = Import
    success_url = lazy(reverse, str)("importer-import-list")
    
    def get_queryset(self):
        kwargs = {}
        return Import.objects.filter(user=self.request.user)




"""
NOT WORKING!!
"""
class ImportModifyView(JSONResponseMixin, UpdateView):
    
    model = Import
  
    def get_queryset(self):
        kwargs = {}
        return Import.objects.filter(user=self.request.user)
    
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



class __nomod__ImportCreateView(ProcessFormView, FormMixin, TemplateResponseMixin):
    
    model = Import
    
    template_name = 'importer/import_create.html'
    form_class = ImportCreateForm
    #success_url = lazy(reverse, str)("feedback-feedback-list")
    
    def post(self, request, *args, **kwargs):
        
        print kwargs
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            i = Import(user=request.user)
            i.save()
            self.success_url = i.get_absolute_url()            
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

"""
Model version, adding some extra fields to the import session
"""
class ImportCreateView(CreateView):
    
    model = Import
    
    template_name = 'importer/import_create.html'
    form_class = ImportCreateModelForm
    #success_url = lazy(reverse, str)("feedback-feedback-list")
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class ImportUpdateView(UpdateView):
    
    model = Import
    template_name = 'importer/import_form_pushy.html'
    def get_queryset(self):
        kwargs = {}
        return Import.objects.filter(user=self.request.user)
    
    
    
@login_required
@csrf_exempt
def multiuploader(request, import_id):
    """
    Main Multiuploader module.
    Parses data from jQuery plugin and makes database changes.
    """
    result = []
    
    if request.method == 'POST':
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')


        print 'MUPLOAD'
        print 'ID: %s' % import_id

        #getting file data for farther manipulations
        file = request.FILES[u'files[]']
        wrapped_file = UploadedFile(file)
        filename = wrapped_file.name
        file_size = wrapped_file.file.size

        import_session = Import.objects.get(pk=import_id)

        import_file = ImportFile()
        import_file.import_session = import_session
        import_file.filename=str(filename)
        import_file.file=file
        import_file.save()

        thumb_url = '' # does not exist, as audio only
        
        #settings imports
        try:
            file_delete_url = settings.MULTI_FILE_DELETE_URL+'/'
            file_url = settings.MULTI_IMAGE_URL+'/'+image.key_data+'/'
        except AttributeError:
            file_delete_url = 'multi_delete/'
            file_url = 'multi_image/'+import_file.filename+'/'

        #generating json response array
        result.append({"name":import_file.filename, 
                       "size":import_file.file.size, 
                       "url":import_file.file.url, 
                        "id":'%s' % import_file.pk, 
                       "thumbnail_url": '',
                       "delete_url": import_file.get_delete_url(), 
                       "delete_type":"POST",})

    else:
        
        import_files = ImportFile.objects.filter(status=0)
        for import_file in import_files:
            result.append({"name":import_file.filename, 
                           "size":import_file.file.size, 
                           "url":import_file.file.url, 
                           "id":'%s' % import_file.pk, 
                           "thumbnail_url": '',
                           "delete_url": import_file.get_delete_url(), 
                           "delete_type":"POST",})
    

    response_data = simplejson.dumps(result)
    if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
        mimetype = 'application/json'
    else:
        mimetype = 'text/plain'
    return HttpResponse(response_data, mimetype=mimetype)













