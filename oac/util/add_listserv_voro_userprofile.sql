alter table oac_userprofile add column oac_listserv tinyint(1) not null default 1 after phone;
alter table oac_userprofile add column voroead_account tinyint(1) not null default 0 after oac_listserv;


