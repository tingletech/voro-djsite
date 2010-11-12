from __future__ import with_statement
import sys
from os.path import abspath, dirname, join
from csv import DictWriter

# import django settings
sys.path.insert(0, abspath(join(dirname(__file__), "../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../apps")))
from django.conf import settings
#os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get("DJANGO_SETTINGS_MODULE","settings")

from django.contrib.auth.models import User
from oac.models import Institution, UserProfile

def main(args):
    with open('users.csv','w') as f:
        fieldnames = ['username', 'first_name', 'last_name', 'email', 'phone', 'institution', 'voro_account'
                     ]
        csvFile = DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        # write header row
        field_dict = dict([(x, x.capitalize()) for x in fieldnames])
        csvFile.writerow(field_dict)
        for user in User.objects.all():
            # look up associated profile & inst
            try:
                profile = user.get_profile()
                phone = profile.phone
                voro_account = profile.voroEAD_account
            except UserProfile.DoesNotExist:
                phone = ''
                voro_account = False
            user.__dict__['phone'] = phone
            user.__dict__['voro_account'] = voro_account
            # inst through group
            groups = user.groups.all()
            instname = ''
            if len(groups):
                firstgroup = user.groups.all()[0]
                grpprofile = firstgroup.groupprofile
                insts = grpprofile.institutions.all()
                if len(insts):
                    instname = insts[0].name
                else:
                    instname = ''
            user.__dict__['institution'] = instname.encode('utf-8')
            csvFile.writerow(user.__dict__, )

if __name__=="__main__":
    main(sys.argv)

