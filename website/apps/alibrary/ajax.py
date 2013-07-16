from django.core import serializers

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from alibrary.models import APILookup, Release, Relation

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

    try:
        if item_type == 'release':
            r = Release.objects.get(pk=item_id)
            ctype = ContentType.objects.get_for_model(r)
            al, created = APILookup.objects.get_or_create(content_type=ctype, object_id=r.id, provider=provider)
            if created:
                log.debug('APILookup created: %s' % (al.pk))


        data = al.get_from_api()


        # js = serializers.get_serializer("json")()
        #data = js.serialize(data, ensure_ascii=False)

        print '***** LOOKUP DATA ***************************'
        print data
        print '*********************************************'



        data = json.dumps(data, encoding="utf-8", ensure_ascii=False)


        return data

    except Exception, e:
        log.warning('%s' % e)
        return None


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
            #al, created = APILookup.objects.get_or_create(content_type=ctype, object_id=r.id, provider=provider)

        data = {'query': '%s %s' % (item.name, item.get_artists()[0])}
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

        if item and uri:
            rel = Relation(content_object=item, url=uri)
            rel.save()

        data = {
            'service': '%s' % rel.service,
            'url': '%s' % rel.url,
            }
        return json.dumps(data)

    except Exception, e:
        log.warning('%s' % e)
        return None
