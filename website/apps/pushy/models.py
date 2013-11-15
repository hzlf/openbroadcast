import logging
from django.db import models
from django.db.models.signals import post_save, post_delete
import redis
import json
import time

from pushy import settings as pushy_settings

from multiprocessing import Pool

logger = logging.getLogger(__name__)

pool = Pool(processes=10)

def pushy_publish(channel, key, message):
    rs = redis.StrictRedis()
    time.sleep(0.005)
    rs.publish('%s%s' % (channel, key), json.dumps(message))
    

def pushy_post_save(sender, **kwargs):
    rs = redis.StrictRedis()
    obj = kwargs['instance']
    created = kwargs['created']


    print '************ pushy_post_save ********************'

    if created:
        action = 'create'
        try:
            route = obj.get_api_list_url()
        except:
            route = obj.get_api_url()
    else:
        action = 'update'
        route = obj.get_api_url()

    message = {
               'route': route,
               'type': action
               }
    logger.debug('Routing message to: %s' % pushy_settings.get_channel())
    logger.debug('route: %s' % route)

    #pushy_publish(pushy_settings.get_channel(), 'update', message)
    pool.apply_async(pushy_publish(pushy_settings.get_channel(), action, message))


def pushy_post_delete(sender, **kwargs):
    rs = redis.StrictRedis()
    obj = kwargs['instance']

    message = {
               'route': obj.get_api_url(),
               'type': 'delete'
               }
    logger.debug('Routing message to: %s' % pushy_settings.get_channel())
    logger.debug('route: %s' % obj.get_api_url())

    pool.apply_async(pushy_publish(pushy_settings.get_channel(), 'delete', message))
    


def setup_signals():

    for model in pushy_settings.get_models().values():

        if not model:
            logger.error('Unable to register model')
            continue
        else:
            logger.debug('Registering model: %s' % model)
            post_save.connect(pushy_post_save, sender=model)
            post_delete.connect(pushy_post_delete, sender=model)


setup_signals()

