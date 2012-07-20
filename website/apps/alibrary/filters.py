#
import django_filters

from alibrary.models import Release

from django.utils.datastructures import SortedDict
ORDER_BY_FIELD = 'o'


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
    class Meta:
        model = Release
        fields = ['releasedate', 'releasetype', 'release_country',]
        
    
    @property
    def filterlist(self):
        
        print 'FFFLLL'
        
        flist = []
        
        if not hasattr(self, '_filterlist'):
            
            """
            fields = SortedDict([(name, filter_.label) for name, filter_ in self.filters.iteritems()])
            fields[ORDER_BY_FIELD] = self.ordering_field
            """
            
            for name, filter_ in self.filters.iteritems():
                ds = Release.objects.values_list(name, flat=True).distinct()
                
                filter_.ds = ds
                
                flist.append(filter_)
                
                print 'Label:',
                print filter_.label
                
                for d in ds:
                    print self.__class__.__name__
                    print d
                    # items.append(d)
                
            
            self._filterlist = flist
            
            """
            Form =  type('%sForm' % self.__class__.__name__, (self._meta.form,), fields)
            if self.is_bound:
                self._filterlist = Form(self.data, prefix=self.form_prefix)
            else:
                self._filterlist = Form(prefix=self.form_prefix)
            """
            
            
        print 'FL!:',    
        print self._filterlist
                
        #return self._filterlist
        
        """
        items = [
                 {'key': 'session',},
                 {'key': 'whatever',},
                 ]
        
        """
        
        return self._filterlist
    