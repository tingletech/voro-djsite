'''
This script loads Django User passwords from an existing clear text passwords
file.
'''
import os, sys

settings_dir = os.path.join(os.path.abspath(os.path.split(__file__)[0]), '..')
sys.path.append(settings_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = "local_settings"
from django.contrib.auth.models import User
from django.conf import settings

repopass_file = '/apps/findaid/data/users/davpass.txt'

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
        print "Uname=%s pswd=%s" % (uname, pswd)
        u = None
        try:
            u = User.objects.get(username=uname)
        except User.DoesNotExist:
            print "Uname=%s not in users db" % uname
            continue
        u.set_password(pswd)
        u.save()

if __name__ == '__main__':
    print 'Database:%s %s %s' % (settings.DATABASE_ENGINE,
                                 settings.DATABASE_NAME, settings.DATABASE_USER)
    print 'Passwords to load: %s' % (repopass_file)
    resp = raw_input('Continue loading passwords? (Y/n)')
    if resp == 'Y':
        load_user_passwords(repopass_file)
    else:
        print 'ABORTING'
