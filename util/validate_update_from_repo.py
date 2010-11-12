import logging
import update_from_repodata_DB as updatePgm

from oac.models import *

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        filename='./validate_update_from_repodata.log',
                        filemode='w')
    logging.info('Start Reading from repodata')


    #confirm counts for tables:

    rows = updatePgm.read_repodata('counties')
    num = len(rows)
    print "Repo counties=%s ; oac_counties=%s" % (num, County.objects.count())

    rows = updatePgm.read_repodata('cities')
    num = len(rows)
    print "Repo cities=%s ; oac_cities=%s" % (num, City.objects.count())

    rows = updatePgm.read_repodata('institutions')
    num = len(rows)
    print "Repo insitutions=%s ; oac_insitutions=%s" % (num, Institution.objects.count())
    
    rows = updatePgm.read_repodata('edit_groups')
    num = len(rows)
    print "Repo edit_groups=%s ; oac_edit_groups=%s" % (num, Group.objects.count())
    
    rows = updatePgm.read_repodata('institution_employees')
    num = len(rows)
    print "Repo employees=%s ; oac_employees=%s ; userprof=%s" % (num,
                                                                  User.objects.count(),
                                                                 UserProfile.objects.count())

    
    rows = updatePgm.read_repodata('edit_groups_institution_employees')
    num = len(rows)
    #aggregate the maps from user to groups
    total_usergroup_maps = 0
    for user in User.objects.all():
        total_usergroup_maps += user.groups.count()

    print "Repo groupUserMapItems=%s ; oac_groupUserMapItems=%s" % (num,
                                                                    total_usergroup_maps)
    
    rows = updatePgm.read_repodata('collections')
    num = len(rows)
    print "Repo collections=%s ; oac_collections=%s" % (num, Collection.objects.count())
    
    rows = updatePgm.read_repodata('collections_institutions')
    num = len(rows)
    total_collinst_maps = 0
    for coll in Collection.objects.all():
        total_collinst_maps += coll.institutions.count()

    print "Repo coll_to_inst_map=%s ; oac_coll_to_inst_map=%s" % (num, total_collinst_maps)
    
    rows = updatePgm.read_repodata('collection_submissions')
    num = len(rows)
    print "Repo collection_submissions=%s ; oac_collection_submissions=%s" % (num, CollectionSubmission.objects.count())
    
    rows = updatePgm.read_repodata('locations')
    num = len(rows)
    print "Repo locations=%s ; oac_locations=%s" % (num, Location.objects.count())
    
    rows = updatePgm.read_repodata('institutions_locations')
    num = len(rows)
    total_locinst_maps = 0
    for loc in Location.objects.all():
        total_locinst_maps += loc.institutions.count()
    print "Repo inst_to_loc_map=%s ; oac_inst_to_loc_map=%s" % (num,
                                                                total_locinst_maps)
