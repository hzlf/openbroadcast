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
# subdirectory for plugins
sys.path.insert(0, os.path.join(PROJECT_DIR, 'cmsplugins'))
# subdirectory for shop
sys.path.insert(0, os.path.join(PROJECT_DIR, 'shop'))

DEBUG = True

TEMPLATE_DEBUG = DEBUG
SERVE_MEDIA = False
COMPRESS_OFFLINE = False
COMPRESS_ENABLED = False


LANGUAGES = [('en', 'en'), ('de', 'de')]
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

TEMPLATE_LOADERS = (    
    # 'django.template.loaders.filesystem.load_template_source', # depreceated
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (                
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'pagination.middleware.PaginationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # cms
    'cms.middleware.multilingual.MultilingualURLMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    # custom
    #'lib.middleware.ProfileMiddleware',
    #'lib.middleware.PrettifyMiddlewareBS',
)

CACHE_BACKEND = 'locmem:///'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'notification.context_processors.notification',
    #'announcements.context_processors.site_wide_announcements',
    # cms
    'cms.context_processors.media',
    # staticfiles
    'django.core.context_processors.static',
    'sekizai.context_processors.sekizai',
    # multilingual
    'multilingual.context_processors.multilingual',
    
    # authentication
    'allauth.context_processors.allauth',
    'allauth.account.context_processors.account',
)


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
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
)

WIDTH_INNER = 960
CMS_PLACEHOLDER_CONF = {
    'main': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width":WIDTH_INNER},
        'name':gettext("Main Content"),
    },
    'template_1_content_2': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width":300},
        'name':gettext("FlexBox"),
    },
    'sidebar_pre': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width":280},
        'name':gettext("Sidebar | Pre-Menu"),
    },
    'sidebar_post': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width":280},
        'name':gettext("Sidebar | Post-Menu"),
    },
    'placeholder_1': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {"width":WIDTH_INNER},
        'name':gettext("Main Content"),
    },
    # home slots
    'home_slot_a': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name':gettext("Home | Slot A"),
    },
    'home_slot_b': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name':gettext("Home | Slot B"),
    },
    'home_slot_c': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name':gettext("Home | Slot C"),
    },
    'home_slot_d': {
        #"plugins": ('TeaserPlugin', 'LinkPlugin'),
        "extra_context": {},
        'name':gettext("Home | Slot D"),
    },
}

CMS_APPLICATIONS_URLS = (
    ('cmsplugin_advancednews.urls', 'News'),
)
CMS_NAVIGATION_EXTENDERS = (
    ('cmsplugin_advancednews.navigation.get_nodes','News navigation'),
)

CMS_PLUGIN_PROCESSORS = (
    'lib.cms_plugin_processors.wrap_text',
)

CMS_SEO_FIELDS = True

CMS_CACHE_DURATIONS = {
    'menus': 1,
    'content': 1,
}

CMS_VIMEO_DEFAULT_WIDTH = 630
CMS_VIMEO_DEFAULT_HEIGHT = 360

CMS_YOUTUBE_DEFAULT_WIDTH = 630
CMS_YOUTUBE_DEFAULT_HEIGHT = 350

# media deliver
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/media/'

# static files (application js/img etc)
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

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
)




INSTALLED_APPS = (
                  
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.webdesign',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.staticfiles',
    'django.contrib.markup',
    
    # core apps
    'django_extensions',
    'django_jenkins',

    'notification',
    'debug_toolbar',
    'mailer',
    'djcelery',
    
    'cms',
    'menus',
    'mptt',
    'south',
    'polymorphic',
    'django_countries',
    'guardian',
    'filer',
    
    
    'sendfile',
    
    
    # cms plugins
    'cms.plugins.text',
    #'cmsplugin_filer_folder',
    #'cmsplugin_filer_image',
    #'cmsplugin_youtube',
    #'cmsplugin_vimeo',
    #'cmsplugin_soundcloud',
    'cmsplugin_pagedown',

    'multilingual',
    'disqus',
    
    # asset and media handling
    'sekizai',
    'compressor',
    'easy_thumbnails',
    
    
    # rest & API
    'djangorestframework',
    
    
    # users/auth
    'avatar',
    'emailconfirmation',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #'allauth.ajax',
    #'allauth.twitter',
    'allauth.openid',
    'allauth.facebook',

    

    
    # custom apps/*
    'asite',
    'alibrary',
    'aplayer',
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
    'taggit',
    'tagging',
    'pure_pagination',
    #'taggit_templatetags',
    
    'obp_legacy',
    
    # helpers
    'dev',
)



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
    'mp3': ['base', 'low'],    
}

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


"""
Filer related settings
"""
FILER_IS_PUBLIC_DEFAULT = True
FILER_ENABLE_PERMISSIONS = True
FILER_STATICMEDIA_PREFIX = '/static/filer/'

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
# EMAIL_BACKEND = 'mailer.backend.DbBackend'


EMAIL_CONFIRMATION_DAYS = 5
EMAIL_DEBUG = DEBUG

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


"""
Identity
"""
CONTACT_EMAIL = 'root@dock18.ch'
ADMINS = (
    ('anorg', 'network@anorg.net'),
)
MANAGERS = ADMINS


"""
Accounts
"""
AUTHENTICATION_BACKENDS = (
    # userena
    'allauth.account.auth_backends.AuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    # base
    'django.contrib.auth.backends.ModelBackend',
)
ANONYMOUS_USER_ID = -1
#AUTH_PROFILE_MODULE = 'profiles.Profile'


LOGIN_REDIRECT_URL = '/accounts/%(username)s/'
LOGIN_URL = '/accounts/signin/'
LOGOUT_URL = '/accounts/signout/'
LOGIN_REDIRECT_URL = "/"

USERENA_ACTIVATION_REQUIRED = False

ACCOUNT_EMAIL_REQUIRED=False
ACCOUNT_EMAIL_VERIFICATION=False
ACCOUNT_EMAIL_AUTHENTICATION=False
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION=True
ACCOUNT_UNIQUE_EMAIL=True
ACCOUNT_USERNAME_REQUIRED=True
SOCIALACCOUNT_QUERY_EMAIL=ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_AUTO_SIGNUP=True
EMAIL_CONFIRMATION_DAYS=5


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

# other...
PRETTIFY = True



DISQUS_API_KEY = 'hLRbAlPsBN6G11HyeNX4qMWiebrLZeVzLpUUimq82jsthcFBohQFMTAwS1iCBjie'
DISQUS_WEBSITE_SHORTNAME = 'hulahoneys'




"""
Other app related
"""

"""
wikisyntax, eg allows tor resolve [a:Artists Name] to object
"""
WIKISYNTAX = (
    ('r','alibrary.util.object_linker.WikiRelease'),
    ('a','alibrary.util.object_linker.WikiArtist'),
)
WIKISYNTAX_DISABLE_CACHE = True

"""
sendfile, delivers bought relases/tracks
"""
SENDFILE_BACKEND = 'sendfile.backends.simple'



"""
celeryd
"""
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

"""
streaming server
"""
RTMP_HOST = '127.0.0.2'
RTMP_APP = 'alibrary'
RTMP_PORT = '1935'


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



import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('django.db.backends').setLevel(logging.ERROR)

# try to override from local_config.py
""""""
try:
    from local_settings import *
except ImportError:
    pass

