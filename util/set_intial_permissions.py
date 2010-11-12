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
    users = User.objects.filter(is_superuser=False)
    permEdit = Permission.objects.get(id=8)
    for user in users:
        user.user_permissions.add(permEdit)
        user.save()

    groups = Group.objects.all()
    permEdit = Permission.objects.get(id=42)
    for group in groups:
        group.permissions.add(permEdit)
        group.save()

if __name__=='__main__':
    main()
