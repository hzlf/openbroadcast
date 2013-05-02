from __future__ import unicode_literals

import random
import string
from xml.dom.minidom import parseString

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe

from selectable.base import ModelLookup
from selectable.tests import Thing

__all__ = (
    'ModelLookupTestCase',
    'MultiFieldLookupTestCase',
    'LookupEscapingTestCase',
)


def as_xml(html):
    "Convert HTML portion to minidom node."
    return parseString('<root>%s</root>' % html)


def parsed_inputs(html):
    "Returns a dictionary mapping name --> node of inputs found in the HTML."
    node = as_xml(html)
    inputs = {}
    for field in node.getElementsByTagName('input'):
        name = dict(field.attributes.items())['name']
        current = inputs.get(name, [])
        current.append(field)
        inputs[name] = current
    return inputs


class PatchSettingsMixin(object):
    def setUp(self):
        super(PatchSettingsMixin, self).setUp()
        self.is_limit_set = hasattr(settings, 'SELECTABLE_MAX_LIMIT')
        if self.is_limit_set:
            self.original_limit = settings.SELECTABLE_MAX_LIMIT
        settings.SELECTABLE_MAX_LIMIT = 25

    def tearDown(self):
        super(PatchSettingsMixin, self).tearDown()
        if self.is_limit_set:
            settings.SELECTABLE_MAX_LIMIT = self.original_limit


class BaseSelectableTestCase(TestCase):
    urls = 'selectable.tests.urls'

    def get_random_string(self, length=10):
        return ''.join(random.choice(string.ascii_letters) for x in range(length))

    def create_thing(self, data=None):
        data = data or {}
        defaults = {
            'name': self.get_random_string(),
            'description': self.get_random_string(),
        }
        defaults.update(data)
        return Thing.objects.create(**defaults)


class SimpleModelLookup(ModelLookup):
    model = Thing
    search_fields = ('name__icontains', )


class ModelLookupTestCase(BaseSelectableTestCase):
    lookup_cls = SimpleModelLookup

    def get_lookup_instance(self):
        return self.__class__.lookup_cls()

    def test_get_name(self):
        name = self.__class__.lookup_cls.name()
        self.assertEqual(name, 'tests-simplemodellookup')

    def test_get_url(self):
        url = self.__class__.lookup_cls.url()
        test_url = reverse('selectable-lookup', args=['tests-simplemodellookup'])
        self.assertEqual(url, test_url)

    def test_format_item(self):
        lookup = self.get_lookup_instance()
        thing = Thing()
        item_info = lookup.format_item(thing)
        self.assertTrue('id' in item_info)
        self.assertTrue('value' in item_info)
        self.assertTrue('label' in item_info)

    def test_get_query(self):
        lookup = self.get_lookup_instance()
        thing = self.create_thing(data={'name': 'Thing'})
        other_thing = self.create_thing(data={'name': 'Other Thing'})
        qs = lookup.get_query(request=None, term='other')
        self.assertTrue(thing.pk not in qs.values_list('id', flat=True))
        self.assertTrue(other_thing.pk in qs.values_list('id', flat=True))

    def test_create_item(self):
        value = self.get_random_string()
        lookup = self.get_lookup_instance()
        thing = lookup.create_item(value)
        self.assertEqual(thing.__class__, Thing)
        self.assertEqual(thing.name, value)
        self.assertFalse(thing.pk)

    def test_get_item(self):
        lookup = self.get_lookup_instance()
        thing = self.create_thing(data={'name': 'Thing'})
        item = lookup.get_item(thing.pk)
        self.assertEqual(thing, item)

    def test_format_item_escaping(self):
        "Id, value and label should be escaped."
        lookup = self.get_lookup_instance()
        thing = self.create_thing(data={'name': 'Thing'})
        item_info = lookup.format_item(thing)
        self.assertFalse(isinstance(item_info['id'], SafeData))
        self.assertFalse(isinstance(item_info['value'], SafeData))
        self.assertTrue(isinstance(item_info['label'], SafeData))


class MultiFieldLookup(ModelLookup):
    model = Thing
    search_fields = ('name__icontains', 'description__icontains', )


class MultiFieldLookupTestCase(ModelLookupTestCase):
    lookup_cls = MultiFieldLookup

    def test_get_name(self):
        name = self.__class__.lookup_cls.name()
        self.assertEqual(name, 'tests-multifieldlookup')

    def test_get_url(self):
        url = self.__class__.lookup_cls.url()
        test_url = reverse('selectable-lookup', args=['tests-multifieldlookup'])
        self.assertEqual(url, test_url)

    def test_description_search(self):
        lookup = self.get_lookup_instance()
        thing = self.create_thing(data={'description': 'Thing'})
        other_thing = self.create_thing(data={'description': 'Other Thing'})
        qs = lookup.get_query(request=None, term='other')
        self.assertTrue(thing.pk not in qs.values_list('id', flat=True))
        self.assertTrue(other_thing.pk in qs.values_list('id', flat=True))


class HTMLLookup(ModelLookup):
    model = Thing
    search_fields = ('name__icontains', )


class SafeHTMLLookup(ModelLookup):
    model = Thing
    search_fields = ('name__icontains', )

    def get_item_label(self, item):
        "Mark label as safe."
        return mark_safe(item.name)


class LookupEscapingTestCase(BaseSelectableTestCase):

    def test_escape_html(self):
        "HTML should be escaped by default."
        lookup = HTMLLookup()
        bad_name = "<script>alert('hacked');</script>"
        escaped_name = escape(bad_name)
        thing = self.create_thing(data={'name': bad_name})
        item_info = lookup.format_item(thing)
        self.assertEqual(item_info['label'], escaped_name)

    def test_conditional_escape(self):
        "Methods should be able to mark values as safe."
        lookup = SafeHTMLLookup()
        bad_name = "<script>alert('hacked');</script>"
        escaped_name = escape(bad_name)
        thing = self.create_thing(data={'name': bad_name})
        item_info = lookup.format_item(thing)
        self.assertEqual(item_info['label'], bad_name)
