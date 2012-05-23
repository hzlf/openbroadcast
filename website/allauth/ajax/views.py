from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from emailconfirmation.models import EmailAddress, EmailConfirmation

from allauth.utils import passthrough_login_redirect_url

from allauth.account.utils import get_default_redirect, user_display, complete_signup 
from allauth.account.forms import AddEmailForm, ChangePasswordForm
from allauth.account.forms import LoginForm, ResetPasswordKeyForm
from allauth.account.forms import ResetPasswordForm, SetPasswordForm, SignupForm

import allauth.account.app_settings

def login(request, **kwargs):

    
    form_class = kwargs.pop("form_class", LoginForm)
    template_name = kwargs.pop("template_name", "ajaxaccount/login.html")
    success_url = kwargs.pop("success_url", None)
    url_required = kwargs.pop("url_required", False)
    extra_context = kwargs.pop("extra_context", {})
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    
    extra = None
    if 'extra' in request.GET:
        extra = request.GET.get('extra')
    
    if extra_context is None:
        extra_context = {}
    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)
    
    if request.method == "POST" and not url_required:
        form = form_class(request.POST)
        if form.is_valid():
            form.login(request)
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()
    
    ctx = {
        "form": form,
        "signup_url": passthrough_login_redirect_url(request,
                                                     reverse("account_signup")),
        "site": Site.objects.get_current(),
        "url_required": url_required,
        "extra": extra,
        "redirect_field_name": redirect_field_name,
        "redirect_field_value": request.REQUEST.get(redirect_field_name),
    }
    ctx.update(extra_context)
    return render_to_response(template_name, RequestContext(request, ctx))


def signup(request, **kwargs):
    
    form_class = kwargs.pop("form_class", SignupForm)
    template_name = kwargs.pop("template_name", "ajaxaccount/signup.html")
    redirect_field_name = kwargs.pop("redirect_field_name", "next")
    success_url = kwargs.pop("success_url", None)
    
    extra = None
    if 'extra' in request.GET:
        extra = request.GET.get('extra')
    
    if success_url is None:
        success_url = get_default_redirect(request, redirect_field_name)
    
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            return complete_signup(request, user, success_url)
    else:
        form = form_class()
    ctx = {"form": form,
           "login_url": passthrough_login_redirect_url(request,
                                                       reverse("account_login")),
           "redirect_field_name": redirect_field_name,
           "extra": extra,
           "redirect_field_value": request.REQUEST.get(redirect_field_name) }
    return render_to_response(template_name, RequestContext(request, ctx))
