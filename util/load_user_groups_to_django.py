#! /usr/bin/python

'''
This script loads the data in institution_employees, edit_groups and edit_groups_institution_employees into the Django user auth system. We still need to provide additional information for both groups and employees. For groups: directory, institution id, and note are additional. For employess phone number is additional. employees can be handled by a django user profile (how to make specific to voro users only). For groups, we will use edit_groups and add a foreign key to the table that references auth_group
'''
import os, sys

# set the DJANGO_SETTINGS_MODULE 
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

#print "sys.path = %s " % sys.path

import django
# import site settings, gives access to db & models
from django.conf import setttings
from repodata.models import Institution_Employee, Edit_Group, Institution

def set_institution_user_perms(user):
    '''Sets the user's permissions for an institution employee
    user is a Django auth_user passed in
    This should go into load_users
    '''
    user.is_staff = True;
    perm_change_inst = django.contrib.auth.models.Permission.objects.get(id=29)
    user.user_permissions.add(perm_change_inst)


def load_users():
    '''
    load usernames from Institution_Employee into auth_users in Django
    '''
    # get Instituion_employees
    employees = Institution_Employee.objects.all()
    for employee in employees:
        #parse name, use last token as last name, rest as first
        (first_name, last_name) = employee.name.rsplit(None,1)
        django_user = django.contrib.auth.models.User(username=employee.login,
                                                      email=employee.email,
                                                      first_name=first_name,
                                                      last_name=last_name)
        django_user.save() # must save before adding ManyToMany keys
    # get the Edit_Groups for employee
        e_groups = employee.group.all()
    # for each Edit_group lookup the corresponding Django group (groups must be 
        for e_grp in e_groups:
            django_user.groups.add(e_grp.group_id)
        django_user.save()

def load_groups():
    '''
    load groups from edit groups into auth_groups in Django
    update the foreign key for edit_groups to point at the new group id
    '''
    # get Edit_Groups
    e_groups = Edit_Group.objects.all()
    for g in e_groups:
        # create a Django group
        django_group = django.contrib.auth.models.Group(name=g.name)
        django_group.save()
        # for the edit_group, update foreign key to new group id
        g.group_id = django_group.id
        g.save()


def load_user_passwords(pfile):
    '''
    pFile is string path to davpass cleartext password file
    '''
    foo = open(pfile,'r')
    plist = [] # list of tuples, uname, password
    for line in foo:
        tokens = line.split(None)
        plist.append( (tokens[0], tokens[1]) )
    foo.close()
    for (uname, pswd) in  plist:
        #print "Uname=%s pswd=%s" % (uname, pswd)
        u = None
        try:
            u = django.contrib.auth.models.User.objects.get(username=uname)
        except django.contrib.auth.models.User.DoesNotExist:
            print "Uname=%s not in users db" % uname
            continue
        u.set_password(pswd)
        u.save()
        print "Set user:%d, uname:%s password to %s" % (u.id, u.username, pswd)




if __name__ == "__main__":
    '''
    load_groups()
    load_users()
    load_user_passwords("/findaid/data/users/davpass.txt")
    '''
    users = django.contrib.auth.models.User.objects.all()
    for user in users:
        if not user.is_superuser:
            set_institution_user_perms(user)

