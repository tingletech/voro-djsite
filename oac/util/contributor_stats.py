#! /usr/bin/python
'''This script generates a csv file that reports the date time of the last 
submitted EAD for all the institutions.
'''

import os, sys, os.path
import datetime
import csv
import StringIO
import collections
import xml.etree.ElementTree as ET
import cgitb; cgitb.enable(format='text')

FILE_PATH = os.path.abspath(os.path.split(__file__)[0])
DJSITE_DIR = os.path.join(FILE_PATH, '..')
EAD_ROOT_DIR = '/dsc/data/in/oac-ead/prime2002/'

sys.path.append(DJSITE_DIR)

# set the DJANGO_SETTINGS_MODULE 
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from oac.models import Institution 


def find_latest_files(root_dir):
    '''Returns a dictionary, keyed by the subdir from <root_dir>
    with the date of the latest file found in the subdirectory
    '''
    latest_file_times = {}
    for root, dirs, files in os.walk(root_dir):
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
    return latest_file_times

def parse_ingest_stats():
    '''Parse the ingest_stats.txt file produced by MAR's scripts.
    Return 2 dictionaries, one of EADs one of METS, both ark indexed.
    Each dict value is a list of the entries in ingest_stats.txt
    --May want to map to inst now?'''
    f = open('/voro/ingest/data/ingest_stats.txt')
    EAD = collections.defaultdict(list)
    METS = collections.defaultdict(list)
    reader = csv.reader(f, delimiter=' ')
    for row in reader:
        object_dir, type, filename, status, timestamp, extra = row
        ark = filename[0:filename.index('.')]
        #print ark, type, filename
        if type == 'METS':
            METS[ark].append([object_dir, status, timestamp, extra])
        elif type == 'EAD':
            EAD[ark].append([object_dir, status, timestamp, extra])
        else:
            raise ValueError('Type must be EAD or METS')
    return EAD, METS

def find_institution_from_ARK(ark):
    try:
        inst = Institution.objects.get(ark=ark)
    except Institution.DoesNotExist:
        inst = None
    return inst

def find_institution_for_EAD(EAD_info):
    '''Find the institution for the given EAD entry. EAD info is a list of
    directory, status, timestamp and extra ingest data. The extra should be of
    form ark:/13030/<inst_ark>. Can use ark to look up institution'''
    inst_ark = EAD_info[0][3]
    return find_institution_from_ARK(inst_ark)

def parse_ark(ark_str):
    '''parse out significant part of ark'''
    return ''.join(('ark:/13030/', ark_str[(ark_str.rindex('/')+1):]))

def parse_ead_url(ead_url):
    '''parse the ark from the URL for the ead'''
    return ead_url[ead_url.rindex('/'):]

def find_EAD_ARK_for_METS(ark, directory):
    '''For a given METS directory, find the EAD's ark for the containing EAD.
    This parses the dc.xml file, looks for relation tags with a q attribute of
    "ispartof". It then looks for values that match "ark://" or
    "http://www.oac.cdlib.org/". It then attempts to lookup the finding aid
    in our EAD data structure...
    '''
    ead_ark = None
    inst_ark = None
    foo = open(os.path.join(directory, ''.join((ark, '.dc.xml'))))
    # will elementtree suffice? probably need lxml
    tree = ET.parse(foo)
    foo.close()
    relations = tree.findall("./relation")
    for relation in relations:
        q = relation.attrib.get('q', None)
        if q:
            if q.lower() == 'ispartof':
                if not relation.text:
                    continue
                elif relation.text.find('ark:/13030/') == 0:
                    inst_ark = parse_ark(relation.text)
                elif relation.text.find('http://www.oac.cdlib.org/findaid/ark:/') > -1:
                    ead_ark = parse_ead_url(relation.text)
                elif relation.text.find('http://oac.cdlib.org/findaid/ark:/') > -1:
                    ead_ark = parse_ead_url(relation.text)
                #check the text, if ark: or http://www.oac.cdlib.org/findaid/
#we can parse and get EAD ark
    return ead_ark, inst_ark


def csvEADDict(EAD):
    '''Return a csv represenation of the EAD dict'''
    fout = StringIO.StringIO()
    writer = csv.writer(fout)
    writer.writerow(('EAD ARK', 'Path', 'Status', 'Timestamp', 'Institution',))
    for ark, ead_infos in EAD.items():
        for fpath, status, timestamp, extra in ead_infos:
            writer.writerow((ark, fpath, status, datetime.date.fromtimestamp(float(timestamp)), find_institution_for_EAD(ead_infos),))
    csvStr = fout.getvalue()
    fout.close()
    return csvStr


