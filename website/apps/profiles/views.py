from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.views.generic import list_detail

from django.views.generic import DetailView, ListView, FormView, UpdateView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.shortcuts import get_object_or_404, render_to_response

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from profiles.models import *
from profiles.forms import *

from actstream.models import *


def profile_list(request):
    return list_detail.object_list(
        request,
        queryset=Profile.objects.all(),
        paginate_by=20,
    )
profile_list.__doc__ = list_detail.object_list.__doc__


class ProfileListView(ListView):
    
    # context_object_name = "artist_list"
    # template_name = "alibrary/artist_list.html"
    
    def get_queryset(self):

        kwargs = {}
        return Profile.objects.filter(**kwargs)


class ProfileDetailView(DetailView):

    context_object_name = "profile"
    model = Profile
    slug_field = 'user__username'
    

    
    def render_to_response(self, context):
        return super(ProfileDetailView, self).render_to_response(context, mimetype="text/html")
        
    def get_context_data(self, **kwargs):
        context = kwargs
        context_object_name = self.get_context_object_name(self.object)
        if context_object_name:
            context[context_object_name] = self.object
            context['user_stream'] = actor_stream(self.object.user)
        return context





def profile_detail(request, username):
    try:
        user = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        raise Http404
    profile = Profile.objects.get(user=user)
    context = { 'object':profile }
    return render_to_response('profiles/profile_detail.html', context, context_instance=RequestContext(request))


@login_required
def profile_edit(request, template_name='profiles/profile_form.html'):
    """Edit profile."""

    if request.POST:
        profile = Profile.objects.get(user=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserForm(request.POST, instance=request.user)
        service_formset = ServiceFormSet(request.POST, instance=profile)
        link_formset = LinkFormSet(request.POST, instance=profile)

        if profile_form.is_valid() and user_form.is_valid() and service_formset.is_valid() and link_formset.is_valid():
            profile_form.save()
            user_form.save()
            link_formset.save()
            service_formset.save()
            #return HttpResponseRedirect(reverse('profile_detail', kwargs={'username': request.user.username}))
            return HttpResponseRedirect(reverse('profiles-profile-edit'))
        else:
            context = {
                'object': profile,
                'action_form': ActionForm(),
                'profile_form': profile_form,
                'user_form': user_form,
                'service_formset': service_formset,
                'link_formset': link_formset
            }
    else:
        profile = Profile.objects.get(user=request.user)
        link_formset = LinkFormSet(instance=profile)
        service_formset = ServiceFormSet(instance=profile)
        
        context = {
            'object': profile,
            'action_form': ActionForm(),
            'profile_form': ProfileForm(instance=profile),
            'user_form': UserForm(instance=request.user),
            'service_formset': service_formset,
            'link_formset': link_formset
        }
    return render_to_response(template_name, context, context_instance=RequestContext(request))