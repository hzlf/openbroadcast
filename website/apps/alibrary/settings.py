"""alibrary - default settings"""
from django.conf import settings
from django.utils.translation import ugettext as _

DEFAULT_RELEASETYPE_CHOICES = (
    (_('General'), (
            ('album', _('Album')),
            ('single', _('Single')),
            ('ep', _('EP')),
            ('compilation', _('Compilation')),
            ('soundtrack', _('Soundtrack')),
            ('audiobook', _('Audiobook')),
            ('spokenword', _('Spokenword')),
            ('interview', _('Interview')),
            ('live', _('Live')),
            ('remix', _('Remix')),
            ('broadcast', _('Broadcast')),
            ('djmix', _('DJ-Mix')),
            ('mixtape', _('Mixtape')),
        )
    ),
    #(_('Recording'), (
    #        ('remix', _('Remix')),
    #        ('live', _('Live')),
    #    )
    #),
    ('other', _('Other')),
)

DEFAULT_LABELTYPE_CHOICES = (
    ('unknown', _('Unknown')),
    ('major', _('Major Label')),
    ('indy', _('Independent Label')),
    ('net', _('Netlabel')),
    ('event', _('Event Label')),
)


RELEASETYPE_CHOICES = getattr(settings, 'ALIBRARY_RELEASETYPE_CHOICES', DEFAULT_RELEASETYPE_CHOICES)
LABELTYPE_CHOICES = getattr(settings, 'ALIBRARY_LABELTYPE_CHOICES', DEFAULT_LABELTYPE_CHOICES)
