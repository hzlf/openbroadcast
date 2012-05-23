#
import django_filters

from alabel.models import Release

class ReleaseFilter(django_filters.FilterSet):
    pressings = django_filters.NumberFilter(lookup_type='gt')
    releasedate = django_filters.DateFilter()
    class Meta:
        model = Release
        fields = ['pressings', 'releasedate',]