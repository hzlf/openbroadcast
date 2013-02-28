# -*- coding: utf-8 -*-
from django import template

from classytags.helpers import InclusionTag
from classytags.core import Options
from classytags.arguments import Argument
from django.utils.safestring import mark_safe
import re

from alibrary.models import Daypart

register = template.Library()

@register.inclusion_tag('abcast/templatetags/jingles_inline.html', takes_context=True)
def jingles_inline(context):
    #context.update({'foo': '...'})
    return context
