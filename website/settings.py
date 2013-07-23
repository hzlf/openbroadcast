# -*- coding: utf-8 -*-
"""
Copyright 2012, Jonas Ohrstrom  - ohrstrom@gmail.com
See LICENSE.txt
"""

import os
import sys

# celery
import djcelery

djcelery.setup_loader()

import posixpath

gettext = lambda s: s
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

# subdirectory for apps
sys.path.insert(0, os.path.join(PROJECT_DIR, 'apps'))
# subdirectory for tools
sys.path.insert(0, os.path.join(PROJECT_DIR, 'tools'))
# subdirectory for plugins
sys.path.insert(0, os.path.join(PROJECT_DIR, 'cmsplugins'))
# subdirectory for shop
sys.path.insert(0, os.path.join(PROJECT_DIR, 'shop'))
# subdirectory for legacy tools
sys.path.insert(0, os.path.join(PROJECT_DIR, 'legacy'))

DEBUG = True

TEMPLATE_DEBUG = DEBUG
#TEMPLATE_STRING_IF_INVALID ='* MISSING *'

SERVE_MEDIA = False
COMPRESS_OFFLINE = False
COMPRESS_ENABLED = False

LANGUAGES = [('en', 'en'), ('de', 'de'), ('fr', 'fr')]
DEFAULT_LANGUAGE = 0

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'data.db'),
        #'NAME': '/Users/ohrstrom/srv/alibrary/data.db',
    },
}

TIME_ZONE = 'Europe/Zurich'

LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'de-de'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

SECRET_KEY = '0r6%7gip5tmez*vygfv+u14h@4lbt^8e2^26o#5_f_#b7%cm)u'
CRYPTO_SECRET = 'JHRhwLiOsyMyL1JA'
AES_SECRET_PASSWORD = 'JHRhwLiOsyMyL1JA'
AES_BLOCK_SIZE = 32

"""
TEMPLATE_LOADERS = (
    # mobile
    #'django_mobile.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
    #'django.template.loaders.app_directories.Loader',
)
"""

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    #'pagination.middleware.PaginationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # cms
    'cms.middleware.multilingual.MultilingualURLMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',

    # mobile [just testing]
    'django_mobile.middleware.MobileDetectionMiddleware',
    'django_mobile.middleware.SetFlavourMiddleware',

    # xs
    'lib.middleware.xs_sharing.XsSharingMiddleware',

    'lib.middleware.profiler.ProfileMiddleware',

    # admin
    'lib.middleware.admin_redirects.AdminRedirectMiddleware',
    # custom
    #'lib.middleware.ProfileMiddleware',
    #'lib.middleware.PrettifyMiddlewareBS',
    #'django_badbrowser.middleware.BrowserSupportDetection',

    'arating.middleware.AratingIpMiddleware',
    #'lib.middleware.social_auth_extra.SocialAuthExceptionExtraMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',

)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    #'notification.context_processors.notification',
    #'announcements.context_processors.site_wide_announcements',
    # cms
    'cms.context_processors.media',
    # staticfiles
    'django.core.context_processors.static',
    'sekizai.context_processors.sekizai',
    # multilingual
    'multilingual.context_processors.multilingual',

    # mobile
    'django_mobile.context_processors.flavour',

    # messaging
    'postman.context_processors.inbox',

    # authentication
    #'allauth.context_processors.allauth',
    #'allauth.account.context_processors.account',
    #'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.backends_data',
    #'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

"""
CMS related settings (template/placeholder setup etc)
"""

CMS_USE_TINYMCE = False
CMS_REDIRECTS = True
#CMS_MODERATOR = True

CMS_TEMPLATES = (
    # generic templates
    ('_templates/layout_a.html', 'Base - X column & Menu'),
    ('_templates/home.html', 'Home template'),
)

