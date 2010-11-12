alter table oac_userprofile add column archon_user varchar(32) NULL after voroead_account;
alter table oac_userprofile add column AT_application_user varchar(32) NULL after archon_user;
alter table oac_userprofile add column AT_database_user varchar(32) NULL after AT_application_user;
