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

class Autopilot(object):
    def __init__(self, * args, **kwargs):
        self.action = kwargs.get('action')
        self.verbosity = int(kwargs.get('verbosity', 1))
        
    def run(self):
        
        print 'Autopilot'
        if self.action == 'schedule':
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
