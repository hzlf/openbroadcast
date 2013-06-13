from django.db import models
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin

from django.utils.translation import ugettext as _

from abcast.models import OnAirPlugin as OnAirPluginModel


@plugin_pool.register_plugin
class OnAirPlugin(CMSPluginBase):
    model = OnAirPluginModel
    name = _("On-Air Plugin")
    render_template = "abcast/cmsplugin/on_air.html"

    # meta
    class Meta:
        app_label = 'abcast'

    def render(self, context, instance, placeholder):

        context.update({
            'instance': instance,
            'object': instance.channel,
            'placeholder': placeholder,
        })
        return context
