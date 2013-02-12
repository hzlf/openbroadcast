from django.utils.translation import ugettext as _
import django_filters
from alibrary.models import Release, Playlist

from django.utils.datastructures import SortedDict
ORDER_BY_FIELD = 'o'

from django.db import models

class CharListFilter(django_filters.Filter):

    def filter(self, qs, value):
        if not value:
            return qs
        if isinstance(value, (list, tuple)):
            lookup = str(value[1])
            if not lookup:
                lookup = 'exact'
            value = value[0]
        else:
            values = value.split(',')
            lookup = self.lookup_type
            
        if value and values:
            
            if len(values) > 1:
                lookup = 'in'
                return qs.filter(**{'%s__%s' % (self.name, lookup): values})
                
            else:
                return qs.filter(**{'%s__%s' % (self.name, lookup): value})
        
        return qs


class ReleaseFilter(django_filters.FilterSet):

    # releasedate = django_filters.DateFilter()
    releasetype = CharListFilter(label="Release type")
    release_country = CharListFilter(label="Country")
    media_release__license__name = CharListFilter(label="License")
    main_format__name = CharListFilter(label="Release Format")
    class Meta:
        model = Release
        fields = ['releasetype', 'release_country', 'main_format__name', 'media_release__license__name',]
    
    @property
    def filterlist(self):

        flist = []
        
        if not hasattr(self, '_filterlist'):

            
            for name, filter_ in self.filters.iteritems():
                    
                ds = self.queryset.values_list(name, flat=False).annotate(n=models.Count("pk", distinct=True)).distinct()
                
                filter_.entries = ds
                
                if ds not in flist:                    
                    flist.append(filter_)

            self._filterlist = flist
        
        return self._filterlist


class PlaylistFilter(django_filters.FilterSet):

    # releasedate = django_filters.DateFilter()
    type = CharListFilter(label=_("Type"))
    status = CharListFilter(label=_("Status"))
    target_duration = CharListFilter(label=_("Target Duration"))
    dayparts__day = CharListFilter(label="Dayparts")
    #media_release__license__name = CharListFilter(label="License")
    #main_format__name = CharListFilter(label="Release Format")
    class Meta:
        model = Playlist
        fields = ['type', 'status', 'target_duration', 'dayparts__day', ]
    
    @property
    def filterlist(self):

        flist = []
        
        if not hasattr(self, '_filterlist'):

            
            for name, filter_ in self.filters.iteritems():
                    
                ds = self.queryset.values_list(name, flat=False).annotate(n=models.Count("pk", distinct=True)).distinct()
                
                filter_.entries = ds
                
                if ds not in flist:                    
                    flist.append(filter_)

            self._filterlist = flist
        
        return self._filterlist
    