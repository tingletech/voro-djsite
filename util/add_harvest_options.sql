alter table oac_institution add column worldcat_harvest tinyint(1) NULL after primary_contact_id;
alter table oac_institution add column archivegrid_harvest tinyint(1) NULL after worldcat_harvest;
alter table oac_institution add column show_subjects tinyint(1) NULL after archivegrid_harvest;
