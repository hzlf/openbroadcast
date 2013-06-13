import datetime

from lib.icecast.api import IcecastAPI

# logging
import logging
logger = logging.getLogger(__name__)

def start_play(item, channel=None, user=None):
    log = logging.getLogger('abcast.util.notify.start_play')

    log.debug('item: %s' % item)
    log.debug('channel: %s' % channel)
    log.debug('user: %s' % user)
    
    """
    Update stream metadata
    """
    text = u'%s - %s | %s' % (item.name, item.artist.name, item.release.name)
    api = IcecastAPI()
    api.set_metadata(channel, text)
    
    
    """
    Add stat information
    """
    """
    try:
        from atracker.util import create_event
        create_event(user, item, channel, 'playout')
    except Exception, e:
        log.warning('exception: %s' % e)
    """
