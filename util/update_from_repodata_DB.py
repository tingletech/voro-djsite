'''
This script is designed to update the Django db from the repodata sqllite
database. New records are added. Existing records are ignored

Need to keep a record of id mapping from old to new ids for various entities.
Then on updates, first do a lookup in this table. If found, don't update???
Mostly needed to reconstruct & maintain references between data.
'''
import os, sys
import sqlite3
import shelve
import logging

settings_dir = os.path.join(os.path.abspath(os.path.split(__file__)[0]), '..')
sys.path.append(settings_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = "local_settings"
from django.contrib.auth.models import User, Group

from oac.models import *

repodata_db = ''
repopass_file = ''

def read_repodata(table,where=None):
    '''Use sqlite3 interface to read repodata db
    Returns sqlite3 rows object for whole table
    '''
    conn = sqlite3.connect(repodata_db)
    #c = conn.cursor()
    SQL = 'SELECT * from %s' % table
    if where:
        SQL+=' %s;' % where
    db_rows = conn.execute(SQL)
    rows = [x for x in db_rows]
    #row_list = rows.fetchall()
    conn.close()
    #    c.close
    return rows



def get_id_mapping(shelf, key):
    obj = {}
    if shelf.has_key(key):
        obj = shelf[key]
    logging.info( 'ID mapping Obj for:%s == %s' % (key, obj))
    return obj

def save_id_mapping(shelf, key, obj):
    shelf[key] = obj

def is_update(map, key):
    new_id = None
    try:
        new_id = map[key]
    except KeyError, exObject:
        pass
    return new_id


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
            u = User.objects.get(username=uname)
        except User.DoesNotExist:
            print "Uname=%s not in users db" % uname
            continue
        u.set_password(pswd)
        u.save()




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        filename='./Xupdate_from_repodata_DB.log',
                        format='%(asctime)s %(levelname)s %(message)s',
                        filemode='w')
    logging.info('Start Reading from repodata')
    shelf = shelve.open("shelf_db")

    old2new_county = get_id_mapping(shelf, 'county')

    rows = read_repodata('counties')
    for row in rows:
        if not is_update(old2new_county, row[1]):
            county = County(name=row[1])
            county.save()
            old2new_county[row[1]] = county.pk
            logging.info("!!!NEW!!! County:%s" % county.name)
        else:
            #update how to treat???
            logging.warning("County to update:%s" % row[1])
            pass

    save_id_mapping(shelf, 'county', old2new_county)   

    

    old2new_city = get_id_mapping(shelf, 'city')
    rows = read_repodata('cities')
    for row in rows:
        if not is_update(old2new_city,row[1]):
            county_row= read_repodata('counties', 'WHERE ID = %s' % row[2])
            county = County.objects.get(name=county_row[0][1])
            city = City(name=row[1], county=county, latitude=row[3],
                    longitude=row[4], custom_zoom_level=row[5])
            city.save()
            old2new_city[row[1]] = city.pk
            logging.info("!!!NEW!!! city:%s" % city.name)
        else:
            logging.warning("city to update:%s" % row[1])
    save_id_mapping(shelf, 'city', old2new_city)


    old2new_institution = get_id_mapping(shelf, 'institution')
    rows = read_repodata('institutions')
    for row in rows:
        if not is_update(old2new_institution, row[1]):
            city_row = read_repodata('cities', 'WHERE ID = %s' % row[9])
            city = City.objects.get(name=city_row[0][1])
            county_row= read_repodata('counties', 'WHERE ID = %s' % row[10])
            county = County.objects.get(name=county_row[0][1])
            parent_institution = None
            if row[3]:
                try:
                    parent_institution = Institution.objects.get(ark=row[3])
                except Institution.DoesNotExist:
                    pass
                                                           
            isa_campus = True if row[19] == 'true' else False
            inst = Institution(id=row[0], ark=row[1],
                           parent_institution=parent_institution,
                               #parent_ark = row[3],
                           name=row[4], mainagency=row[5],
                           cdlpath=row[6], address1=row[8], city=city,
                           county=county, zip4=row[11], url=row[12],
                           region=row[13], latitude=row[14], longitude=row[15],
                           custom_zoom_level=row[16], description=row[17],
                           isa_campus=isa_campus)
            inst.save()
            old2new_institution[row[1]] = inst.pk
            logging.info("!!!NEW!!! institution:%s" % inst.name)
        else:
            logging.warning("institution to update:%s, ark:%s" % (row[4],
                                                                  row[1]))
    save_id_mapping(shelf, 'institution', old2new_institution)



    old2new_group = get_id_mapping(shelf, 'group')
    rows = read_repodata('edit_groups')
    for row in rows:
        '''associate group with Django auth group and GroupProfile'''
        if not is_update(old2new_group, row[1]):
            auth_group = Group(name=row[1])
            auth_group.save()
            old2new_group[row[1]] = auth_group.pk
            inst = None
            if row[3]:
                try:
                    inst_row = read_repodata('institutions',' WHERE ID = %s' %
                                             row[3])
                    inst = Institution.objects.get(ark=inst_row[0][1])
                except Institution.DoesNotExist:
                    pass
            group_profile = GroupProfile( group = auth_group,  directory=row[2],
                                         institution=inst, note = row[4])
            group_profile.save()
            logging.info("!!!NEW!!! group :%s" % auth_group.name)
        else:
            logging.warning("group to update:%s" % row[1])
    save_id_mapping(shelf, 'group', old2new_group)

    old2new_user = get_id_mapping(shelf, 'user')
    rows = read_repodata('institution_employees')
    for row in rows:
        if not is_update(old2new_user, row[1]):
            #need to create a Django aut user for this entry
            # then tie it to the proper group (mapping old group id to new
            # auth_group id
            
            # split existing name field:
            name_split = row[3].split()
            last_name = str(name_split[-1:][0])
            first_name = ' '.join(name_split[:-1])
            email = 'mark.redar@ucop.edu'
            if row[4]:
                email = row[4]
            auth_user = User(username=row[1], last_name=last_name,
                             first_name=first_name, email=email, is_staff=False,
                             is_active = True, is_superuser = False)

            auth_user.save()
            old2new_user[row[1]] = auth_user.pk
            logging.info( "inst_emp # =%s  djangoUserID=%s last=%s first=%s email=%s" % (row[0], auth_user.pk, last_name, first_name, email))
            user_profile = UserProfile(user=auth_user, phone=row[5])
            user_profile.save()
            '''
CREATE TABLE institution_employees ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "login" varchar(255) DEFAULT NULL, "group" varchar(255) DEFAULT NULL, "name" varchar(255) DEFAULT NULL, "email" varchar(255) DEFAULT NULL, "phone" varchar(255) DEFAULT NULL, "created_at" datetime DEFAULT NULL, "updated_at" datetime DEFAULT NULL);
           ''' 
            logging.info("!!!NEW!!! user:%s" % auth_user.username)
        else:
            logging.warning("user to update:%s" % row[1])

    save_id_mapping(shelf, 'user', old2new_user)

    old2new_group_employee = get_id_mapping(shelf, 'group_employee')
    # this will be in the new group to user mapping
    rows = read_repodata('edit_groups_institution_employees')
    for row in rows:
        inst_emp_row = read_repodata('institution_employees', ' WHERE ID = %s' % row[1])
        inst_emp_login = inst_emp_row[0][1]
        edit_group_row = read_repodata('edit_groups', ' WHERE ID = %s' % row[2])
        edit_group_name = edit_group_row[0][1]

        combine_id = inst_emp_login + ':' +  edit_group_name
        if not is_update(old2new_group_employee, combine_id):
            # for each row in old db, take institution_employee_id (row[1]) and map
            # to new user id. 
        # Take edit_group_id (row[2]) and map to new group id
            auth_user = User.objects.get(username=inst_emp_login)
            auth_group = Group.objects.get(name=edit_group_name)
            # then make new entry in auth_user_groups
            auth_user.groups.add(auth_group)
            auth_user.save()
            # save the mapping in the old2new_group_employee dictionary
            # this will probably need to be a bit more sophisticated
            old2new_group_employee[combine_id] = str(auth_user.pk) + ':' + str(auth_group.pk)
        else:
            pass

    save_id_mapping(shelf, 'group_employee', old2new_group_employee)

    old2new_collection = get_id_mapping(shelf, 'collection')
    rows = read_repodata('collections')
    for row in rows:
        if not is_update(old2new_collection, row[1]):
            coll = Collection(ark=row[1], call_number=row[2], file_title=row[3],
                              date=row[4], extent=row[5], online_items=row[6],
                              description=row[7], source_record_type=row[8],
                              suppress=row[9], status=row[10])
            coll.save()
            # add an ark object for this collection
            arkObj = ArkObject(ark=row[1], app_label=Collection._meta.app_label,
                               model_name=Collection._meta.object_name.lower())
            arkObj.save()
            old2new_collection[row[1]] = coll.pk
            logging.info("!!!NEW!!! collection:%s and ArkObject" % coll.ark)
        else:
            logging.warning("collection to update:%s" % row[1])
    save_id_mapping(shelf, 'collection', old2new_collection)

    old2new_collection_institution = get_id_mapping(shelf, 'collection_institution')
    rows = read_repodata('collections_institutions')
    for row in rows:
        coll_row = read_repodata('collections',' WHERE ID = %s' % row[1])
        coll_ark = coll_row[0][1]
        inst_row = read_repodata('institutions', ' WHERE ID = %s' % row[2])
        inst_ark = inst_row[0][1]
        
        combine_id = coll_ark + ':' + inst_ark
        if not is_update(old2new_collection_institution, combine_id):
            coll = Collection.objects.get(ark=coll_ark)
            inst = Institution.objects.get(ark=inst_ark)
            coll.institutions.add(inst)
            coll.save()
            old2new_collection_institution[combine_id] = str(coll.pk) + ':' + str(inst.pk)
        else:
            pass
    save_id_mapping(shelf, 'collection_institution', old2new_collection_institution)


    old2new_collection_submission = get_id_mapping(shelf, 'collection_submission')
    rows = read_repodata('collection_submissions')
    for row in rows:
        coll_row = read_repodata('collections',' WHERE ID = %s' % row[1])
        coll_ark = coll_row[0][1]
        user_row = read_repodata('institution_employees', 'WHERE ID = %s' %
                                 row[2])
        user_login = user_row[0][1]
        combine_id = coll_ark + ':' + user_login
        if not is_update(old2new_collection_submission, combine_id):
            coll = Collection.objects.get(ark=coll_ark)
            user = Institution.objects.get(username=user_login)
            collsub = CollectionSubmission(collection=coll, user=user,
                                           status=row[3])
            collsub.save()
            old2new_collection_submission[combine_id] = collsub.pk
        else:
            pass
    save_id_mapping(shelf, 'collection_submission', old2new_collection_submission)

    old2new_location = get_id_mapping(shelf, 'location')
    rows = read_repodata('locations')
    for row in rows:
        if not is_update(old2new_location, row[1]):
            loc = Location(mai_code_location=row[1], location_type=row[2],
                           region=row[3], suppress=row[4], campus=row[5],
                           cmp=row[6], primary_name=row[7], campus_name=row[8],
                           prefix=row[9], notes=row[10])
            loc.save()
            old2new_location[row[1]] = loc.pk
            logging.info("+++NEW+++ location:%s" % loc.mai_code_location)
        else:
            logging.warning("location to update:%s" % row[1])
    save_id_mapping(shelf, 'location', old2new_location)

    old2new_location_institution = get_id_mapping(shelf, 'location_institution')
    rows = read_repodata('institutions_locations')
    for row in rows:
        loc_row = read_repodata('locations', 'WHERE ID = %s' % row[2])
        loc_mai_code = loc_row[0][1]
        inst_row = read_repodata('institutions', ' WHERE ID = %s' % row[2])
        inst_ark = inst_row[0][1]
        combine_id = loc_mai_code + ':' + inst_ark
        if not is_update(old2new_location_institution, combine_id):
            loc = Location.objects.get(mai_code_location=loc_mai_code)
            inst = Institution.objects.get(ark=inst_ark)
            loc.institutions.add(inst)
            loc.save()
            old2new_location_institution[combine_id] = loc.pk
        else:
            pass
    save_id_mapping(shelf, 'location_institution', old2new_location_institution)


    load_user_passwords(repopass_file)

    shelf.close()
