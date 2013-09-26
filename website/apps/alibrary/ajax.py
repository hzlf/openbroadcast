from django.core import serializers

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from alibrary.models import APILookup, Release, Relation, Label, Artist, Media

from lib.util.merge import merge_model_objects

import requests

import json

# logging
import logging
logger = logging.getLogger(__name__)


@dajaxice_register
def api_lookup(request, *args, **kwargs):


    log = logging.getLogger('alibrary.ajax.api_lookup')

    item_type = kwargs.get('item_type', None)
    item_id = kwargs.get('item_id', None)
    provider = kwargs.get('provider', None)

    log.debug('type: %s - id: %s - provider: %s' % (item_type, item_id, provider))

    data = {}


    try:
        if item_type == 'release':
            i = Release.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(i)
            al, created = APILookup.objects.get_or_create(content_type=ctype, object_id=i.id, provider=provider)
            if created:
                log.debug('APILookup created: %s' % (al.pk))

        if item_type == 'artist':
            i = Artist.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(i)
            al, created = APILookup.objects.get_or_create(content_type=ctype, object_id=i.id, provider=provider)
            if created:
                log.debug('APILookup created: %s' % (al.pk))

        if item_type == 'label':
            i = Label.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(i)
            al, created = APILookup.objects.get_or_create(content_type=ctype, object_id=i.id, provider=provider)
            if created:
                log.debug('APILookup created: %s' % (al.pk))



        data = al.get_from_api()

        print data


    except Exception, e:
        log.warning('%s' % e)

    return json.dumps(data, encoding="utf-8")


@dajaxice_register
def provider_search_query(request, *args, **kwargs):


    log = logging.getLogger('alibrary.ajax.api_lookup')

    item_type = kwargs.get('item_type', None)
    item_id = kwargs.get('item_id', None)
    provider = kwargs.get('provider', None)

    log.debug('type: %s - id: %s - provider: %s' % (item_type, item_id, provider))

    data = {}
    try:
        if item_type == 'release':
            item = Release.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(item)
            data = {'query': '%s %s' % (item.name, item.get_artists()[0])}

        if item_type == 'artist':
            item = Artist.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(item)
            data = {'query': '%s' % (item.name)}

        if item_type == 'label':
            item = Label.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(item)
            data = {'query': '%s' % (item.name)}


        return json.dumps(data)

    except Exception, e:
        log.warning('%s' % e)
        return None



@dajaxice_register
def provider_search(request, *args, **kwargs):

    log = logging.getLogger('alibrary.ajax.api_lookup')

    item_type = kwargs.get('item_type', None)
    item_id = kwargs.get('item_id', None)
    provider = kwargs.get('provider', None)
    query = kwargs.get('query', None)

    log.debug('query: %s' % (query))


    url = 'http://dgs.anorg.net/database/search?q=%s&type=%s&per_page=%s' % (query, item_type, 50)

    #r = requests.get('http://api.discogs.com/database/search?q=the+fat+of+the+land+the+prodigy&type=release')
    r = requests.get(url)
    results = r.json()['results']
    text = r.text
    #text = text.replace('api.discogs.com', 'dgs.anorg.net')
    results = json.loads(text)['results']


    print r.json()

    data = {
        'query': query,
        'results': results,
    }



    try:
        data = json.dumps(data)
        return data

    except Exception, e:
        log.warning('%s' % e)
        return None


@dajaxice_register
def provider_update(request, *args, **kwargs):

    log = logging.getLogger('alibrary.ajax.api_lookup')


    print kwargs

    item_type = kwargs.get('item_type', None)
    item_id = kwargs.get('item_id', None)
    provider = kwargs.get('provider', None)
    uri = kwargs.get('uri', None)

    log.debug('uri: %s' % (uri))

    item = None
    data = {}
    try:
        if item_type == 'release':
            item = Release.objects.get(pk=item_id)

        if item_type == 'artist':
            item = Artist.objects.get(pk=item_id)

        if item_type == 'label':
            item = Label.objects.get(pk=item_id)


        if item and uri:
            rel = Relation(content_object=item, url=uri)
            rel.save()

        data = {
            'service': '%s' % rel.service,
            'url': '%s' % rel.url,
            }


    except Exception, e:
        log.warning('%s' % e)


    return json.dumps(data)









"""
listview functions (merge etc)
"""

@dajaxice_register
def merge_items(request, *args, **kwargs):

    log = logging.getLogger('alibrary.ajax.merge_items')


    print kwargs

    item_type = kwargs.get('item_type', None)
    item_ids = kwargs.get('item_ids', None)
    master_id = kwargs.get('master_id', None)

    slave_items = []
    master_item = None
    data = {
        'status': None,
        'error': None
    }


    if item_type and item_ids and master_id:
        log.debug('type: %s - ids: %s - master: %s' % (item_type, ', '.join(item_ids), master_id))
        try:

            if item_type == 'release':
                items = Release.objects.filter(pk__in=item_ids).exclude(pk=int(master_id))
                for item in items:
                    slave_items.append(item)

                master_item = Release.objects.get(pk=int(master_id))
                if slave_items and master_item:
                    merge_model_objects(master_item, slave_items)
                    master_item.save()
                    # needed to clear cache
                    for media in master_item.media_release.all():
                        media.save()
                    data['status'] = True
                else:
                    data['status'] = False
                    data['error'] = 'No selection'


            if item_type == 'media':
                items = Media.objects.filter(pk__in=item_ids).exclude(pk=int(master_id))
                for item in items:
                    slave_items.append(item)

                master_item = Media.objects.get(pk=int(master_id))
                if slave_items and master_item:
                    merge_model_objects(master_item, slave_items)
                    master_item.save()
                    data['status'] = True
                else:
                    data['status'] = False
                    data['error'] = 'No selection'

            if item_type == 'artist':
                items = Artist.objects.filter(pk__in=item_ids).exclude(pk=int(master_id))
                for item in items:
                    slave_items.append(item)

                master_item = Artist.objects.get(pk=int(master_id))
                if slave_items and master_item:
                    merge_model_objects(master_item, slave_items)
                    master_item.save()
                    # needed to clear cache
                    """"""
                    for media in master_item.media_artist.all():
                        media.save()

                    data['status'] = True
                else:
                    data['status'] = False
                    data['error'] = 'No selection'

            if item_type == 'label':
                items = Label.objects.filter(pk__in=item_ids).exclude(pk=int(master_id))
                for item in items:
                    slave_items.append(item)

                master_item = Label.objects.get(pk=int(master_id))
                if slave_items and master_item:
                    merge_model_objects(master_item, slave_items)
                    master_item.save()
                    # needed to clear cache
                    """
                    for media in master_item.media_release.all():
                        media.save()
                    """
                    data['status'] = True
                else:
                    data['status'] = False
                    data['error'] = 'No selection'



        except Exception, e:
            log.warning('%s' % e)
            data['status'] = False
            data['error'] = '%s' % e

    return json.dumps(data)