WIDTH_INNER = 960
CMS_PLACEHOLDER_CONF = {
    'main': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width": WIDTH_INNER},
        'name': gettext("Main Content"),
    },
    'template_1_content_2': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width": 300},
        'name': gettext("FlexBox"),
    },
    'sidebar_pre': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width": 280},
        'name': gettext("Sidebar | Pre-Menu"),
    },
    'sidebar_post': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width": 280},
        'name': gettext("Sidebar | Post-Menu"),
    },
    'placeholder_1': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width": WIDTH_INNER},
        'name': gettext("Main Content"),
    },
    # home slots
    'home_slot_a': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name': gettext("Home | Slot A"),
    },
    'home_slot_b': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name': gettext("Home | Slot B"),
    },
    'home_slot_c': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name': gettext("Home | Slot C"),
    },
    'home_slot_d': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name': gettext("Home | Slot D"),
    },
}

CMS_APPLICATIONS_URLS = (
    ('cmsplugin_advancednews.urls', 'News'),
)
CMS_NAVIGATION_EXTENDERS = (
    ('cmsplugin_advancednews.navigation.get_nodes', 'News navigation'),
)

CMS_PLUGIN_PROCESSORS = (
    'lib.cms_plugin_processors.wrap_text',
)

CMS_SEO_FIELDS = True

CMS_CACHE_DURATIONS = {
    'menus': 1,
    'content': 1,
}

CMS_VIMEO_DEFAULT_WIDTH = 830
CMS_VIMEO_DEFAULT_HEIGHT = 467

CMS_YOUTUBE_DEFAULT_WIDTH = 830
CMS_YOUTUBE_DEFAULT_HEIGHT = 467

# media deliver
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

# static files (application js/img etc)
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

LEGACY_STORAGE_ROOT = None

ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'site-static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
    'dajaxice.finders.DajaxiceFinder',
)

COMMENTS_APP = 'fluent_comments'
COMMENT_MAX_LENGTH = 800
FLUENT_COMMENTS_EXCLUDE_FIELDS = ['title', 'email', 'name', 'url', ]

INSTALLED_APPS = (

    #'admin_tools.theming',
    #'admin_tools.menu',
    #'admin_tools.dashboard',

    #'admintools_bootstrap',
    'admin_style',
    'admin_tools',

    'admin_shortcuts',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.syndication',
    'django.contrib.humanize',
    'django.contrib.webdesign',
    'django.contrib.admin',


    'threadedcomments',
    'fluent_comments',

    'django.contrib.comments',
    'django.contrib.staticfiles',
    'django.contrib.markup',
    'django.contrib.sitemaps',

    #'staticfiles',

    # server
    'gunicorn',
    'django_date_extensions',
    'esi',
    #'turbolinks',

    'haystack',

    # messaging & registration
    'postman',
    #'invite',

    # core apps
    'django_extensions',
    'django_jenkins',
    'django_filters',

    # base app
    'base',

    #'notification',
    'notifications',
    'debug_toolbar',
    'mailer',
    'djcelery',

    'cms',
    'menus',
    'mptt',
    'south',
    'polymorphic',
    'django_countries',
    'l10n',
    'guardian',
    'filer',
    'private_files',

    'profiles',
    #'django_hgroups',


    'sendfile',

    'reversion',

    'clear_cache',

    'actstream',

    'django_badbrowser',
    'datatrans',

    'genericadmin',


    # temp

    'eav',

    # dajax
    'dajaxice',
    'dajax',

    'ajax_select',


    'email_obfuscator',


    # cms plugins
    'cms.plugins.text',
    'cms.plugins.link',
    'cms.plugins.inherit',
    #'cmsplugin_filer_folder',
    #'cmsplugin_filer_image',
    'cmsplugin_youtube',
    'cmsplugin_vimeo',
    #'cmsplugin_soundcloud',
    'cmsplugin_pagedown',

    'shortcutter',

    'multilingual',
    'disqus',
    'selectable',

    'autocomplete_light',

    # asset and media handling
    'sekizai',
    'compressor',
    'easy_thumbnails',

    # translation
    'modeltranslation',


    # rest & API
    'djangorestframework',

    # stats
    'atracker',


    # users/auth
    'avatar',
    'emailconfirmation',
    #'allauth',
    #'allauth.account',
    #'allauth.socialaccount',
    ##'allauth.ajax',
    ##'allauth.twitter',
    #'allauth.openid',
    #'allauth.facebook',


    # alternative registration
    'registration',
    'social_auth',
    'dropbox',
    'invitation',

    'tastypie',

    'crispy_forms',
    'floppyforms',
    #'djangoratings',
    #'agon_ratings',
    'django_mobile',


    # custom apps/*
    'pusher',
    'asite',
    'alibrary',
    'aplayer',
    'importer',
    'exporter',
    'abcast',
    'multiuploader',
    'arating',
    'asearch',
    #'django_db_signals',
    'pushy',


    # blog
    'zinnia',
    'cmsplugin_zinnia',

    'bcmon',
    #'secretballot',
    'genericrelations',
    'ashop',
    'ashop.addressmodel',
    #'acalendar',
    #'articles',
    'spurl',
    'lib',
    #'teaser',

    # shop apps
    'shop',
    'shop_ajax',
    'paypal.standard.ipn',
    'shop_paypal',
    #'discount',

    'wikisyntax',
    #'taggit',
    'tagging',
    'ac_tagging',
    'pure_pagination',
    #'taggit_templatetags',

    'obp_legacy',

    # helpers
    'dev',


    # spf
    'csvimport',
    'spf',

    # monitoring
    #'kitsune',
)

