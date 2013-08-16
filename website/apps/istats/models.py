import logging
import time
from celery.task.control import inspect

from exporter.models import Export

class Stats(object):

    def __init__(self):
        self.celery_inspector = inspect()



    def get_server_stats(self):

        """
        return self.celery_inspector.scheduled()
        cstats = self.celery_inspector.stats()

        return cstats

        processes = []

        for worker in cstats:
            ts = cstats[worker]['total']
            for t in ts:
                processes.append({'process': t, 'queue': ts[t]})

        return processes
        """



        stats = []



        ts = {
                'key': 'exporter',
                'display': 'Exports',
                'queue': Export.objects.filter(status=2).count(),
                'estimate': Export.objects.filter(status=2).count() * 60,

        }
        stats.append(ts)


        return stats