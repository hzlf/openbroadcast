from django.db import models
from django.db.models.signals import post_save
import redis
import json

from pusher import settings as pusher_settings

from alibrary.models import Playlist

def pusher_post_save(sender, **kwargs):
    rs = redis.StrictRedis()
    obj = kwargs['instance']
    message = {
               'uuid': obj.uuid,
               'route': obj.get_api_url(),
               'type': 'update'
               }
    rs.publish('push_update', json.dumps(message))
    

def setup_signals():

    for model in pusher_settings.get_models().values():
        if not model:
            continue
        else:
            post_save.connect(pusher_post_save, sender=model)


setup_signals()

