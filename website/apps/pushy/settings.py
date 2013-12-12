from django.conf import settings
from django.db.models import get_model

SETTINGS = getattr(settings, 'PUSHY_SETTINGS', {})

def get_channel():
    return '%s' % SETTINGS.get('CHANNEL_PREFIX', 'pushy_')

def get_models():
    
    models = {}
    for model in SETTINGS.get('MODELS', None):
        models[model.lower()] = get_model(*model.split('.'))
    return models