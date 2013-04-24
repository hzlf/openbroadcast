from django import template

from ..models import Event

register = template.Library()


@register.inclusion_tag('atracker/templatetags/events_for_object.html', takes_context=True)
def events_for_object(context, obj):

    # events = Event.objects.filter(object_id=obj.pk)
    events = Event.objects.by_obj(obj=obj)
    
    if events:
        return {
            'request': context['request'],
            'events': events
        }

    return {}


@register.inclusion_tag('object_events/notifications.html', takes_context=True)
def render_notifications(context, notification_amount=8):
    """Template tag to render fresh notifications for the current user."""
    if context.get('request') and context['request'].user.is_authenticated():
        events = ObjectEvent.objects.filter(user=context['request'].user)
        if events:
            return {
                'authenticated': True,
                'request': context['request'],
                'unread_amount': events.filter(read_by_user=False).count(),
                'notifications': events[:notification_amount],
            }
        return {'authenticated': True}
    return {}