ZINNIA_ENTRY_BASE_MODEL = 'cmsplugin_zinnia.placeholder.EntryPlaceholder'

"""
Mixed shizzle
"""
FIXTURE_DIRS = [
    os.path.join(PROJECT_DIR, 'fixtures'),
]
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
TEMP_DIR = '%s/%s' % (PROJECT_DIR, 'temp')

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 5,
    'MARGIN_PAGES_DISPLAYED': 2,
}

FORMATS_MEDIA = {
    #'mp3': ['base', 'low'],
    'mp3': ['base', ],
}

"""
ADMIN_SHORTCUTS = [
    {
        'title': 'Library',
        'shortcuts': [
            {
                'url_name': 'admin:alibrary_release_changelist',
                'title': 'Releases',
                'count_new': 'project.utils.count_new_orders',
            },
        ]
    },
]
"""

"""
API-Keys (override in local_settings)
"""
# google related
GOOGLE_MAPS_API_KEY = 'ABQIAAAAOHPJc2-0TzaYgfOquRJgtRR2_LvdznTgfqpGEUf18uq-dm_lmhSjdzKrt5n5UfFjwviK9F39LyXJng'

# facebook oauth settings
FACEBOOK_APP_ID = "108235479287674"
FACEBOOK_SECRET_KEY = "a5b0a3ce9f47d1eadaf004ffd9da4e1f"
FACEBOOK_API_SECRET = 'a5b0a3ce9f47d1eadaf004ffd9da4e1f'
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'publish_stream']


# analyzer
ECHONEST_API_KEY = 'DC7YKF3VYN7R0LG1M'
ENMFP_CODEGEN_BIN = PROJECT_DIR + '/lib/analyzer/bin/codegen.Darwin'
ECHOPRINT_CODEGEN_BIN = 'echoprint-codegen'

"""
Filer related settings
"""
FILER_IS_PUBLIC_DEFAULT = True
FILER_ENABLE_PERMISSIONS = True
FILER_STATICMEDIA_PREFIX = '/static/filer/'

# private files settings, not for "filer" app
FILE_PROTECTION_METHOD = 'basic'

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)
THUMBNAIL_QUALITY = 80

"""
Emial & messageing settings
"""
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'mailer.backend.DbBackend'


EMAIL_CONFIRMATION_DAYS = 5
EMAIL_DEBUG = DEBUG

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

