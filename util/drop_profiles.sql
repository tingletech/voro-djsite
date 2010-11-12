create table oac_gpTemp select * from oac_groupprofile;
create table oac_upTemp select * from oac_userprofile;

drop table oac_groupprofile;
drop table oac_userprofile;
