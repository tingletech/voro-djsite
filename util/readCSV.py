import os, sys
settings_dir = os.path.join(os.path.abspath(os.path.split(__file__)[0]), '..')
sys.path.append(settings_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
from django.contrib.auth.models import User, Group

from oac.models import *

import csv
filename = 'bct_copy_dsc_institutions_melvyl_marc.csv'
foo = file(filename, 'U')
r = csv.reader(foo)
for line in r:
        (campus_name, primary_loc, primary_loc_display, flag, melvyl_name) = line
        #create new db entry (MARC_PrimaryNameDisplay)
        marcmap = MARC_PrimaryNameDisplayMap(campus_name=campus_name,
                                              primary_loc=primary_loc,
                                              primary_loc_display=primary_loc_display,
                                              flag=flag,
                                              melvyl_name = melvyl_name
                                             )

        marcmap.save()
