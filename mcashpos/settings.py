# Django settings for mcashpos project.
import inspect
import os

SITE_ROOT = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(SITE_ROOT, 'pos.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, '../django-static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ftb8_a@#6drzbakut0j^6*6qjd)7=i-q^(4w6j1l13n!ym6vop'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mcashpos.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'mcashpos.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'gunicorn',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mcashpos',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


class POS_SETTINGS(object):
    MCASH_SERVER = 'https://mcashdevelop.appspot.com/'
    MERCHANT_API_URL = MCASH_SERVER + 'merchant/v1'
    MERCHANT_ID = '2nslnb'
    USER_ID = 'pos1'
    POS_ID = '1'
    TESTBED_TOKEN = 'z0YhQz36gbukcS7tdKy-uyVDvX4Hlr7kM_cizah2_EI'
    MCASH_SECRET = 'supersecret'
    CURRENCY = 'NOK'
    SHORTLINK_ID = '---0'
    PUSHER_APP_ID = '39544'
    PUSHER_APP_KEY = 'b9ad66f2dcad7152fb47'
    PUSHER_SERVER = 'http://api.pusherapp.com/'
    PUSHER_APP_URL = '%s/apps/%s' % (PUSHER_SERVER, PUSHER_APP_ID)
    PUSHER_CHANNEL_PREFIX = 'm-%s-' % MERCHANT_ID

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)

    def as_dict(self):
        return {key: value for key, value in filter(lambda a: a[0].upper() == a[0], inspect.getmembers(self))}

    def as_json(self):
        import json
        import re
        r = re.compile(r'_(\w)')
        d = self.as_dict()
        for key in d.keys():
            d[r.sub(lambda pat: pat.group(1).upper(), key.lower())] = d.pop(key)
        return json.dumps(d)


PUSHER_APP_SECRET = 'fcac654dc089308ae627'
import pusher
pusher.app_id = POS_SETTINGS.PUSHER_APP_ID
pusher.key = 'e36a43a6022a7610678f'
pusher.secret = PUSHER_APP_SECRET

from mcashpos.pos import POS
POS.api_url = POS_SETTINGS.MERCHANT_API_URL
POS.merchant_id = POS_SETTINGS.MERCHANT_ID
POS.pos_id = POS_SETTINGS.POS_ID
POS.secret = POS_SETTINGS.MCASH_SECRET
POS.user_id = POS_SETTINGS.USER_ID
POS.testbed_token = POS_SETTINGS.TESTBED_TOKEN
