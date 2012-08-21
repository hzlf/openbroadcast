# -*- coding: utf-8 -*-
from __future__ import with_statement
from cms.api import create_page, publish_page, add_plugin
from cms.conf.patch import post_patch_check
from cms.exceptions import PluginAlreadyRegistered, PluginNotRegistered
from cms.models import Page, Placeholder
from cms.models.pluginmodel import CMSPlugin, PluginModelBase
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.plugins.file.models import File
from cms.plugins.inherit.models import InheritPagePlaceholder
from cms.plugins.link.forms import LinkForm
from cms.plugins.link.models import Link
from cms.plugins.text.models import Text
from cms.plugins.text.utils import (plugin_tags_to_id_list, 
    plugin_tags_to_admin_html)
from cms.plugins.twitter.models import TwitterRecentEntries
from cms.test_utils.project.pluginapp.models import Article, Section
from cms.test_utils.project.pluginapp.plugins.manytomany_rel.models import (
    ArticlePluginModel)
from cms.test_utils.testcases import (CMSTestCase, URL_CMS_PAGE, 
    URL_CMS_PAGE_ADD, URL_CMS_PLUGIN_ADD, URL_CMS_PLUGIN_EDIT, URL_CMS_PAGE_CHANGE, URL_CMS_PLUGIN_REMOVE)
from cms.sitemaps.cms_sitemap import CMSSitemap
from cms.test_utils.util.context_managers import SettingsOverride
from cms.utils.copy_plugins import copy_plugins_to
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.forms.widgets import Media
from django.test.testcases import TestCase
import os
import datetime


class DumbFixturePlugin(CMSPluginBase):
    model = CMSPlugin
    name = "Dumb Test Plugin. It does nothing."
    render_template = ""
    admin_preview = False

    def render(self, context, instance, placeholder):
        return context

class PluginsTestBaseCase(CMSTestCase):

    def setUp(self):
        self.super_user = User(username="test", is_staff = True, is_active = True, is_superuser = True)
        self.super_user.set_password("test")
        self.super_user.save()

        self.slave = User(username="slave", is_staff=True, is_active=True, is_superuser=False)
        self.slave.set_password("slave")
        self.slave.save()


        self.FIRST_LANG = settings.LANGUAGES[0][0]
        self.SECOND_LANG = settings.LANGUAGES[1][0]
        
        self._login_context = self.login_user_context(self.super_user)
        self._login_context.__enter__()
    
    def tearDown(self):
        self._login_context.__exit__(None, None, None)

    def approve_page(self, page):
        response = self.client.get(URL_CMS_PAGE + "%d/approve/" % page.pk)
        self.assertRedirects(response, URL_CMS_PAGE)
        # reload page
        return self.reload_page(page)

    def get_request(self, *args, **kwargs):
        request = super(PluginsTestBaseCase, self).get_request(*args, **kwargs)
        request.placeholder_media = Media()
        return request


