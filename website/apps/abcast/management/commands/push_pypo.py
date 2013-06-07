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

from kombu.connection import BrokerConnection
from kombu.messaging import Exchange, Queue, Consumer, Producer
from kombu.simple import SimpleQueue, SimpleBuffer
from kombu.common import maybe_declare
from kombu.pools import producers

import pika

MQ_HOST = '172.16.82.134'
MQ_PORT = '5672'
MQ_USER = 'airtime'
MQ_PASS = 'LON6XVJK2PPZDSQPH2BV'
MQ_VHOST = '/airtime'


from random import choice

class Pusher(object):
    def __init__(self, * args, **kwargs):
        self.action = kwargs.get('action')
        self.verbosity = int(kwargs.get('verbosity', 1))
        
    def run(self):
        
        print 'pypo Pusher'
        if self.action == 'update_schedule':
            print 'update_schedule!!'
            credentials = pika.PlainCredentials(MQ_USER, MQ_PASS)
            connection = pika.BlockingConnection(pika.ConnectionParameters(MQ_HOST,
                                       5672,
                                       '/airtime',
                                       credentials))
            channel = connection.channel()
            channel.queue_declare(queue='pypo-fetch', durable=True)
            message = {
                       'schedule': {
                                    'media': {}
                                    },
                       'event_type': 'update_schedule'
                       }
            
            import json
            message = json.dumps(message)
            
            message = 'hallo'
            
            channel.basic_publish(exchange='airtime-pypo',
                      routing_key='pypo-fetch',
                      body=message)
            
            channel.close()
            connection.close()


            
            
        if self.action == 'update_schedule_kombu':
            print 'update_schedule!!'
            
            exchange = Exchange("airtime-pypo", "direct", durable=True, auto_delete=True)
            queue = Queue("pypo-fetch", exchange=exchange, key="foo", durable=True)
            
            connection = BrokerConnection(MQ_HOST, MQ_USER, MQ_PASS, MQ_VHOST)
            channel = connection.channel()
            
            simple_queue = SimpleQueue(channel, queue)
            
            
            
            
            
            message = {
                       'schedule': {
                                    'media': {}
                                    },
                       'event_type': 'update_schedule'
                       }
            
            
            print simple_queue.qsize()
            
            print 'do:'
            
            
            producer = Producer(channel, exchange=exchange, routing_key=None, serializer="json")
            
            
            
            producer.publish(message, routing_key='pypo-fetch')
            
            
            print simple_queue.qsize()
            channel.close()
            





class Command(NoArgsCommand):

    option_list = BaseCommand.option_list + (
        make_option('--action',
            action='store',
            dest='action',
            default=False,
            help='Fill up the scheduler!!'),
        )

    def handle_noargs(self, **options):
        p = Pusher(**options)
        p.run()
