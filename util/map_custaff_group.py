import os, sys
import random
import math

FILE_PATH = os.path.abspath(os.path.split(__file__)[0])
DJSITE_DIR = os.path.join(FILE_PATH, '..')

sys.path.append(DJSITE_DIR)

# set the DJANGO_SETTINGS_MODULE 
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

import django
from django.contrib.auth.models import User, Group, Permission 


def main():
    users = User.objects.all()
    for user in users:
            g = user.groups.filter(name='custaff')
            if g:
                print user 
                groupToAdd = Group.objects.get(name='cabeurle')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cubanc')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cubfa')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cuceda')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cueth')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cuhm')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cuit')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cumusi')
                user.groups.add(groupToAdd)
                groupToAdd = Group.objects.get(name='cuwr')
                user.groups.add(groupToAdd)
                #user.save()

if __name__=='__main__':
    main()