class PluginsTestCase(PluginsTestBaseCase):

    def _create_text_plugin_on_page(self, page):
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder':page.placeholders.get(slot="body").pk,
        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEquals(response.status_code, 200)
        created_plugin_id = int(response.content)
        self.assertEquals(created_plugin_id, CMSPlugin.objects.all()[0].pk)
        return created_plugin_id

    def _edit_text_plugin(self, plugin_id, text):
        edit_url = "%s%s/" % (URL_CMS_PLUGIN_EDIT, plugin_id) 
        response = self.client.get(edit_url)
        self.assertEquals(response.status_code, 200)
        data = {
            "body": text
        }
        response = self.client.post(edit_url, data)
        self.assertEquals(response.status_code, 200)
        txt = Text.objects.get(pk=plugin_id)
        return txt

    def test_add_edit_plugin(self):
        """
        Test that you can add a text plugin
        """
        # add a new text plugin
        page_data = self.get_new_page_data()
        response = self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]
        created_plugin_id = self._create_text_plugin_on_page(page)
        # now edit the plugin
        txt = self._edit_text_plugin(created_plugin_id, "Hello World")
        self.assertEquals("Hello World", txt.body)
        # edit body, but click cancel button
        data = {
            "body":"Hello World!!",
            "_cancel":True,
        }
        response = self.client.post(URL_CMS_PAGE_ADD, data)
        self.assertEquals(response.status_code, 200)
        txt = Text.objects.all()[0]
        self.assertEquals("Hello World", txt.body)


    def test_plugin_order(self):
        """
        Test that plugin position is saved after creation
        """
        page_en = create_page("PluginOrderPage", "col_two.html", "en",
                              slug="page1",published=True, in_navigation=True)
        ph_en = page_en.placeholders.get(slot="col_left")

        # We check created objects and objects from the DB to be sure the position value
        # has been saved correctly
        text_plugin_1 = add_plugin(ph_en, "TextPlugin", "en", body="I'm the first")
        text_plugin_2 = add_plugin(ph_en, "TextPlugin", "en", body="I'm the second")
        db_plugin_1 = CMSPlugin.objects.get(pk=text_plugin_1.pk)
        db_plugin_2 = CMSPlugin.objects.get(pk=text_plugin_2.pk)

        with SettingsOverride(CMS_MODERATOR=False, CMS_PERMISSION=False):
            self.assertEqual(text_plugin_1.position,1)
            self.assertEqual(db_plugin_1.position,1)
            self.assertEqual(text_plugin_2.position,2)
            self.assertEqual(db_plugin_2.position,2)
            ## Finally we render the placeholder to test the actual content
            rendered_placeholder = ph_en.render(self.get_context(page_en.get_absolute_url()),None)
            self.assertEquals(rendered_placeholder,"I'm the firstI'm the second")

    def test_add_cancel_plugin(self):
        """
        Test that you can cancel a new plugin before editing and 
        that the plugin is removed.
        """
        # add a new text plugin
        page_data = self.get_new_page_data()
        response = self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder':page.placeholders.get(slot="body").pk,
        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)
        # now click cancel instead of editing
        edit_url = URL_CMS_PLUGIN_EDIT + response.content + "/"
        response = self.client.get(edit_url)
        self.assertEquals(response.status_code, 200)
        data = {
            "body":"Hello World",
            "_cancel":True,
        }
        response = self.client.post(edit_url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(0, Text.objects.count())

    def test_add_text_plugin_empty_tag(self):
        """
        Test that you can add a text plugin
        """
        # add a new text plugin
        page_data = self.get_new_page_data()
        response = self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder':page.placeholders.get(slot="body").pk,
            }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)
        # now edit the plugin
        edit_url = URL_CMS_PLUGIN_EDIT + response.content + "/"
        response = self.client.get(edit_url)
        self.assertEquals(response.status_code, 200)
        data = {
            "body":'<div class="someclass"></div><p>foo</p>'
        }
        response = self.client.post(edit_url, data)
        self.assertEquals(response.status_code, 200)
        txt = Text.objects.all()[0]
        self.assertEquals('<div class="someclass"></div><p>foo</p>', txt.body)

    def test_add_text_plugin_html_sanitizer(self):
        """
        Test that you can add a text plugin
        """
        # add a new text plugin
        page_data = self.get_new_page_data()
        response = self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder':page.placeholders.get(slot="body").pk,
            }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)
        # now edit the plugin
        edit_url = URL_CMS_PLUGIN_EDIT + response.content + "/"
        response = self.client.get(edit_url)
        self.assertEquals(response.status_code, 200)
        data = {
            "body":'<script>var bar="hacked"</script>'
        }
        response = self.client.post(edit_url, data)
        self.assertEquals(response.status_code, 200)
        txt = Text.objects.all()[0]
        self.assertEquals('&lt;script&gt;var bar="hacked"&lt;/script&gt;', txt.body)

    def test_copy_plugins(self):
        """
        Test that copying plugins works as expected.
        """
        # create some objects
        page_en = create_page("CopyPluginTestPage (EN)", "nav_playground.html", "en")
        page_de = create_page("CopyPluginTestPage (DE)", "nav_playground.html", "de")
        ph_en = page_en.placeholders.get(slot="body")
        ph_de = page_de.placeholders.get(slot="body")
        
        # add the text plugin
        text_plugin_en = add_plugin(ph_en, "TextPlugin", "en", body="Hello World")
        self.assertEquals(text_plugin_en.pk, CMSPlugin.objects.all()[0].pk)
        
        # add a *nested* link plugin
        link_plugin_en = add_plugin(ph_en, "LinkPlugin", "en", target=text_plugin_en,
                                 name="A Link", url="https://www.django-cms.org")
        
        # the call above to add a child makes a plugin reload required here.
        text_plugin_en = self.reload(text_plugin_en)
        
        # check the relations
        self.assertEquals(text_plugin_en.get_children().count(), 1)
        self.assertEqual(link_plugin_en.parent.pk, text_plugin_en.pk)
        
        # just sanity check that so far everything went well
        self.assertEqual(CMSPlugin.objects.count(), 2)
        
        # copy the plugins to the german placeholder
        copy_plugins_to(ph_en.cmsplugin_set.all(), ph_de, 'de')
        
        self.assertEqual(ph_de.cmsplugin_set.filter(parent=None).count(), 1)
        text_plugin_de = ph_de.cmsplugin_set.get(parent=None).get_plugin_instance()[0]
        self.assertEqual(text_plugin_de.get_children().count(), 1)
        link_plugin_de = text_plugin_de.get_children().get().get_plugin_instance()[0]
        
        
        # check we have twice as many plugins as before
        self.assertEqual(CMSPlugin.objects.count(), 4)
        
        # check language plugins
        self.assertEqual(CMSPlugin.objects.filter(language='de').count(), 2)
        self.assertEqual(CMSPlugin.objects.filter(language='en').count(), 2)
        
        
        text_plugin_en = self.reload(text_plugin_en)
        link_plugin_en = self.reload(link_plugin_en)
        
        # check the relations in english didn't change
        self.assertEquals(text_plugin_en.get_children().count(), 1)
        self.assertEqual(link_plugin_en.parent.pk, text_plugin_en.pk)
        
        self.assertEqual(link_plugin_de.name, link_plugin_en.name)
        self.assertEqual(link_plugin_de.url, link_plugin_en.url)
        
        self.assertEqual(text_plugin_de.body, text_plugin_en.body)
        

    def test_remove_plugin_before_published(self):
        """
        When removing a draft plugin we would expect the public copy of the plugin to also be removed
        """
        # add a page
        page_data = self.get_new_page_data()
        response = self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]

        # add a plugin
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder':page.placeholders.get(slot="body").pk,
        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)
        # there should be only 1 plugin
        self.assertEquals(CMSPlugin.objects.all().count(), 1)

        # delete the plugin
        plugin_data = {
            'plugin_id': int(response.content)
        }
        remove_url = URL_CMS_PLUGIN_REMOVE
        response = self.client.post(remove_url, plugin_data)
        self.assertEquals(response.status_code, 200)
        # there should be no plugins
        self.assertEquals(0, CMSPlugin.objects.all().count())

    def test_remove_plugin_after_published(self):
        # add a page
        page_data = self.get_new_page_data()
        response = self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]

        # add a plugin
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder':page.placeholders.get(slot="body").pk,
        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        plugin_id = int(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)

        # there should be only 1 plugin
        self.assertEquals(CMSPlugin.objects.all().count(), 1)

        # publish page
        response = self.client.post(URL_CMS_PAGE + "%d/change-status/" % page.pk, {1 :1})
        self.assertEqual(response.status_code, 200)

        # there should now be two plugins - 1 draft, 1 public
        self.assertEquals(CMSPlugin.objects.all().count(), 2)

        # delete the plugin
        plugin_data = {
            'plugin_id': plugin_id
        }
        remove_url = URL_CMS_PLUGIN_REMOVE
        response = self.client.post(remove_url, plugin_data)
        self.assertEquals(response.status_code, 200)

        # there should be no plugins
        self.assertEquals(CMSPlugin.objects.all().count(), 0)

    def test_remove_plugin_not_associated_to_page(self):
        """
        Test case for PlaceholderField
        """
        page_data = self.get_new_page_data()
        response = self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]

        # add a plugin
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder':page.placeholders.get(slot="body").pk,
        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)

        # there should be only 1 plugin
        self.assertEquals(CMSPlugin.objects.all().count(), 1)

        ph = Placeholder(slot="subplugin")
        ph.save()
        plugin_data = {
            'plugin_type':"TextPlugin",
            'language':settings.LANGUAGES[0][0],
            'placeholder': ph.pk,
            'parent': int(response.content)
        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        # no longer allowed for security reasons
        self.assertEqual(response.status_code, 404)

    def test_register_plugin_twice_should_raise(self):
        number_of_plugins_before = len(plugin_pool.get_all_plugins())
        # The first time we register the plugin is should work
        plugin_pool.register_plugin(DumbFixturePlugin)
        # Let's add it a second time. We should catch and exception
        raised = False
        try:
            plugin_pool.register_plugin(DumbFixturePlugin)
        except PluginAlreadyRegistered:
            raised = True
        self.assertTrue(raised)
        # Let's also unregister the plugin now, and assert it's not in the
        # pool anymore
        plugin_pool.unregister_plugin(DumbFixturePlugin)
        # Let's make sure we have the same number of plugins as before:
        number_of_plugins_after = len(plugin_pool.get_all_plugins())
        self.assertEqual(number_of_plugins_before, number_of_plugins_after)

    def test_unregister_non_existing_plugin_should_raise(self):
        number_of_plugins_before = len(plugin_pool.get_all_plugins())
        raised = False
        try:
            # There should not be such a plugin registered if the others tests
            # don't leak plugins
            plugin_pool.unregister_plugin(DumbFixturePlugin)
        except PluginNotRegistered:
            raised = True
        self.assertTrue(raised)
        # Let's count, to make sure we didn't remove a plugin accidentally.
        number_of_plugins_after = len(plugin_pool.get_all_plugins())
        self.assertEqual(number_of_plugins_before, number_of_plugins_after)
                
    def test_inheritplugin_media(self):
        """
        Test case for InheritPagePlaceholder
        """
        with SettingsOverride(CMS_MODERATOR=False):
            inheritfrompage = create_page('page to inherit from',
                                          'nav_playground.html',
                                          'en')
            
            body = inheritfrompage.placeholders.get(slot="body")
            
            plugin = TwitterRecentEntries(
                plugin_type='TwitterRecentEntriesPlugin',
                placeholder=body, 
                position=1, 
                language=settings.LANGUAGE_CODE,
                twitter_user='djangocms',
            )
            plugin.insert_at(None, position='last-child', save=True)
            
            page = create_page('inherit from page',
                               'nav_playground.html',
                               'en',
                               published=True)
            
            inherited_body = page.placeholders.get(slot="body")
                    
            inherit_plugin = InheritPagePlaceholder(
                plugin_type='InheritPagePlaceholderPlugin',
                placeholder=inherited_body, 
                position=1, 
                language=settings.LANGUAGE_CODE,
                from_page=inheritfrompage,
                from_language=settings.LANGUAGE_CODE)
            inherit_plugin.insert_at(None, position='last-child', save=True)
            
            self.client.logout()
            response = self.client.get(page.get_absolute_url())
            self.assertTrue('%scms/js/libs/jquery.tweet.js' % settings.STATIC_URL in response.content, response.content)

    def test_render_textplugin(self):
        # Setup
        page = create_page("render test", "nav_playground.html", "en")
        ph = page.placeholders.get(slot="body")
        text_plugin = add_plugin(ph, "TextPlugin", "en", body="Hello World")
        link_plugins = []
        for i in range(0, 10):
            link_plugins.append(add_plugin(ph, "LinkPlugin", "en",
                target=text_plugin,
                name="A Link %d" % i,
                url="http://django-cms.org"))
            text_plugin.text.body += '<img src="/static/cms/images/plugins/link.png" alt="Link - %s" id="plugin_obj_%d" title="Link - %s" />' % (
                link_plugins[-1].name,
                link_plugins[-1].pk,
                link_plugins[-1].name,
            )
        text_plugin.save()
        txt = text_plugin.text
        ph = Placeholder.objects.get(pk=ph.pk)
        with self.assertNumQueries(2):
            # 1 query for the CMSPlugin objects,
            # 1 query for each type of child object (1 in this case, all are Link plugins)
            txt.body = plugin_tags_to_admin_html(
                '\n'.join(["{{ plugin_object %d }}" % l.cmsplugin_ptr_id
                           for l in link_plugins]))
        txt.save()
        text_plugin = self.reload(text_plugin)

        with self.assertNumQueries(2):
            rendered = text_plugin.render_plugin(placeholder=ph)
        for i in range(0, 10):
            self.assertTrue('A Link %d' % i in rendered)

    def test_copy_textplugin(self):
        """
        Test that copying of textplugins replaces references to copied plugins
        """
        page = create_page("page", "nav_playground.html", "en")
        
        placeholder = page.placeholders.get(slot='body')

        plugin_base = CMSPlugin(
            plugin_type='TextPlugin',
            placeholder=placeholder,
            position=1,
            language=self.FIRST_LANG)
        plugin_base.insert_at(None, position='last-child', save=False)

        plugin = Text(body='')
        plugin_base.set_base_attr(plugin)
        plugin.save()

        plugin_ref_1_base = CMSPlugin(
            plugin_type='TextPlugin',
            placeholder=placeholder,
            position=1,
            language=self.FIRST_LANG)
        plugin_ref_1_base.insert_at(plugin_base, position='last-child', save=False)

        plugin_ref_1 = Text(body='')
        plugin_ref_1_base.set_base_attr(plugin_ref_1)
        plugin_ref_1.save()

        plugin_ref_2_base = CMSPlugin(
            plugin_type='TextPlugin',
            placeholder=placeholder,
            position=2,
            language=self.FIRST_LANG)
        plugin_ref_2_base.insert_at(plugin_base, position='last-child', save=False)

        plugin_ref_2 = Text(body='')
        plugin_ref_2_base.set_base_attr(plugin_ref_2)

        plugin_ref_2.save()

        plugin.body = plugin_tags_to_admin_html(' {{ plugin_object %s }} {{ plugin_object %s }} ' % (str(plugin_ref_1.pk), str(plugin_ref_2.pk)))
        plugin.save()
        self.assertEquals(plugin.pk, 1)
        page_data = self.get_new_page_data()

        #create 2nd language page
        page_data.update({
            'language': self.SECOND_LANG,
            'title': "%s %s" % (page.get_title(), self.SECOND_LANG),
        })
        response = self.client.post(URL_CMS_PAGE_CHANGE % page.pk + "?language=%s" % self.SECOND_LANG, page_data)
        self.assertRedirects(response, URL_CMS_PAGE)

        self.assertEquals(CMSPlugin.objects.filter(language=self.FIRST_LANG).count(), 3)
        self.assertEquals(CMSPlugin.objects.filter(language=self.SECOND_LANG).count(), 0)
        self.assertEquals(CMSPlugin.objects.count(), 3)
        self.assertEquals(Page.objects.all().count(), 1)

        copy_data = {
            'placeholder': placeholder.pk,
            'language': self.SECOND_LANG,
            'copy_from': self.FIRST_LANG,
        }
        response = self.client.post(URL_CMS_PAGE + "copy-plugins/", copy_data)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.count('<li '), 3)
        # assert copy success
        self.assertEquals(CMSPlugin.objects.filter(language=self.FIRST_LANG).count(), 3)
        self.assertEquals(CMSPlugin.objects.filter(language=self.SECOND_LANG).count(), 3)
        self.assertEquals(CMSPlugin.objects.count(), 6)

        new_plugin = Text.objects.get(pk=6)
        idlist = sorted(plugin_tags_to_id_list(new_plugin.body))
        expected = sorted([4, 5])
        self.assertEquals(idlist, expected)

    def test_empty_plugin_is_ignored(self):
        page = create_page("page", "nav_playground.html", "en")

        placeholder = page.placeholders.get(slot='body')

        plugin = CMSPlugin(
            plugin_type='TextPlugin',
            placeholder=placeholder,
            position=1,
            language=self.FIRST_LANG)
        plugin.insert_at(None, position='last-child', save=True)

        # this should not raise any errors, but just ignore the empty plugin
        out = placeholder.render(self.get_context(), width=300)
        self.assertFalse(len(out))
        self.assertFalse(len(placeholder._en_plugins_cache))

    def test_editing_plugin_changes_page_modification_time_in_sitemap(self):
        now = datetime.datetime.now()
        one_day_ago = now - datetime.timedelta(days=1)
        page = create_page("page", "nav_playground.html", "en", published=True, publication_date=now)
        page.creation_date = one_day_ago
        page.changed_date = one_day_ago

        plugin_id = self._create_text_plugin_on_page(page)
        plugin = self._edit_text_plugin(plugin_id, "fnord")

        actual_last_modification_time = CMSSitemap().lastmod(page)
        self.assertEqual(plugin.changed_date, actual_last_modification_time)


