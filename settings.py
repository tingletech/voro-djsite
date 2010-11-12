import os
from config_reader import read_config

#To make project independent of absolute path:
PROJECT_ROOT = PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

SEND_BROKEN_LINK_EMAILS = True

DATABASES = read_config()

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles PST8PDT SystemV/PST8PDT US/Pacific US/Pacific-New'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join([PROJECT_PATH, 'site_media'])

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'site_media'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    #'django.middleware.gzip.GZipMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

CACHE_BACKEND = 'file:///dsc/workspace/cache/django'
CACHE_MIDDLEWARE_SECONDS = 12*60*60
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, "oac", "templates"),
    os.path.join(PROJECT_PATH, "arkComments", "templates"),
    os.path.join(PROJECT_PATH, "templates"),
)

AUTHENTICATION_BACKENDS = (
                           'xtf.perm_backend.XTFObjectOwnerPermBackend',
                           'xtf.perm_backend.ARKObjectOwnerPermBackend',
                           'django.contrib.auth.backends.ModelBackend',
                          )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.comments',
    'contact',
    'oac',
    'ssi',
    'passwd_md5',
    'request_acct',
    'xtf',
    'themed_collection'
)

# for ssi includes, remove once SSI apache working
SSI_ROOT = os.environ.get('DJANGO_SSI_ROOT', '/dsc/webdocs/www.oac.cdlib.org/')
ALLOWED_INCLUDE_ROOTS = (
    SSI_ROOT,
)

AUTH_PROFILE_MODULE = 'oac.userprofile'

#SESSION_COOKIE_SECURE = 'False'

# this uses pinax style import of local_settings
try:
    from local_settings import *
except ImportError: 
    import sys
    sys.stderr.write("WARNING: NO local_settings found. Using PRODUCTION VALUES")
except:
    import sys
    sys.stderr.write("Error importing local_settings.py\n")
    sys.stderr.write("TYPE:"+str(sys.exc_info()[0])+'\n')
    sys.stderr.write("MSG:"+str(sys.exc_info()[1]))
    sys.stderr.write('\n\n')
