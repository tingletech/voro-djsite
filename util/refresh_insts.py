import os, sys, os.path
import datetime

FILE_PATH = os.path.abspath(os.path.split(__file__)[0])
DJSITE_DIR = os.path.join(FILE_PATH, '..')
APPS_DIR = os.path.join(DJSITE_DIR, 'apps')

sys.path.append(DJSITE_DIR)
sys.path.append(APPS_DIR)

# set the DJANGO_SETTINGS_MODULE 
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from django.conf import settings
print settings.DATABASES
from oac.models import Institution 

for inst in Institution.objects.all():
    inst.save(force_update=True)