class FileSystemPluginTests(PluginsTestBaseCase):
    def setUp(self):
        super(FileSystemPluginTests, self).setUp()
        call_command('collectstatic', interactive=False, verbosity=0, link=True)
        
    def tearDown(self):
        for directory in [settings.STATIC_ROOT, settings.MEDIA_ROOT]:
            for root, dirs, files in os.walk(directory, topdown=False):
                # We need to walk() the directory tree since rmdir() does not allow
                # to remove non-empty directories...
                for name in files:
                    # Start by killing all files we walked
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    # Now all directories we walked...
                    os.rmdir(os.path.join(root, name))
        super(FileSystemPluginTests, self).tearDown()
        
    def test_fileplugin_icon_uppercase(self):
        page = create_page('testpage', 'nav_playground.html', 'en')
        body = page.placeholders.get(slot="body") 
        plugin = File(
            plugin_type='FilePlugin',
            placeholder=body,
            position=1,
            language=settings.LANGUAGE_CODE,
        )
        plugin.file.save("UPPERCASE.JPG", SimpleUploadedFile("UPPERCASE.jpg", "content"), False)
        plugin.insert_at(None, position='last-child', save=True)
        self.assertNotEquals(plugin.get_icon_url().find('jpg'), -1)




class PluginManyToManyTestCase(PluginsTestBaseCase):

    def setUp(self):
        self.super_user = User(username="test", is_staff = True, is_active = True, is_superuser = True)
        self.super_user.set_password("test")
        self.super_user.save()

        self.slave = User(username="slave", is_staff=True, is_active=True, is_superuser=False)
        self.slave.set_password("slave")
        self.slave.save()
        
        self._login_context = self.login_user_context(self.super_user)
        self._login_context.__enter__()
    
        # create 3 sections
        self.sections = []
        self.section_pks = []
        for i in range(3):
            section = Section.objects.create(name="section %s" %i)
            self.sections.append(section)
            self.section_pks.append(section.pk)
        self.section_count = len(self.sections)
        # create 10 articles by section
        for section in self.sections:
            for j in range(10):
                Article.objects.create(
                    title="article %s" % j,
                    section=section
                )
        self.FIRST_LANG = settings.LANGUAGES[0][0]
        self.SECOND_LANG = settings.LANGUAGES[1][0]
    
    def test_add_plugin_with_m2m(self):
        # add a new text plugin
        page_data = self.get_new_page_data()
        self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]
        placeholder = page.placeholders.get(slot="body")
        plugin_data = {
            'plugin_type': "ArticlePlugin",
            'language': self.FIRST_LANG,
            'placeholder': placeholder.pk,
        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)
        # now edit the plugin
        edit_url = URL_CMS_PLUGIN_EDIT + response.content + "/"
        response = self.client.get(edit_url)
        self.assertEquals(response.status_code, 200)
        data = {
            'title': "Articles Plugin 1",
            "sections": self.section_pks
        }
        response = self.client.post(edit_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ArticlePluginModel.objects.count(), 1)
        plugin = ArticlePluginModel.objects.all()[0]
        self.assertEquals(self.section_count, plugin.sections.count())

    def test_add_plugin_with_m2m_and_publisher(self):
        page_data = self.get_new_page_data()
        self.client.post(URL_CMS_PAGE_ADD, page_data)
        page = Page.objects.all()[0]
        placeholder = page.placeholders.get(slot="body")

        # add a plugin
        plugin_data = {
            'plugin_type': "ArticlePlugin",
            'language': self.FIRST_LANG,
            'placeholder': placeholder.pk,

        }
        response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(int(response.content), CMSPlugin.objects.all()[0].pk)

        # there should be only 1 plugin
        self.assertEquals(1, CMSPlugin.objects.all().count())

        articles_plugin_pk = int(response.content)
        self.assertEquals(articles_plugin_pk, CMSPlugin.objects.all()[0].pk)
        # now edit the plugin
        edit_url = URL_CMS_PLUGIN_EDIT + response.content + "/"

        data = {
            'title': "Articles Plugin 1",
            'sections': self.section_pks
        }
        response = self.client.post(edit_url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(1, ArticlePluginModel.objects.count())
        articles_plugin = ArticlePluginModel.objects.all()[0]
        self.assertEquals(u'Articles Plugin 1', articles_plugin.title)
        self.assertEquals(self.section_count, articles_plugin.sections.count())


        # check publish box
        page = publish_page(page, self.super_user)

        # there should now be two plugins - 1 draft, 1 public
        self.assertEquals(2, ArticlePluginModel.objects.all().count())

        db_counts = [plugin.sections.count() for plugin in ArticlePluginModel.objects.all()]
        expected = [self.section_count for i in range(len(db_counts))]
        self.assertEqual(expected, db_counts)


    def test_copy_plugin_with_m2m(self):
        page = create_page("page", "nav_playground.html", "en")
        
        placeholder = page.placeholders.get(slot='body')

        plugin = ArticlePluginModel(
            plugin_type='ArticlePlugin',
            placeholder=placeholder,
            position=1,
            language=self.FIRST_LANG)
        plugin.insert_at(None, position='last-child', save=True)

        edit_url = URL_CMS_PLUGIN_EDIT + str(plugin.pk) + "/"

        data = {
            'title': "Articles Plugin 1",
            "sections": self.section_pks
        }
        response = self.client.post(edit_url, data)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(ArticlePluginModel.objects.count(), 1)

        self.assertEqual(ArticlePluginModel.objects.all()[0].sections.count(), self.section_count)

        page_data = self.get_new_page_data()

        #create 2nd language page
        page_data.update({
            'language': self.SECOND_LANG,
            'title': "%s %s" % (page.get_title(), self.SECOND_LANG),
        })
        response = self.client.post(URL_CMS_PAGE_CHANGE % page.pk + "?language=%s" % self.SECOND_LANG, page_data)
        self.assertRedirects(response, URL_CMS_PAGE)

        self.assertEquals(CMSPlugin.objects.filter(language=self.FIRST_LANG).count(), 1)
        self.assertEquals(CMSPlugin.objects.filter(language=self.SECOND_LANG).count(), 0)
        self.assertEquals(CMSPlugin.objects.count(), 1)
        self.assertEquals(Page.objects.all().count(), 1)
        copy_data = {
            'placeholder': placeholder.pk,
            'language': self.SECOND_LANG,
            'copy_from': self.FIRST_LANG,
        }
        response = self.client.post(URL_CMS_PAGE + "copy-plugins/", copy_data)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.count('<li '), 1)
        # assert copy success
        self.assertEquals(CMSPlugin.objects.filter(language=self.FIRST_LANG).count(), 1)
        self.assertEquals(CMSPlugin.objects.filter(language=self.SECOND_LANG).count(), 1)
        self.assertEquals(CMSPlugin.objects.count(), 2)
        db_counts = [plugin.sections.count() for plugin in ArticlePluginModel.objects.all()]
        expected = [self.section_count for i in range(len(db_counts))]
        self.assertEqual(expected, db_counts)

