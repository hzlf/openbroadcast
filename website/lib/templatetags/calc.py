from django import template
from django.conf import settings
from django.template import Library, Node, Template, resolve_variable

import time

register = template.Library()

@register.filter 
def multiply(value, arg):
    return int(value) * int(arg) 

@register.filter 
def divide(value, arg):
    try:
        return int(int(value) / int(arg))
    except:
        return None

@register.filter 
def subtract(value, arg):
    return int(int(value) - int(arg)) 

@register.filter 
def squaretuple(value):
    return '%sx%s' % (value, value) 

@register.filter 
def halftuple(value):
    return '%sx%s' % (value, int(value) / 2) 

@register.filter 
def widetuple(value):
    return '%sx%s' % (value, int(value) / 16 * 9) 

@register.filter 
def sec_to_time(value):
    if value >= 3600:
        return time.strftime('%H:%M:%S', time.gmtime(value))
    else:
        return time.strftime('%M:%S', time.gmtime(value))

@register.filter 
def msec_to_time(value):
    value = int(value/1000)
    if value >= 3600:
        return time.strftime('%H:%M:%S', time.gmtime(value))
    else:
        return time.strftime('%M:%S', time.gmtime(value))