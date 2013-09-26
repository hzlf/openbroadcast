from django.utils.translation import ugettext as _
import django_filters
from alibrary.models import Release, Playlist, Artist, Media, Label

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


class DekadeFilter(django_filters.ChoiceFilter):
    pass


class ReleaseFilter(django_filters.FilterSet):
    # releasedate = django_filters.DateFilter()
    releasetype = CharListFilter(label="Release type")
    release_country = CharListFilter(label="Country")
    media_release__license__name = CharListFilter(label="License")
    main_format__name = CharListFilter(label="Release Format")
    #releasedate = DekadeFilter(label="Release date")
    class Meta:
        model = Release
        fields = ['releasetype', 'release_country', 'main_format__name', 'media_release__license__name', ]

    @property
    def filterlist(self):

        flist = []

        if not hasattr(self, '_filterlist'):


            for name, filter_ in self.filters.iteritems():

                ds = self.queryset.values_list(name, flat=False).annotate(
                    n=models.Count("pk", distinct=True)).distinct()

                filter_.entries = ds

                if ds not in flist:
                    flist.append(filter_)

            self._filterlist = flist

        return self._filterlist


class ArtistFilter(django_filters.FilterSet):
    type = CharListFilter(label=_("Artist type"))
    country__printable_name = CharListFilter(label=_("Country"))
    professions = CharListFilter(label=_("Professions"))

    class Meta:
        model = Artist
        fields = ['type', 'country__printable_name', 'country__continent', 'professions__name']

    @property
    def filterlist(self):
        flist = []
        if not hasattr(self, '_filterlist'):
            for name, filter_ in self.filters.iteritems():
                ds = self.queryset.values_list(name, flat=False).annotate(
                    n=models.Count("pk", distinct=True)).distinct()
                filter_.entries = ds
                if ds not in flist:
                    flist.append(filter_)

            self._filterlist = flist

        return self._filterlist


class LabelFilter(django_filters.FilterSet):
    type = CharListFilter(label=_("Label type"))
    country = CharListFilter(label=_("Country"))

    class Meta:
        model = Label
        fields = ['type', 'country', ]

    @property
    def filterlist(self):
        flist = []
        if not hasattr(self, '_filterlist'):
            for name, filter_ in self.filters.iteritems():
                ds = self.queryset.values_list(name, flat=False).annotate(
                    n=models.Count("pk", distinct=True)).distinct()
                filter_.entries = ds
                if ds not in flist:
                    flist.append(filter_)

            self._filterlist = flist

        return self._filterlist


class MediaFilter(django_filters.FilterSet):
    license__name = CharListFilter(label=_("License"))
    base_bitrate = CharListFilter(label=_("Bitrate"))
    base_format = CharListFilter(label=_("Format"))
    base_samplerate = CharListFilter(label=_("Samplerate"))
    mediatype = CharListFilter(label=_("Type"))
    PROCESSED_CHOICES = (
        (0, _('Waiting')),
        (1, _('Done')),
        (2, _('Error')),
    )
    processed = django_filters.ChoiceFilter(label=_("Status"), choices=PROCESSED_CHOICES)

    class Meta:
        model = Media
        fields = ['license__name', 'mediatype', 'base_bitrate', 'base_format', 'base_samplerate', 'processed', 'tempo', 'key']

    @property
    def filterlist(self):


        flist = []

        if not hasattr(self, '_filterlist'):


            for name, filter_ in self.filters.iteritems():

                ds = self.queryset.values_list(name, flat=False).annotate(
                    n=models.Count("pk", distinct=True)).distinct()

                # TODO: extreme hackish...
                if name == 'processed':
                    nd = []
                    for d in ds:
                        nd.append([d[0], d[1], self.PROCESSED_CHOICES[d[0]][1]])

                    filter_.entries = nd

                else:
                    filter_.entries = ds



                if ds not in flist:
                    flist.append(filter_)

            self._filterlist = flist

        return self._filterlist



DAY_CHOICES = (
    (0, _('Mon')),
    (1, _('Tue')),
    (2, _('Wed')),
    (3, _('Thu')),
    (4, _('Fri')),
    (5, _('Sat')),
    (6, _('Sun')),
)

class PlaylistFilter(django_filters.FilterSet):
    # releasedate = django_filters.DateFilter()
    type = CharListFilter(label=_("Type"))
    status = CharListFilter(label=_("Status"))
    target_duration = CharListFilter(label=_("Target Duration"))
    dayparts = django_filters.ChoiceFilter(label="Dayparts")
    weather__name = CharListFilter(label="Weather")
    seasons__name = CharListFilter(label="Season")
    #media_release__license__name = CharListFilter(label="License")
    #main_format__name = CharListFilter(label="Release Format")
    class Meta:
        model = Playlist
        fields = ['type', 'status', 'target_duration', 'dayparts', 'weather__name', 'seasons__name', ]

    def __init__(self, *args, **kwargs):
        super(PlaylistFilter, self).__init__(*args, **kwargs)
        self.filters['dayparts'].extra.update(
            {
                'choices': DAY_CHOICES
            })


    @property
    def filterlist(self):

        flist = []

        if not hasattr(self, '_filterlist'):

            for name, filter_ in self.filters.iteritems():

                ds = self.queryset.values_list(name, flat=False).annotate(
                    n=models.Count("pk", distinct=True)).distinct()

                """
                if name == 'dayparts':
                    print '************* DPF ****'
                    tlist = []
                    for d in ds:
                        print d
                        # tlist.append([d[0], d[1], DAY_CHOICES[d[0]]])
                        tlist.append([d[0], d[1], DAY_CHOICES[0] ])

                    ds = tlist
                """

                filter_.entries = ds

                if ds not in flist:
                    #pass
                    flist.append(filter_)

            self._filterlist = flist

        return self._filterlist
    