class PluginsMetaOptionsTests(TestCase):
    ''' TestCase set for ensuring that bugs like #992 are caught '''

    # these plugins are inlined because, due to the nature of the #992
    # ticket, we cannot actually import a single file with all the
    # plugin variants in, because that calls __new__, at which point the
    # error with splitted occurs.

    def test_meta_options_as_defaults(self):
        ''' handling when a CMSPlugin meta options are computed defaults '''
        # this plugin relies on the base CMSPlugin and Model classes to
        # decide what the app_label and db_table should be
        class TestPlugin(CMSPlugin):
            pass

        plugin = TestPlugin()
        self.assertEqual(plugin._meta.db_table, 'cmsplugin_testplugin')
        self.assertEqual(plugin._meta.app_label, 'tests') # because it's inlined

    def test_meta_options_as_declared_defaults(self):
        ''' handling when a CMSPlugin meta options are declared as per defaults '''
        # here, we declare the db_table and app_label explicitly, but to the same
        # values as would be computed, thus making sure it's not a problem to
        # supply options.
        class TestPlugin2(CMSPlugin):
            class Meta:
                db_table = 'cmsplugin_testplugin2'
                app_label = 'tests'

        plugin = TestPlugin2()
        self.assertEqual(plugin._meta.db_table, 'cmsplugin_testplugin2')
        self.assertEqual(plugin._meta.app_label, 'tests') # because it's inlined

    def test_meta_options_custom_app_label(self):
        ''' make sure customised meta options on CMSPlugins don't break things '''

        class TestPlugin3(CMSPlugin):
            class Meta:
                app_label = 'one_thing'

        plugin = TestPlugin3()
        self.assertEqual(plugin._meta.db_table, 'cmsplugin_testplugin3') # because it's inlined
        self.assertEqual(plugin._meta.app_label, 'one_thing')

    def test_meta_options_custom_db_table(self):
        ''' make sure custom database table names are OK. '''
        class TestPlugin4(CMSPlugin):
            class Meta:
                db_table = 'or_another'

        plugin = TestPlugin4()
        self.assertEqual(plugin._meta.db_table, 'or_another')
        self.assertEqual(plugin._meta.app_label, 'tests') # because it's inlined

    def test_meta_options_custom_both(self):
        ''' We should be able to customise app_label and db_table together '''
        class TestPlugin5(CMSPlugin):
            class Meta:
                app_label = 'one_thing'
                db_table = 'or_another'

        plugin = TestPlugin5()
        self.assertEqual(plugin._meta.db_table, 'or_another')
        self.assertEqual(plugin._meta.app_label, 'one_thing')

