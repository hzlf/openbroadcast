from django.db import models
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin

from django.utils.translation import ugettext as _

from alabel.models import MediaPlugin as MediaPluginModel
from alabel.models import ReleasePlugin as ReleasePluginModel


@plugin_pool.register_plugin
class MediaPlugin(CMSPluginBase):
    model = MediaPluginModel
    name = _("Track Plugin")
    render_template = "alabel/cmsplugin/media.html"

    # meta
    class Meta:
        app_label = 'alabel'

    def render(self, context, instance, placeholder):

   
        context.update({
            'instance': instance,
            'object': instance.media,
            'media': instance.media,
            'placeholder': placeholder,
        })
        return context


@plugin_pool.register_plugin
class ReleasePlugin(CMSPluginBase):
    model = ReleasePluginModel
    name = _("Release Plugin")
    render_template = "alabel/cmsplugin/release.html"

    # meta
    class Meta:
        app_label = 'alabel'

    def render(self, context, instance, placeholder):

   
        context.update({
            'instance': instance,
            'object': instance.release,
            'item': instance.release,
            'release': instance.release,
            'placeholder': placeholder,
        })
        return context