"""
Identity
"""
CONTACT_EMAIL = 'root@hazelfire.com'
ADMINS = (
    ('anorg', 'root@hazelfire.com'),
)
MANAGERS = ADMINS

"""
Accounts
"""
AUTHENTICATION_BACKENDS = (
    # allauth
    #'allauth.account.auth_backends.AuthenticationBackend',
    # base
    'django.contrib.auth.backends.ModelBackend',
    # guardian
    'guardian.backends.ObjectPermissionBackend',
)
ANONYMOUS_USER_ID = -1
#AUTH_PROFILE_MODULE = 'profiles.Profile'


LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/signout/'
LOGIN_REDIRECT_URL = "/"

"""
allauth version
"""
USERENA_ACTIVATION_REQUIRED = False

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_AUTO_SIGNUP = True
EMAIL_CONFIRMATION_DAYS = 5

"""
registration version
with socialauth
"""
ACCOUNT_ACTIVATION_DAYS = 7
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.contrib.dropbox.DropboxBackend',
    'social_auth.backends.contrib.soundcloud.SoundcloudBackend',
    #'social_auth.backends.yahoo.YahooBackend',
    #'social_auth.backends.browserid.BrowserIDBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'social_auth.backends.contrib.disqus.DisqusBackend',
    #'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    #'social_auth.backends.contrib.orkut.OrkutBackend',
    #'social_auth.backends.contrib.foursquare.FoursquareBackend',
    'social_auth.backends.contrib.github.GithubBackend',
    #'social_auth.backends.contrib.vk.VKOAuth2Backend',
    #'social_auth.backends.contrib.live.LiveBackend',
    #'social_auth.backends.contrib.skyrock.SkyrockBackend',
    #'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    #'social_auth.backends.contrib.readability.ReadabilityBackend',
    #'social_auth.backends.contrib.fedora.FedoraBackend',
    #'social_auth.backends.OpenIDBackend',
    # legacy
    'obp_legacy.auth.backends.LegacyBackend',
    # base
    'django.contrib.auth.backends.ModelBackend',
    # guardian
    'guardian.backends.ObjectPermissionBackend',
)
TWITTER_CONSUMER_KEY = 'Fbp98cYDsI3mY51krZVhVg'
TWITTER_CONSUMER_SECRET = 'ZTOXzo3zJH4AG1Q6rTHxsiKorDqeQkNWixThiZEfrc'
FACEBOOK_APP_ID = '154134078100508'
FACEBOOK_API_SECRET = 'f92f325fa14d5f8fa25c9cdd1700f854'
FACEBOOK_EXTENDED_PERMISSIONS = ['email', ]
LINKEDIN_CONSUMER_KEY = 'aaa'
LINKEDIN_CONSUMER_SECRET = 'bbb'
GOOGLE_CONSUMER_KEY = 'aaa'
GOOGLE_CONSUMER_SECRET = 'bbb'
GOOGLE_OAUTH2_CLIENT_ID = 'aaa'
GOOGLE_OAUTH2_CLIENT_SECRET = 'bbb'
FOURSQUARE_CONSUMER_KEY = 'aaa'
FOURSQUARE_CONSUMER_SECRET = 'bbb'
YAHOO_CONSUMER_KEY = 'aaa'
YAHOO_CONSUMER_SECRET = 'bbb'
GITHUB_APP_ID = '93b8c5a82ee21f19e4c3'
GITHUB_API_SECRET = 'a2602afb10e29096b101e3b698403996a6e86d70'
DROPBOX_APP_ID = 'hysrslzv780iu8n'
DROPBOX_API_SECRET = '5y9ldihkc9ot6cz'
SOUNDCLOUD_CLIENT_ID = 'f009f9ca05053570a2c05d55f08f3dc8'
SOUNDCLOUD_CLIENT_SECRET = 'ad689159fcecc12e14664084ab495874'
#LOGIN_URL          = '/login-form/'
#LOGIN_REDIRECT_URL = '/logged-in/'
#LOGIN_ERROR_URL    = '/login-error/'

