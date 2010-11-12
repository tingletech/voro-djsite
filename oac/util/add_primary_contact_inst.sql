alter table oac_institution add column primary_contact_id int(11) default NULL;                                                             
alter table oac_institution add key oac_institution_primary_contact_id (primary_contact_id);

alter table oac_institution add column marc_ltr_recipient_id int(11) default NULL;

alter table oac_institution add key oac_institution_marc_ltr_recipient_id (marc_ltr_recipient_id);

