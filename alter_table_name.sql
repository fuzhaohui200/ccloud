alter table aix_aix_manage_ip rename to aix_aix_manage_ip_10;
alter table aix_aix_service_ip rename to aix_aix_service_ip_10;
alter table aix_hdisk rename to aix_hdisk_10;
alter table aix_vioclient rename to aix_vioclient_10;
alter table aix_aix_resource_lock rename to aix_aix_resource_lock_10;
alter table aix_aix_server add column "alias" varchar(50);