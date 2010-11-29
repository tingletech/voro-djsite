import os.path
import sys

from settings import *

#muck with path to get apps dir in
sys.path.insert(0, os.path.join(PROJECT_ROOT, "apps"))

err_stream = sys.stderr.write
    
err_stream("test_settings overriding default settings...\n")
DEBUG = True
TEMPLATE_DEBUG = DEBUG

FIXTURE_DIRS = (os.path.join(PROJECT_ROOT, 'fixtures'),)
print "FIXTURE_DIRS:", FIXTURE_DIRS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db/oac4dev'),
    }
}

FIXTURE_DIRS = (os.path.join(PROJECT_ROOT, 'fixtures'),)

MD5_REALM = 'voro user'
MD5_SHELF = './users.digest'

sys.stderr.write('\n\nDATABASES:'+str(DATABASES)+'\n\n')
