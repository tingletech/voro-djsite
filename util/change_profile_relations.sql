insert into oac_groupprofile (id, group_id, directory, note, created_at, updated_at) select oac_gpTemp.id, oac_gpTemp.group_id, oac_gpTemp.directory, oac_gpTemp.note, oac_gpTemp.created_at, oac_gpTemp.updated_at from oac_gpTemp;

insert into oac_groupprofile_institutions (groupprofile_id, institution_id) select oac_gpTemp.id, oac_gpTemp.institution_id from oac_gpTemp;

insert into oac_userprofile (id, user_id, phone, created_at, updated_at) select oac_upTemp.id, oac_upTemp.user_id, oac_upTemp.phone, oac_upTemp.created_at, oac_upTemp.updated_at from oac_upTemp;

