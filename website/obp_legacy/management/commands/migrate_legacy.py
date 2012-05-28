#-*- coding: utf-8 -*-
from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand, NoArgsCommand
from optparse import make_option
import os
import sys

import re

from tagging.models import Tag

from alibrary.models import Artist, Release, Media, Label

from obp_legacy.models import *

from django.template.defaultfilters import slugify

from datetime import datetime


class LegacyImporter(object):
    def __init__(self, * args, **kwargs):
        self.object_type = kwargs.get('object_type')
        self.verbosity = int(kwargs.get('verbosity', 1))
        



    def import_release(self, lr):

        print 'trying to get related data'
        
        lms = lr.mediasreleases_set.all()
        las = lr.artistsreleases_set.all()
        lls = lr.labelsreleases_set.all()
        
        r, created = Release.objects.get_or_create(legacy_id=lr.id)
        
        if created:
            print 'Not here yet -> created'
        else:
            print 'found by legacy_id -> use'
        
        """
        Release creation/update & mapping
        """
        r.slug = slugify(lr.name)
        r.legacy_id = lr.id
        
        """
        Mapping new <> legacy
        """
        r.name = lr.name
        # ... rest here
        
        r.save()
        
        """
        Tag Mapping
        """
        ntrs = NtagsReleases.objects.using('legacy').filter(release_id=lr.id)
        # r.tags.clear()
        for ntr in ntrs:
            print 'Tag ID: %s' % ntr.ntag_id
            nt = Ntags.objects.using('legacy').get(id=ntr.ntag_id)
            print 'Tag Name: %s' % nt.name

            
            Tag.objects.add_tag(r, '"%s"' % nt.name)
            
            #r.tags.add_tag(nt.name)
            #r.tags.add(nt.name)
        
        
        """
        Label mapping
        """
        for ll in lls:
            l, created = Label.objects.get_or_create(legacy_id=ll.label.id)
            l.slug = slugify(ll.label.name)
            """
            Mapping new <> legacy
            """
            l.name = ll.label.name
            
            # save (& send to process queue...) :)
            l.save()
            
            # assign release
            r.label = l
            r.save()
        
        
        """
        Loop tracks and track-related artists
        """
        """
        for lm in lms:
            m, created = Media.objects.get_or_create(legacy_id=lm.media.id)
            m.slug = slugify(lm.media.name)
                
            
            # Mapping new <> legacy
            
            m.name = lm.media.name
            try:
                m.tracknumber = int(lm.media.tracknumber)
            except Exception, e:
                m.tracknumber = 0
            
            # assign release
            m.release = r
            
            # save (& send to process queue...) :)
            m.save()
            
            
            # get track artist
            
            tlas = lm.media.artistsmedias_set.all()
            for tla in tlas:
                print "** TLA **"
                #print tla.artist.name
                
                a, created = Artist.objects.get_or_create(legacy_id=tla.artist.id)
                a.slug = slugify(tla.artist.name)
                a.name = tla.artist.name
                
                a.save()
                
                m.artist = a
                m.save()
        """     
            
            
        
        
        """
        Update migration timestamp on legacy database
        """
        lr.migrated = datetime.now()
        lr.save()
        
        
        return









    def walker(self):
        
        if(self.object_type == 'releases'):
            
            lrs = Releases.objects.using('legacy').filter(migrated=None).exclude(name=u'').all()[0:10]
        
        
            for lr in lrs:
                print
                print '----------------------------------------'
                print 'got release:',
                print u'%s' % lr.name.encode('ascii', 'replace')
                
                self.import_release(lr)
                
                #print lr.id
        return
                
        




class Command(NoArgsCommand):
    """
    Import directory structure into alibrary:

        manage.py import_folder --path=/tmp/assets/images
    """

    option_list = BaseCommand.option_list + (
        make_option('--type',
            action='store',
            dest='object_type',
            default=False,
            help='Import files located in the path into django-filer'),
        )

    def handle_noargs(self, **options):
        legacy_importer = LegacyImporter(**options)
        legacy_importer.walker()
