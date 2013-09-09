import django
from django.conf import settings
from django.db.models import get_model, get_app

DEBUG = getattr(settings, 'PUSHY_ASSET_DEBUG', True)

def get_channel():
    return '%s' % SETTINGS.get('CHANNEL_PREFIX', 'pushy_asset_')

