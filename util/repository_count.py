import os, sys
from os.path import abspath, dirname, join

#sys.path.insert(0, '/findaid/local/pythonlib/')
#sys.path.insert(0, '/ro/local/pythonlib/')
sys.path.insert(0, abspath(join(dirname(__file__), "../")))
# set the DJANGO_SETTINGS_MODULE 
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"


import django
# import site settings, gives access to db & models
from django.conf import settings
from oac.models import Institution
sys.path.insert(0, join(settings.PROJECT_PATH, "apps"))

insts = Institution.objects.all()

repos = []

print "TOTAL INSTS", len(insts)
for inst in insts:
    if inst.children.count() == 0:
        repos.append(inst)

#print repos

print "Individual repos in OAC:", len(repos)
