# -*- coding: utf-8 -*-
from django import template

from classytags.helpers import InclusionTag
from classytags.core import Options
from classytags.arguments import Argument
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def download_url(obj, format, version):
    return obj.get_download_url(format, version)





@register.filter
def parse_cuepoints(text):
    
    p = re.compile("(?P<time>[\d]{1,2}:[\d]{2})");
    text = re.sub(p, format_cuelinks, text)

    return mark_safe(text)
    #return text


def format_cuelinks(m):

    t = m.group(0)
    s = sum(int(x) * 60 ** i for i,x in enumerate(reversed(t.split(":"))))

    str = '<a class="cuepoint" href="#%s">%s</a>' % (s, t)
    print m.group(0)
    return str


