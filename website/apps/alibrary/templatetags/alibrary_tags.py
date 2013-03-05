# -*- coding: utf-8 -*-
from django import template

from classytags.helpers import InclusionTag
from classytags.core import Options
from classytags.arguments import Argument
from django.utils.safestring import mark_safe
import re

from alibrary.models import Daypart

register = template.Library()

@register.filter
def download_url(obj, format, version):
    return obj.get_download_url(format, version)


@register.filter
def quality_indicator(obj):
    return obj.get_media_indicator()


@register.filter
def parse_cuepoints(text):
    
    p = re.compile("(?P<time>[\d]{1,2}:[\d]{2})");
    text = re.sub(p, format_cuelinks, text)

    return mark_safe(text)


def format_cuelinks(m):

    t = m.group(0)
    s = sum(int(x) * 60 ** i for i,x in enumerate(reversed(t.split(":"))))

    str = '<a class="cuepoint" href="#%s">%s</a>' % (s, t)
    print m.group(0)
    return str



@register.inclusion_tag('alibrary/templatetags/playlists_inline.html', takes_context=True)
def playlists_inline(context):
    #context.update({'foo': '...'})
    return context

@register.inclusion_tag('alibrary/templatetags/dayparts_inline.html', takes_context=True)
def dayparts_inline(context, object):
    context.update({'object': object})
    return context

@register.inclusion_tag('alibrary/templatetags/m2m_inline.html', takes_context=True)
def m2m_inline(context, items):
    context.update({'items': items})
    return context

