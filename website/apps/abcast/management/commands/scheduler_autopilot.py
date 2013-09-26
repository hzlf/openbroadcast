#-*- coding: utf-8 -*-
from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
import os
import sys
import time
import re

from abcast.models import *
from alibrary.models import Playlist
import datetime

from random import choice

# logging
import logging
logger = logging.getLogger(__name__)

START_OFFSET = -1 # hours to look ahead
RANGE = 12 # hours to fill



class Autopilot(object):
    def __init__(self, * args, **kwargs):
        self.action = kwargs.get('action')
        self.verbosity = int(kwargs.get('verbosity', 1))
        
        
    def add_emission(self, slot_start):
        
        log = logging.getLogger('abcast.autopilot.add_emission')
        log.debug('auto-adding emission, slot start: %s' % slot_start)
            
        # check if overlapping emission exists
        ces = Emission.objects.filter(time_start__lt=slot_start, time_end__gt=slot_start)
        print 'coliding emissions'
        print ces
        if ces.count() > 0:
            next_start = ces[0].time_end
        else:
            next_start = slot_start
            
        print 'next_start: %s' % next_start
            
        # check how much time is available until next emission
        fes = Emission.objects.filter(time_start__gte=next_start).order_by('time_start')
        print fes
        free_slot = 14400
        if fes.count() > 0:
            log.debug('got %s emissions scheduled in future' % fes.count())
            diff = fes[0].time_start - next_start
            free_slot = int(diff.total_seconds())

        log.debug('length of free slot is: %s seconds' % free_slot)
        log.debug('length of free slot is: %s hours' % (int(free_slot) / 60 / 60))
            
        if free_slot == 0:
            print 'FREE SLOT IS ZERO - FUCK!'
            return fes[0].time_end
            
        """
        look for possible playlists to schedule
        """
        ps = Playlist.objects.filter(target_duration__lte=free_slot, rotation=True).order_by('?')
        
        if ps.count() > 0:
            p = ps[0]
        else:
            p = None
        
        print 'The random selection iiiiiiiiiiiiiis!!'
        print p
        
        # create the scheduler entry
        if p:
            pass
            e = Emission(content_object=p, time_start=next_start)
            e.save()
            
            print 'Created emission, will run until: %s' % e.time_end
            
            return e.time_end
        

    def free_time_in_range(self, range_start, range_end):
        
        log = logging.getLogger('abcast.autopilot.free_time_in_range')
        log.debug('range_start: %s' % range_start)
        log.debug('range_end: %s' % range_end)
        
        
        
        
        range_seconds = int((range_end - range_start).total_seconds())
        print 'range_seconds %s' % range_seconds
        
        emissions_total = 0
        es = Emission.objects.filter(time_end__gte=range_start, time_start__lte=range_end)
        for e in es:
            print e
            emissions_total += int(e.content_object.get_duration())
        
            
        print 'range_seconds:   %s' % range_seconds
        print 'emissions_total: %s' % (int(emissions_total) / 1000)
            
        free_time = range_seconds - (int(emissions_total) / 1000)
        
        return free_time
        
        
    def run(self):
        
        log = logging.getLogger('abcast.autopilot.run')
        
        log.debug('running autopilot, action: %s' % self.action)
        
        
        if self.action == 'schedule':
            
            log.debug('try to fill up the schedule')
            
            now = datetime.datetime.now()
            range_start = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1 + START_OFFSET)
            range_end = range_start + datetime.timedelta(hours=RANGE)
            
            log.debug('range_start: %s' % range_start)
            log.debug('range_end:   %s' % range_end)
            
            slot_start = range_start
            
            
            print 'FREEEEEE'
            print self.free_time_in_range(range_start, range_end)
            
            """"""
            while self.free_time_in_range(range_start, range_end) > 0:
                slot_start = self.add_emission(slot_start)
            
             
        
        if self.action == 'schedule__':
            print 'schedule!!'
            
            now = datetime.datetime.now()
            
            time_start = now + datetime.timedelta(hours=4)
            time_end = now + datetime.timedelta(hours=48)
        
            print time_start
            print time_end
            
            """
            Check if there are any emissions scheduled for that range
            """
            
            ses = Emission.objects.filter(time_end__gte=time_start, time_end__lte=time_end).order_by('-time_end')
            print ses
            for se in ses:
                print se.time_end
                
            if ses.count() > 0:
                print 'got one'
                pass
            else:
                
                print 'put something...'
                se = Emission.objects.filter(time_end__lte=time_start).order_by('-time_end')[0]
                print se.time_end
                """
                get random playlist by dayparting
                """
                pl = Playlist.objects.get(pk=1009)
                
                e = Emission()
                e.source = 'autopilot'
                e.name = pl.name
                e.content_object = pl
                e.time_start = se.time_end
                
                h = (0,1,2,3)
                m = (0, 15, 30, 45)
                
                e.time_end = se.time_end + datetime.timedelta(hours=choice(h), minutes=choice(m))
                e.save()
                
                
                
                
            





class Command(NoArgsCommand):

    option_list = BaseCommand.option_list + (
        make_option('--action',
            action='store',
            dest='action',
            default=False,
            help='Fill up the scheduler!!'),
        )

    def handle_noargs(self, **options):
        ap = Autopilot(**options)
        ap.run()