# invitation
INVITATION_INVITE_ONLY = False
INVITATION_EXPIRE_DAYS = 10
INVITATION_INITIAL_INVITATIONS = 5

SOCIAL_AUTH_SLUGIFY_USERNAMES = True
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/signout/'
LOGIN_REDIRECT_URL = "/"

LOGIN_ERROR_URL = LOGIN_URL











# profiles & co
ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/network/profiles/%s/" % o.username,
}
AUTH_PROFILE_MODULE = "profiles.Profile"

"""
Shop configuration
"""
# shop config
SHOP_ADDRESS_MODEL = 'ashop.addressmodel.models.Address'

SHOP_SHIPPING_BACKENDS = (
    'ashop.shipping.SkipShippingBackend',
    'shop.shipping.backends.flat_rate.FlatRateShipping',
)

SHOP_PAYMENT_BACKENDS = (
    'shop.payment.backends.pay_on_delivery.PayOnDeliveryBackend',
    'shop_paypal.offsite_paypal.OffsitePaypalBackend',

)

SHOP_CART_MODIFIERS = (
    #'shop_simplevariations.cart_modifier.ProductOptionsModifier',
    'ashop.modifiers.BulkRebateModifier',
    'discount.cart_modifiers.DiscountCartModifier',
    'ashop.modifiers.FixedTaxRate',
    'ashop.modifiers.FixedShippingCosts', # move before Tax if you want to add taxes to shipping as well
)

# shop and payment settings
SHOP_SHIPPING_FLAT_RATE = "10.00"
SHOP_CURRENCY = {
    'code': 'USD',
    'character': '$',
    'separator': '',
}

"""
Payment providers
"""
# paypal
PAYPAL_RECEIVER_EMAIL = 'spam3_1325160774_biz@anorg.net'
PAYPAL_CURRENCY_CODE = SHOP_CURRENCY['code']

"""
Search
"""
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr',
    },
}

"""
Messaging
https://bitbucket.org/psam/django-postman/wiki/Quick_Start_Guide
"""
# POSTMAN_DISALLOW_ANONYMOUS = True  # default is False
# POSTMAN_DISALLOW_MULTIRECIPIENTS = True  # default is False
# POSTMAN_DISALLOW_COPIES_ON_REPLY = True  # default is False
# POSTMAN_DISABLE_USER_EMAILING = True  # default is False
POSTMAN_AUTO_MODERATE_AS = True  # default is None
POSTMAN_SHOW_USER_AS = 'get_full_name'
# POSTMAN_NOTIFIER_APP = None  # default is 'notification'
POSTMAN_MAILER_APP = 'mailer'



# other...
PRETTIFY = True

DISQUS_API_KEY = 'hLRbAlPsBN6G11HyeNX4qMWiebrLZeVzLpUUimq82jsthcFBohQFMTAwS1iCBjie'
DISQUS_WEBSITE_SHORTNAME = 'obp-dev'

"""
Other app related
"""

"""
wikisyntax, eg allows tor resolve [a:Artists Name] to object
"""
WIKISYNTAX = (
    ('r', 'alibrary.util.object_linker.WikiRelease'),
    ('a', 'alibrary.util.object_linker.WikiArtist'),
)
WIKISYNTAX_DISABLE_CACHE = True

"""
sendfile, delivers bought relases/tracks
"""
SENDFILE_BACKEND = 'sendfile.backends.simple'

BADBROWSER_REQUIREMENTS = (
    ("firefox", "3.0"),
    ("chrome", "10.0"),
    ("microsoft internet explorer", "8"),
    ("opera", None), # None indicates no support for the given browser, whatever the version
)
BADBROWSER_SUGGEST = ("firefox", "chrome", "safari", "opera", "microsoft internet explorer")
#BADBROWSER_BASE_TEMPLATE = "base.html"

