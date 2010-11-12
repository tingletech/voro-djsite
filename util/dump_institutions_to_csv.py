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
from oac.models import Institution, City, County

def main(args):
    with open('institutions.csv','w') as f:
        fieldnames = ['name', 'email', 'phone', 'url', 'address1', 'address2',
                      'city', 'county', 'zip4', 'ark'
                     ]
        csvFile = DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        # write header row
        field_dict = dict([(x, x.capitalize()) for x in fieldnames])
        csvFile.writerow(field_dict)
        for inst in Institution.objects.all():
            # look up City
            inst.__dict__['city'] = inst.city.name
            inst.__dict__['county'] = inst.county.name
            inst.__dict__['name'] = inst.name.encode('utf-8')
            inst.__dict__['email'] = inst.email.encode('utf-8') if inst.email else None 
            inst.__dict__['phone'] = inst.phone.encode('utf-8') if inst.phone else None 
            inst.__dict__['url'] = inst.url.encode('utf-8') if inst.url else None 
            inst.__dict__['address1'] = inst.address1.encode('utf-8') if inst.address1 else None 
            inst.__dict__['address2'] = inst.address2.encode('utf-8') if inst.address2 else None 
            inst.__dict__['zip4'] = inst.zip4.encode('utf-8') if inst.zip4 else None 
            csvFile.writerow(inst.__dict__, )

if __name__=="__main__":
    main(sys.argv)