class SekizaiTests(TestCase):
    def test_post_patch_check(self):
        post_patch_check()
         
    def test_fail(self):
        with SettingsOverride(CMS_TEMPLATES=[('fail.html', 'fail')]):
            self.assertRaises(ImproperlyConfigured, post_patch_check)


class LinkPluginTestCase(PluginsTestBaseCase):
    def test_does_not_verify_existance_of_url(self):
        form = LinkForm(
            {'name': 'Linkname', 'url': 'http://www.nonexistant.test'})
        self.assertTrue(form.is_valid())

    def test_opens_in_same_window_by_default(self):
        """Could not figure out how to render this plugin

        Checking only for the values in the model"""
        form = LinkForm({'name': 'Linkname',
            'url': 'http://www.nonexistant.test'})
        link = form.save()
        self.assertEquals(link.target, '')

    def test_open_in_blank_window(self):
        form = LinkForm({'name': 'Linkname',
            'url': 'http://www.nonexistant.test', 'target' : '_blank'})
        link = form.save()
        self.assertEquals(link.target, '_blank')

    def test_open_in_parent_window(self):
        form = LinkForm({'name': 'Linkname',
            'url': 'http://www.nonexistant.test', 'target' : '_parent'})
        link = form.save()
        self.assertEquals(link.target, '_parent')

    def test_open_in_top_window(self):
        form = LinkForm({'name': 'Linkname',
            'url': 'http://www.nonexistant.test', 'target' : '_top'})
        link = form.save()
        self.assertEquals(link.target, '_top')

    def test_open_in_nothing_else(self):
        form = LinkForm({'name': 'Linkname',
            'url': 'http://www.nonexistant.test', 'target' : 'artificial'})
        self.assertFalse(form.is_valid())

