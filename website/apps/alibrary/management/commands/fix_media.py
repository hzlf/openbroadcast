#-*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

import logging
log = logging.getLogger(__name__)




class MediaFix(object):
    def __init__(self, * args, **kwargs):
        self.verbosity = int(kwargs.get('verbosity', 1))

    def fix_durations(self):

        from alibrary.models import Media

        print
        print '-----------------------------------------------'
        print "Trying to fix media durations"
        print '-----------------------------------------------'
        print

        print 'Num. tracks:        %s' % Media.objects.count();
        print 'Without duration:   %s' % Media.objects.filter(duration=None).count();
        print 'With ZERO duration: %s' % Media.objects.filter(duration=0).count();

        ms = Media.objects.filter(duration=None)
        for m in ms:
            try:
                m.duration = m.get_duration()
                if m.duration and m.duration > 0:
                    log.debug('got duration "%s" for: id: %s - %s' % (m.duration, m.pk, m.name))
                else:
                    log.warning('zero or none duration "%s" for: id: %s - %s' % (m.duration, m.pk, m.name))
                m.save()
            except Exception, e:
                log.warning('unable to get duration for: id: %s - %s' % (m.pk, m.name))
        
        ms = Media.objects.filter(duration=0)
        for m in ms:
            try:
                m.duration = m.get_duration()
                if m.duration and m.duration > 0:
                    log.debug('got duration "%s" for: id: %s - %s' % (m.duration, m.pk, m.name))
                else:
                    log.warning('zero or none duration "%s" for: id: %s - %s' % (m.duration, m.pk, m.name))
                m.save()
            except Exception, e:
                log.warning('unable to get duration for: id: %s - %s' % (m.pk, m.name))

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        media_fix = MediaFix(**options)
        # file_importer.walker()
        media_fix.fix_durations()
