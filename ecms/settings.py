# Django settings for ecms project.
# coding=utf-8
import os

_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
ALLLOG_FILENAME = os.path.join(_ROOT_PATH, 'logs/all.log').replace("\\", "/");
ECMSLOG_FILENAME = os.path.join(_ROOT_PATH, 'logs/ecms.log').replace("\\", "/");
SCRIPTLOG_FILENAME = os.path.join(_ROOT_PATH, 'logs/script.log').replace("\\", "/");

DEBUG = True
#TEMPLATE_DEBUG = DEBUG
TEMPLATE_DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

AUTH_PROFILE_MODULE='workflow.UserProfile'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': '/Users/tanleon/Documents/ECMS/ecms/ecms/sqlite3.db',                      # Or path to database file if using sqlite3.
        'NAME': os.path.join(_ROOT_PATH,'sqlite3.db').replace('\\','/'),
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE='zh-cn'
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
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.abspath(os.path.join(SITE_ROOT, '../'))

STATIC_ROOT = os.path.join(SITE_ROOT, 'collectedstatic')


# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(_ROOT_PATH, 'static').replace('\\','/'), #project-wide static files
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
SECRET_KEY = 'p-9!&amp;3q1e8btyl9gg9&amp;_lt!@3)locr1ac&amp;(!o!npwybev2kz$%'

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
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware'
)

ROOT_URLCONF = 'ecms.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ecms.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(_ROOT_PATH, 'templates').replace('\\','/'),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'workflow',
    'vmware',
    'tastypie',
    'UI',
    'EUAO',
    'aix',
    'charge',
    'batch',
)
TASTYPIE_SWAGGER_API_MODULE = 'workflow.api'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {'version': 1,  
    'disable_existing_loggers': True,  
    'formatters': {  
        'standard': {  
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(pathname)s:%(lineno)d] [%(levelname)s]- %(message)s'  
        },
        'ecms_log':{
            'format': '%(asctime)s [%(name)s:%(filename)s:%(lineno)d] [%(levelname)s]- %(message)s'  
        },
    },  
    'filters': {  
    },  
    'handlers': {
        'default': {  
            'level':'DEBUG',  
            'class':'logging.handlers.RotatingFileHandler',  
            'filename': ALLLOG_FILENAME, #或者直接写路径：'c://logs/all.log',  
            'maxBytes': 1024*1024*5, # 5 MB  
            'backupCount': 5,  
            'formatter':'standard',  
        },
        'ecms_default': {
           'level':'DEBUG',  
            'class':'logging.handlers.RotatingFileHandler',  
            'filename': ECMSLOG_FILENAME, #或者直接写路径：'c://logs/all.log',  
            'maxBytes': 1024*1024*1, # 5 MB  
            'backupCount': 5,  
            'formatter':'ecms_log',
        },
        'request_handler': {  
            'level':'DEBUG',  
            'class':'logging.handlers.RotatingFileHandler',  
            'filename': SCRIPTLOG_FILENAME, #或者直接写路径：'filename':'c:/logs/request.log''              
            'maxBytes': 1024*1024*5, # 5 MB  
            'backupCount': 5,  
            'formatter':'standard',  
        },  
        'scprits_handler': {  
            'level':'DEBUG',  
            'class':'logging.handlers.RotatingFileHandler',  
            'filename': SCRIPTLOG_FILENAME, #或者直接写路径：'filename':'c:/logs/script.log'  
            'maxBytes': 1024*1024*5, # 5 MB  
            'backupCount': 5,  
            'formatter':'standard',  
        },  
    },  
    'loggers': {  
        'django': {  
            'handlers': ['default'],  
            'level': 'INFO',  
            'propagate': False  
        },
        'ecms': {
            'handlers': ['ecms_default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django.request': {  
            'handlers': ['request_handler'],  
            'level': 'DEBUG',  
            'propagate': False  
        },  
        'scripts': { # 脚本专用日志  
            'handlers': ['scprits_handler'],  
            'level': 'INFO',  
            'propagate': False  
        },  
    }  
}  


LOGIN_URL='/login'