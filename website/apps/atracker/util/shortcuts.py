from atracker.models import Event

import logging
log = logging.getLogger(__name__)

def create_event(user, content_object, event_content_object=None, event_type=''):
    log = logging.getLogger('atracker.util.create_event')
    log.info('adding event "%s" for "%s"' % (event_type, content_object))
    
    Event.create_event(user, content_object, event_content_object, event_type)
