#! /usr/bin/python
'''This script generates a csv file that reports the date time of the last 
submitted EAD for all the institutions.
'''

import os, sys, os.path
import datetime
import csv
import cgitb; cgitb.enable(format='text')

FILE_PATH = os.path.abspath(os.path.split(__file__)[0])
DJSITE_DIR = os.path.join(FILE_PATH, '..')
EAD_ROOT_DIR = '/dsc/data/in/oac-ead/prime2002/'

sys.path.append(DJSITE_DIR)

# set the DJANGO_SETTINGS_MODULE 
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from oac.models import Institution 

def main(args):
    institutions = Institution.objects.all()
    latest_file_times = {}
    for root, dirs, files in os.walk(EAD_ROOT_DIR):
        # for current directory, find latest file time
        # filetimes are in secs from epoch 0
        latest = 0
        for f in files:
            cur_time = os.path.getmtime(os.path.join(root, f))
            if latest < cur_time:
                latest = cur_time
        # Convert latest to datetime and just put extra path 
        # as dict key
        if latest:
            latest_dt = datetime.date.fromtimestamp(latest)
        else:
            latest_dt = None
        subdir = root.replace(EAD_ROOT_DIR,'')
        latest_file_times[subdir] = latest_dt

    fout = open('institution_last_active.csv', 'w')
    writer = csv.writer(fout)
    writer.writerow(('Institution', 'Parnet Institution', 'Address1', 'Address2', 'City', 'Zip', 'Inst. email', 'Inst. phone', 'Inst. URL', 'Contact Name', 'Contact email', 'Contact phone', 'Path', 'Latest File Time'))
    for inst in institutions:
        latest = latest_file_times.get(inst.cdlpath, None)
        parent_name = inst.parent_institution.name.encode('utf-8') if inst.parent_institution else ''
        contact=''
        contact_phone=''
        contact_email=''
        if inst.primary_contact:
            contact = inst.primary_contact.get_full_name().encode('utf-8')
            contact_email = inst.primary_contact.email.encode('utf-8')
            try:
                contact_phone = inst.primary_contact.get_profile().phone.encode('utf-8')
            except:
                pass
        writer.writerow((inst.name.encode('utf-8'), parent_name, inst.address1.encode('utf-8') if inst.address1 else '', inst.address2.encode('utf-8') if inst.address2 else '', inst.city, inst.zip4.encode('utf-8') if inst.zip4 else '', inst.email.encode('utf-8') if inst.email else '', inst.phone.encode('utf-8') if inst.phone else '', inst.url.encode('utf-8'), contact, contact_email, contact_phone, inst.cdlpath, str(latest)))
    fout.close()

if __name__=="__main__":
    main(sys.argv)
