#-*- coding: utf-8 -*-
#from django.core.files import File as DjangoFile
import pprint
from optparse import make_option

from django.core.management.base import BaseCommand, NoArgsCommand

from cms.models import CMSPlugin
from importer.models import *
from importer.util.process import Process
from importer.util.importer import Importer

IF_ID = 2329
# http://local.openbroadcast.ch:8080/de/admin/importer/importfile/2282/


class ImporterTest(object):
    def __init__(self, * args, **kwargs):
        self.test = kwargs.get('test')
        self.if_id = kwargs.get('if_id')
        self.verbosity = int(kwargs.get('verbosity', 1))
        
        self.pp = pprint.PrettyPrinter(indent=2)

        print
        print '********* TEST *************'
        print self.test
        print '****************************'
        print
        #print self.if_id



    def run(self):





        if self.test == 'process':
            print 'testing process'
            
            processor = Process()
            
            obj = ImportFile.objects.get(pk=self.if_id)
            
            media_id = processor.id_by_sha1(obj.file)
            print 'path: %s' % obj.file.path  
            print 'media_id: %s', media_id
            
            """"""
            print
            obj.results_tag = processor.extract_metadata(obj.file)
            
            self.pp.pprint(obj.results_tag)

            obj.results_acoustid = processor.get_aid(obj.file)
            processor.get_musicbrainz(obj)


        if self.test == 'import':
            print 'testing import'
            importer = Importer()
            obj = ImportFile.objects.get(pk=self.if_id)
            media, status = importer.run(obj)

            print '*************************************'
            print media


        if self.test == 'lookup':
            from alibrary.models.artistmodels import Release
            from importer.util.importer import mb_complete_release_task

            mb_id = 'a808ae2c-9c89-4b2c-96cb-e527554b4ee2'
            obj = Release.objects.get(pk=2102)


            print 'name:  %s' % obj.name
            print 'mb id: %s' % mb_id

            mb_complete_release_task(obj, mb_id)

            
            
            
            


class Command(NoArgsCommand):

    option_list = BaseCommand.option_list + (
        make_option('--test',
            action='store',
            dest='test',
            default=False,
            help='Test Processing'),
        make_option('--if_id',
            action='store',
            dest='if_id',
            default=IF_ID,
            help='set importfile id'),
        )

    def handle_noargs(self, **options):
        
        it = ImporterTest(**options)
        it.run()
