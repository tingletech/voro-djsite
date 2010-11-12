import os, sys
#sys.path.insert(0, '/findaid/local/pythonlib/')
#sys.path.insert(0, '/voro/local/pythonlib/')
#print >> sys.stderr, 'HI FROM WSGI STARTUP'
#print >> sys.stderr, unicode(sys.path)
#print >> sys.stderr, os.environ['LD_LIBRARY_PATH']
sys.stderr.flush()
import django.core.handlers.wsgi

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

#do pinax style setup
from os.path import abspath, dirname, join
from site import addsitedir

sys.path.insert(0, abspath(join(dirname(__file__), "../")))

from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

sys.path.insert(0, join(settings.PROJECT_PATH, "apps"))

application = django.core.handlers.wsgi.WSGIHandler()