def getEADTimeSlice(EAD, start_date, end_date):
    EAD_time_filtered = collections.defaultdict(list)
    for ark, ead_infos in EAD.items():
        for fpath, status, timestamp, extra in ead_infos:
            if (start_date <= datetime.date.fromtimestamp(float(timestamp)) <= end_date):
                EAD_time_filtered[ark].append((fpath, status, timestamp, extra))
    return EAD_time_filtered

def csvMETSDict(METS, EAD):
    fout = StringIO.StringIO()
    writer = csv.writer(fout)
    writer.writerow(('METS ARK', 'Path', 'Status', 'Timestamp', 'Institution',))
    for ark, mets_infos in METS.items():
        for fpath, status, timestamp, extra in mets_infos:
            ead_ark, inst_ark =  find_EAD_ARK_for_METS(ark, mets_infos[0][0])
            inst = "Unable to determine"
            if inst_ark:
                inst = find_institution_from_ARK(inst_ark)
            elif ead_ark:
                if EAD[ead_ark]:
                    inst = find_institution_for_EAD(EAD[ead_ark])
            writer.writerow((ark, fpath, status, datetime.date.fromtimestamp(float(timestamp)), str(inst)))
    csv_str = fout.getvalue()
    fout.close()
    return csv_str

def getMETSTimeSlice(METS, start_date, end_date):
    METS_time_filtered = collections.defaultdict(list)
    for ark, mets_infos in METS.items():
        for fpath, status, timestamp, extra in mets_infos:
            if (start_date <= datetime.date.fromtimestamp(float(timestamp)) <= end_date):
                METS_time_filtered[ark].append((fpath, status, timestamp, extra))
    return METS_time_filtered

def csvByInstitutionIngest():
    institutions = Institution.objects.all()
    latest_prime2002_times = find_latest_files(EAD_ROOT_DIR)
    fout = StringIO.StringIO()
    writer = csv.writer(fout)
    writer.writerow(('Institution', 'Parent Institution', 'Address1', 'Address2', 'City', 'Zip', 'Inst. email', 'Inst. phone', 'Inst. URL', 'Contact Name', 'Contact email', 'Contact phone', 'Path', 'Setup Date', 'Latest EAD Time'))
    for inst in institutions:
        latest = latest_prime2002_times.get(inst.cdlpath, None)
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
        writer.writerow((inst.name.encode('utf-8'), parent_name, inst.address1.encode('utf-8') if inst.address1 else '', inst.address2.encode('utf-8') if inst.address2 else '', inst.city, inst.zip4.encode('utf-8') if inst.zip4 else '', inst.email.encode('utf-8') if inst.email else '', inst.phone.encode('utf-8') if inst.phone else '', inst.url.encode('utf-8'), contact, contact_email, contact_phone, inst.cdlpath, inst.created_at.strftime('%Y-%m-%d'), str(latest.strftime('%Y-%m-%d') if latest else None)))

    csv_str = fout.getvalue()
    fout.close()
    return csv_str

def main(args):
    start=datetime.datetime.now()
    EAD, METS = parse_ingest_stats()
#    for ark in EAD.keys():
#        inst = find_institution_for_EAD(EAD[ark])
#        if not inst:
#            print "NO INSTITUTION FOR ", ark
#    for ark in METS.keys():
#        ead_ark =  find_EAD_ARK_for_METS(ark, METS[ark][0][0])
#        if not ead_ark:
#            print "NO EAD ARK FOUND FOR: ", ark
#        if len(METS[ark]) > 1:
#            print ark, METS[ark]

    
    start_date = datetime.date(2010,01,01)
    end_date = datetime.date.today()
    EAD_time_filtered = getEADTimeSlice(EAD, start_date, end_date)
    csv_ead_report = csvEADDict(EAD_time_filtered)
    foo = open('ead_report.csv', 'w')
    foo.write(csv_ead_report)
    foo.close()
    #print "TIME FILTERED", EAD_time_filtered

    METS_time_filtered = getMETSTimeSlice(METS, start_date, end_date)
    foo = open('mets_report.csv', 'w')
    foo.write(csvMETSDict(METS_time_filtered, EAD))
    foo.close()


    #print "TIME FILTERED", METS_time_filtered
    end=datetime.datetime.now()
    print "\n\nTHE LATEST UPDATES RUN TOOK", end-start

    fout = open('institution_last_active.csv', 'w')
    fout.write(csvByInstitutionIngest())
    fout.close()

    end=datetime.datetime.now()
    print "\n\nWHOLE BANANA RUN TOOK", end-start


if __name__=="__main__":
    main(sys.argv)