"""
celeryd
"""
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

CELERY_ROUTES = {
    #'importer.models.process_task': {'queue': 'import'},
    # assign import task to single-instance worker
    'importer.models.import_task': {'queue': 'import'},
}

"""
streaming server
"""
RTMP_HOST = '127.0.0.2'
RTMP_APP = 'alibrary'
RTMP_PORT = '1935'

ICECAST_HOST = '127.0.0.2'
ICECAST_PORT = '8000'

"""
mb server
"""
MUSICBRAINZ_HOST = 'mb.anorg.net'
MUSICBRAINZ_RATE_LIMIT = False

"""
pusher / nodejs
"""
SOCKETIO_URL = 'http://localhost:8888/'
PUSHER_SETTINGS = {
    'MODELS': ('alibrary.playlist',),
}

"""
using django pushy!!
"""
PUSHY_SETTINGS = {
    'MODELS': (
        'alibrary.playlist',
        'importer.import',
        'importer.importfile',
        'abcast.emission',
    ),
    'SOCKET_SERVER': 'http://localhost:8888/',
    'CHANNEL_PREFIX': 'pushy_',
    'DEBUG': DEBUG
}

"""
ajax lookups
"""
AJAX_LOOKUP_CHANNELS = {
    'aliases': {'model': 'alibrary.artist', 'search_field': 'name'}
}
# AJAX_SELECT_BOOTSTRAP = True
# AJAX_SELECT_INLINES = 'inline'




# media conversion
"""
stream - defaults to: mp3, highest available bitrate.
would theoretically be possible to implement bitrate-switching
depending on users connection.
"""
FORMATS_STREAM = {
    'mp3': [128],
}
FORMATS_DOWNLOAD = {
    'mp3': [192],
    'flac': ['base'],
    'wav': ['base'],
}

WAVEFORM_SIZES = {
    's': [100, 20],
    'm': [300, 30],
    'l': [600, 100],
}

IMAGE_BASE_SIZES = {
    'xs': '32',
    's': '64',
    'm': '160',
    'l': '512',
    #'xl': '1024',
}



# jenkins
PROJECT_APPS = (
    'aplayer',
    #'alibrary',
)
JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
    #'django_jenkins.tasks.run_csslint',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)
SOUTH_TESTS_MIGRATE = False

WYM_CONTAINERS = ",\n".join([
    "{'name': 'P', 'title': 'Paragraph', 'css': 'wym_containers_p'}",
    "{'name': 'H1', 'title': 'Heading_1', 'css': 'wym_containers_h1'}",
    "{'name': 'H2', 'title': 'Heading_2', 'css': 'wym_containers_h2'}",
    "{'name': 'H3', 'title': 'Heading_3', 'css': 'wym_containers_h3'}",
    "{'name': 'H4', 'title': 'Heading_4', 'css': 'wym_containers_h4'}",
    "{'name': 'BLOCKQUOTE', 'title': 'Blockquote', 'css': 'wym_containers_blockquote'}",
])

WYM_CLASSES = ",\n".join([
    "{'name': 'date', 'title': 'PARA: Date', 'expr': 'p'}",
    "{'name': 'hidden-note', 'title': 'PARA: Hidden note', 'expr': 'p[@class!=\"important\"]'}",
])

ACTSTREAM_SETTINGS = {
    'MODELS': ('auth.user', 'auth.group', 'alibrary.release', 'alibrary.playlist', 'alibrary.artist', 'alibrary.media',
               'zinnia.entry', 'abcast.emission'),
    #'MANAGER': 'myapp.streams.MyActionManager',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 1,
}

import logging

logging.basicConfig(level=logging.DEBUG)
#logging.getLogger('django.db.backends').setLevel(logging.ERROR)

# try to override from local_config.py
DEBUG_APPS = None
try:
    from local_settings import *

    if DEBUG_APPS:
        INSTALLED_APPS += DEBUG_APPS
except ImportError:
    pass