class NoDatabasePluginTests(TestCase):
    def test_render_meta_is_unique(self):
        text = Text()
        link = Link()
        self.assertNotEqual(id(text._render_meta), id(link._render_meta))
    
    def test_render_meta_does_not_leak(self):
        text = Text()
        link = Link()
        
        text._render_meta.text_enabled = False
        link._render_meta.text_enabled = False
        
        self.assertFalse(text._render_meta.text_enabled)
        self.assertFalse(link._render_meta.text_enabled)
        
        link._render_meta.text_enabled = True

        self.assertFalse(text._render_meta.text_enabled)
        self.assertTrue(link._render_meta.text_enabled)
    
    def test_db_table_hack(self):
        # TODO: Django tests seem to leak models from test methods, somehow
        # we should clear django.db.models.loading.app_cache in tearDown.
        plugin_class = PluginModelBase('TestPlugin', (CMSPlugin,), {'__module__': 'cms.tests.plugins'})
        self.assertEqual(plugin_class._meta.db_table, 'cmsplugin_testplugin')
    
    def test_db_table_hack_with_mixin(self):
        class LeftMixin: pass
        class RightMixin: pass
        plugin_class = PluginModelBase('TestPlugin2', (LeftMixin, CMSPlugin, RightMixin), {'__module__': 'cms.tests.plugins'})
        self.assertEqual(plugin_class._meta.db_table, 'cmsplugin_testplugin2')
