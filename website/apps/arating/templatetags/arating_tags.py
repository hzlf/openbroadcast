from django import template
from django.contrib.contenttypes.models import ContentType

from arating.models import VOTE_CHOICES 

register = template.Library()
from alibrary.models import Release
     
@register.inclusion_tag('arating/inline.html', takes_context=True)
def rating_for_object(context, object):
    
    request = context['request']
    
    try:
        user_vote = object.votes.filter(user=request.user)[0].vote
        print "user_vote: %s" % user_vote
    except (TypeError, IndexError) as e:
        user_vote = None
    
        
    choices = []
    for choice in reversed(VOTE_CHOICES):
        print 'choice: %s user_vote: %s' % (choice[0], user_vote)
        count = object.votes.filter(vote=choice[0]).count()
        tc = {'key': choice[0], 'count': count, 'active': user_vote==choice[0] }
        choices.append(tc)

    data = {}
    data['choices'] = choices
    data['request'] = request
    #data['rating'] = rating
    data['object'] = object
    data['ct'] = '%s.%s' % (ContentType.objects.get_for_model(object).app_label, object.__class__.__name__.lower())
    
    
    return data
     
     
