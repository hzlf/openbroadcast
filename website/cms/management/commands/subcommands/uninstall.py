# -*- coding: utf-8 -*-
from cms.management.commands.subcommands.base import SubcommandsCommand
from cms.models.pluginmodel import CMSPlugin
from cms.models.titlemodels import Title
from django.core.management.base import LabelCommand


class UninstallApphooksCommand(LabelCommand):
    
    args = "APPHOK_NAME"
    label = 'apphook name (eg SampleApp)'
    help = 'Uninstalls (sets to null) specified apphooks for all pages'
    
    def handle_label(self, label, **options):
        queryset = Title.objects.filter(application_urls=label)
        number_of_apphooks = queryset.count()

        if number_of_apphooks > 0:
            if options.get('interactive'):
                confirm = raw_input("""
You have requested to remove %d %r apphooks.
Are you sure you want to do this?
Type 'yes' to continue, or 'no' to cancel: """ % (number_of_apphooks, label))
            else:
                confirm = 'yes'
            if confirm == 'yes':
                queryset.update(application_urls=None)
                self.stdout.write('%d %r apphooks uninstalled\n' % (number_of_apphooks, label))
        else:
            self.stdout.write('no %r apphooks found\n' % label)
            
class UninstallPluginsCommand(LabelCommand):

    args = "PLUGIN_NAME"
    label = 'plugin name (eg SamplePlugin)'
    help = 'Uninstalls (deletes) specified plugins from the CMSPlugin model'
    
    def handle_label(self, label, **options):
        queryset = CMSPlugin.objects.filter(plugin_type=label)
        number_of_plugins = queryset.count()
        
        if number_of_plugins > 0:
            if options.get('interactive'):
                confirm = raw_input("""
You have requested to remove %d %r plugins.
Are you sure you want to do this?
Type 'yes' to continue, or 'no' to cancel: """ % (number_of_plugins, label))
            else:
                confirm = 'yes'
            queryset.delete()
            self.stdout.write('%d %r plugins uninstalled\n' % (number_of_plugins, label))
        else:
            self.stdout.write('no %r plugins found\n' % label)            

class UninstallCommand(SubcommandsCommand):
    help = 'Uninstall commands'
    subcommands = {
        'apphooks': UninstallApphooksCommand,
        'plugins': UninstallPluginsCommand
    }