''' read in the oac_participants data and attempt to update OAC Django models
according to data read. Will attempt to set the oac_listserv & voroead account
bools and set primary contact for intitution. Will use email to filter users and
attempt to look up inst names for primary contacts
Must run from djsite homedir with django_admin.py shell <
./oac/util/set_participant_data.py
'''

from django.contrib.auth.models import User
from oac.models import Institution, UserProfile

import csv
filename = './oac/util/oac_participants.csv'
foo = file(filename, 'U')
r = csv.reader(foo)
parts = []
for line in r:
    parts.append(line)

print len(parts)

for row in parts:
    #get email and attempt to lookup user
    email = row[6].strip()
    if email == '':
        print "No email for %s %s at %s" % (row[4], row[5], row[0])
        continue
    try:
        user = User.objects.get(email=email)
        try:
            prof = user.get_profile()
            if row[10].strip().lower() == 'n':
                prof.OAC_listserv = False
            if row[11].strip().lower() == 'y':
                prof.voroEAD_account = True
            else:
                prof.voroEAD_account = False
            print "User=%s R10=%s R11=%s pOAC=%s pVoro=%s" % (user, row[10].strip().lower(),
                                     row[11].strip().lower(),
                                     prof.OAC_listserv,
                                     prof.voroEAD_account)
            prof.save()
        except UserProfile.DoesNotExist:
            print "No profile for user:%s" % user
    except User.DoesNotExist:
        print "No Django user for %s : %s %s" % (email, row[4], row[5])
        continue
    # row[4] means primary contact, try to set on institution
    if row[4] != '':
        try:
            inst = Institution.objects.get(name=row[0].strip())
            print "FOUND INST: %s Set Primary_contact=%s" % (inst, user)
            inst.primary_contact = user
            inst.save()
        except Institution.DoesNotExist:
            print "No institution found for Primary Contact %s : %s %s Inst-name:%s" % (email,
                            row[4],
                            row[5],
                            row[0]
                            )
            continue
        except Institution.MultipleObjectsReturned:
            print "Multiple Institutions for %s contact:%s : %s" % (row[0].strip(),
                                                               email,
                                                               row[4]
                                                              )
            continue
