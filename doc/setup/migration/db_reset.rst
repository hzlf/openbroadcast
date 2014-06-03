./manage.py cleanup


remove unneeded entries
=======================

# TRUNCATE TABLE `invite_invite`;



in python shell:
================

Release.objects.all().delete()
Artist.objects.all().delete()
Media.objects.all().delete()
Label.objects.all().delete()
Playlist.objects.all().delete()
Agency.objects.all().delete()

AgencyScope.objects.all().delete()
APILookup.objects.all().delete()
Distributor.objects.all().delete()
NameVariation.objects.all().delete()
PlaylistItem.objects.all().delete()
Series.objects.all().delete()

# arating
Vote.objects.all().delete()

# atracker
Event.objects.all().delete()

# bcmon
Playout.objects.all().delete()

# bcmon
Comment.objects.all().delete()

# exporter
Export.objects.all().delete()

# filer
File.objects.all().delete()
Folder.objects.all().delete()
Image.objects.all().delete()

# importer
Import.objects.all().delete()
ImportFile.objects.all().delete()

# tags
Tag.objects.all().delete()




# user & profiles
Invitation.objects.all().delete()
User.objects.exclude(username='root').delete()
Community.objects.all().delete()











thumbnails
==========

TRUNCATE TABLE `easy_thumbnails_thumbnail`;
TRUNCATE TABLE `easy_thumbnails_source`;




reload fixtures
===============

./manage.py loaddata apps/abcast/fixtures/abcast.json
./manage.py loaddata apps/alibrary/fixtures/abcast.json






abcast
======


SET foreign_key_checks = 0;
ALTER TABLE `abcast_daypart_weekdays` DROP FOREIGN KEY `daypart_id_refs_id_2f1332c`;
DROP TABLE `abcast_daypart`;
DROP TABLE `abcast_daypart_weekdays`;
DROP TABLE `abcast_weekday`;
DROP TABLE `abcast_daypartset`;
DROP TABLE `abcast_emission`;
DROP TABLE `abcast_broadcast`;
DROP TABLE `abcast_jingle`;
DROP TABLE `abcast_jingleset`;
DROP TABLE `cmsplugin_onairplugin`;
ALTER TABLE `abcast_streamserver_formats` DROP FOREIGN KEY `streamformat_id_refs_id_7cd2fecc`;
DROP TABLE `abcast_streamformat`;
ALTER TABLE `abcast_streamserver_formats` DROP FOREIGN KEY `streamserver_id_refs_id_e5934864`;
ALTER TABLE `abcast_channel` DROP FOREIGN KEY `stream_server_id_refs_id_706aadce`;
DROP TABLE `abcast_streamserver`;
DROP TABLE `abcast_streamserver_formats`;
DROP TABLE `abcast_channel`;
DROP TABLE `abcast_onairitem`;
ALTER TABLE `abcast_stationmembers_roles` DROP FOREIGN KEY `stationmembers_id_refs_id_f20ee0a3`;
DROP TABLE `abcast_stationmembers`;
DROP TABLE `abcast_stationmembers_roles`;
DROP TABLE `abcast_role`;
DROP TABLE `abcast_station`;
SET foreign_key_checks = 1;


BEGIN;
CREATE TABLE `abcast_station` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(256),
    `teaser` varchar(512),
    `slug` varchar(50) NOT NULL,
    `type` varchar(12) NOT NULL,
    `main_image_id` integer,
    `description` longtext,
    `website` varchar(256),
    `phone` varchar(128),
    `fax` varchar(128),
    `address1` varchar(100),
    `address2` varchar(100),
    `city` varchar(100),
    `zip` varchar(10),
    `country_id` integer,
    `description_html` longtext
)
;
ALTER TABLE `abcast_station` ADD CONSTRAINT `country_id_refs_id_32701dc4` FOREIGN KEY (`country_id`) REFERENCES `l10n_country` (`id`);
ALTER TABLE `abcast_station` ADD CONSTRAINT `main_image_id_refs_file_ptr_id_1090bc53` FOREIGN KEY (`main_image_id`) REFERENCES `filer_image` (`file_ptr_id`);
CREATE TABLE `abcast_role` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(200) NOT NULL
)
;
CREATE TABLE `abcast_stationmembers_roles` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `stationmembers_id` integer NOT NULL,
    `role_id` integer NOT NULL,
    UNIQUE (`stationmembers_id`, `role_id`)
)
;
ALTER TABLE `abcast_stationmembers_roles` ADD CONSTRAINT `role_id_refs_id_f79a30ec` FOREIGN KEY (`role_id`) REFERENCES `abcast_role` (`id`);
CREATE TABLE `abcast_stationmembers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `station_id` integer NOT NULL
)
;
ALTER TABLE `abcast_stationmembers` ADD CONSTRAINT `user_id_refs_id_b175af15` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `abcast_stationmembers` ADD CONSTRAINT `station_id_refs_id_a07ec435` FOREIGN KEY (`station_id`) REFERENCES `abcast_station` (`id`);
ALTER TABLE `abcast_stationmembers_roles` ADD CONSTRAINT `stationmembers_id_refs_id_f20ee0a3` FOREIGN KEY (`stationmembers_id`) REFERENCES `abcast_stationmembers` (`id`);
CREATE TABLE `abcast_onairitem` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `content_type_id` integer NOT NULL,
    `object_id` integer UNSIGNED NOT NULL,
    UNIQUE (`content_type_id`, `object_id`)
)
;
ALTER TABLE `abcast_onairitem` ADD CONSTRAINT `content_type_id_refs_id_ba0f7005` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
CREATE TABLE `abcast_channel` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(256),
    `teaser` varchar(512),
    `slug` varchar(50) NOT NULL,
    `type` varchar(12) NOT NULL,
    `stream_url` varchar(256),
    `description` longtext,
    `station_id` integer,
    `rtmp_app` varchar(256),
    `rtmp_path` varchar(256),
    `has_scheduler` bool NOT NULL,
    `stream_server_id` integer,
    `mount` varchar(64),
    `on_air_type_id` integer,
    `on_air_id` integer UNSIGNED,
    `description_html` longtext,
    UNIQUE (`on_air_type_id`, `on_air_id`)
)
;
ALTER TABLE `abcast_channel` ADD CONSTRAINT `on_air_type_id_refs_id_386aeefa` FOREIGN KEY (`on_air_type_id`) REFERENCES `django_content_type` (`id`);
ALTER TABLE `abcast_channel` ADD CONSTRAINT `station_id_refs_id_89b3cd40` FOREIGN KEY (`station_id`) REFERENCES `abcast_station` (`id`);
CREATE TABLE `abcast_streamserver_formats` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `streamserver_id` integer NOT NULL,
    `streamformat_id` integer NOT NULL,
    UNIQUE (`streamserver_id`, `streamformat_id`)
)
;
CREATE TABLE `abcast_streamserver` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(256),
    `host` varchar(256),
    `source_pass` varchar(64),
    `admin_pass` varchar(64),
    `active` bool NOT NULL,
    `type` varchar(12) NOT NULL
)
;
ALTER TABLE `abcast_channel` ADD CONSTRAINT `stream_server_id_refs_id_706aadce` FOREIGN KEY (`stream_server_id`) REFERENCES `abcast_streamserver` (`id`);
ALTER TABLE `abcast_streamserver_formats` ADD CONSTRAINT `streamserver_id_refs_id_e5934864` FOREIGN KEY (`streamserver_id`) REFERENCES `abcast_streamserver` (`id`);
CREATE TABLE `abcast_streamformat` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `type` varchar(12) NOT NULL,
    `bitrate` integer UNSIGNED NOT NULL
)
;
ALTER TABLE `abcast_streamserver_formats` ADD CONSTRAINT `streamformat_id_refs_id_7cd2fecc` FOREIGN KEY (`streamformat_id`) REFERENCES `abcast_streamformat` (`id`);
CREATE TABLE `cmsplugin_onairplugin` (
    `cmsplugin_ptr_id` integer NOT NULL PRIMARY KEY,
    `channel_id` integer NOT NULL,
    `show_channel_info` bool NOT NULL
)
;
ALTER TABLE `cmsplugin_onairplugin` ADD CONSTRAINT `cmsplugin_ptr_id_refs_id_27951332` FOREIGN KEY (`cmsplugin_ptr_id`) REFERENCES `cms_cmsplugin` (`id`);
ALTER TABLE `cmsplugin_onairplugin` ADD CONSTRAINT `channel_id_refs_id_7f68f899` FOREIGN KEY (`channel_id`) REFERENCES `abcast_channel` (`id`);
CREATE TABLE `abcast_jingleset` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(200) NOT NULL,
    `slug` varchar(50) NOT NULL,
    `description` longtext,
    `main_image_id` integer,
    `station_id` integer
)
;
ALTER TABLE `abcast_jingleset` ADD CONSTRAINT `main_image_id_refs_file_ptr_id_8c3e72ec` FOREIGN KEY (`main_image_id`) REFERENCES `filer_image` (`file_ptr_id`);
ALTER TABLE `abcast_jingleset` ADD CONSTRAINT `station_id_refs_id_44f729c6` FOREIGN KEY (`station_id`) REFERENCES `abcast_station` (`id`);
CREATE TABLE `abcast_jingle` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(200) NOT NULL,
    `slug` varchar(50) NOT NULL,
    `processed` integer UNSIGNED NOT NULL,
    `conversion_status` integer UNSIGNED NOT NULL,
    `lock` integer UNSIGNED NOT NULL,
    `type` varchar(12) NOT NULL,
    `description` longtext,
    `duration` integer UNSIGNED,
    `user_id` integer,
    `artist_id` integer,
    `set_id` integer,
    `master` varchar(1024),
    `master_sha1` varchar(64),
    `folder` varchar(1024)
)
;
ALTER TABLE `abcast_jingle` ADD CONSTRAINT `user_id_refs_id_fe074f93` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `abcast_jingle` ADD CONSTRAINT `artist_id_refs_id_385d1055` FOREIGN KEY (`artist_id`) REFERENCES `alibrary_artist` (`id`);
ALTER TABLE `abcast_jingle` ADD CONSTRAINT `set_id_refs_id_62915d3e` FOREIGN KEY (`set_id`) REFERENCES `abcast_jingleset` (`id`);
CREATE TABLE `abcast_broadcast` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(200) NOT NULL,
    `slug` varchar(50) NOT NULL,
    `status` integer UNSIGNED NOT NULL,
    `type` varchar(12) NOT NULL,
    `description` longtext,
    `duration` integer UNSIGNED,
    `user_id` integer,
    `playlist_id` integer
)
;
ALTER TABLE `abcast_broadcast` ADD CONSTRAINT `user_id_refs_id_8dac8d80` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `abcast_broadcast` ADD CONSTRAINT `playlist_id_refs_id_7f420171` FOREIGN KEY (`playlist_id`) REFERENCES `alibrary_playlist` (`id`);
CREATE TABLE `abcast_emission` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `name` varchar(200) NOT NULL,
    `slug` varchar(50) NOT NULL,
    `status` integer UNSIGNED NOT NULL,
    `color` integer UNSIGNED NOT NULL,
    `type` varchar(12) NOT NULL,
    `source` varchar(12) NOT NULL,
    `time_start` datetime,
    `time_end` datetime,
    `duration` integer UNSIGNED,
    `user_id` integer,
    `channel_id` integer,
    `content_type_id` integer NOT NULL,
    `object_id` integer UNSIGNED NOT NULL,
    `locked` bool NOT NULL
)
;
ALTER TABLE `abcast_emission` ADD CONSTRAINT `channel_id_refs_id_b268d4ac` FOREIGN KEY (`channel_id`) REFERENCES `abcast_channel` (`id`);
ALTER TABLE `abcast_emission` ADD CONSTRAINT `user_id_refs_id_10eb7773` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `abcast_emission` ADD CONSTRAINT `content_type_id_refs_id_d3460029` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
CREATE TABLE `abcast_daypartset` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `channel_id` integer,
    `time_start` date,
    `time_end` date
)
;
ALTER TABLE `abcast_daypartset` ADD CONSTRAINT `channel_id_refs_id_74a143dc` FOREIGN KEY (`channel_id`) REFERENCES `abcast_channel` (`id`);
CREATE TABLE `abcast_weekday` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `day` integer UNSIGNED NOT NULL
)
;
CREATE TABLE `abcast_daypart_weekdays` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `daypart_id` integer NOT NULL,
    `weekday_id` integer NOT NULL,
    UNIQUE (`daypart_id`, `weekday_id`)
)
;
ALTER TABLE `abcast_daypart_weekdays` ADD CONSTRAINT `weekday_id_refs_id_a080b6bf` FOREIGN KEY (`weekday_id`) REFERENCES `abcast_weekday` (`id`);
CREATE TABLE `abcast_daypart` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `uuid` varchar(36) NOT NULL,
    `created` datetime NOT NULL,
    `updated` datetime NOT NULL,
    `daypartset_id` integer,
    `time_start` time NOT NULL,
    `time_end` time NOT NULL,
    `name` varchar(128),
    `description` longtext,
    `mood` longtext,
    `sound` longtext,
    `talk` longtext
)
;
ALTER TABLE `abcast_daypart` ADD CONSTRAINT `daypartset_id_refs_id_cce4513e` FOREIGN KEY (`daypartset_id`) REFERENCES `abcast_daypartset` (`id`);
ALTER TABLE `abcast_daypart_weekdays` ADD CONSTRAINT `daypart_id_refs_id_2f1332c` FOREIGN KEY (`daypart_id`) REFERENCES `abcast_daypart` (`id`);
CREATE INDEX `abcast_station_a951d5d6` ON `abcast_station` (`slug`);
CREATE INDEX `abcast_station_c38d606b` ON `abcast_station` (`main_image_id`);
CREATE INDEX `abcast_station_534dd89` ON `abcast_station` (`country_id`);
CREATE INDEX `abcast_stationmembers_fbfc09f1` ON `abcast_stationmembers` (`user_id`);
CREATE INDEX `abcast_stationmembers_15e3331d` ON `abcast_stationmembers` (`station_id`);
CREATE INDEX `abcast_onairitem_e4470c6e` ON `abcast_onairitem` (`content_type_id`);
CREATE INDEX `abcast_channel_a951d5d6` ON `abcast_channel` (`slug`);
CREATE INDEX `abcast_channel_15e3331d` ON `abcast_channel` (`station_id`);
CREATE INDEX `abcast_channel_567e3955` ON `abcast_channel` (`stream_server_id`);
CREATE INDEX `abcast_channel_cef0a72a` ON `abcast_channel` (`on_air_type_id`);
CREATE INDEX `cmsplugin_onairplugin_f9972756` ON `cmsplugin_onairplugin` (`channel_id`);
CREATE INDEX `abcast_jingleset_52094d6e` ON `abcast_jingleset` (`name`);
CREATE INDEX `abcast_jingleset_a951d5d6` ON `abcast_jingleset` (`slug`);
CREATE INDEX `abcast_jingleset_c38d606b` ON `abcast_jingleset` (`main_image_id`);
CREATE INDEX `abcast_jingleset_15e3331d` ON `abcast_jingleset` (`station_id`);
CREATE INDEX `abcast_jingle_52094d6e` ON `abcast_jingle` (`name`);
CREATE INDEX `abcast_jingle_a951d5d6` ON `abcast_jingle` (`slug`);
CREATE INDEX `abcast_jingle_fbfc09f1` ON `abcast_jingle` (`user_id`);
CREATE INDEX `abcast_jingle_e995513f` ON `abcast_jingle` (`artist_id`);
CREATE INDEX `abcast_jingle_c6e0480d` ON `abcast_jingle` (`set_id`);
CREATE INDEX `abcast_jingle_e46ae04e` ON `abcast_jingle` (`master_sha1`);
CREATE INDEX `abcast_broadcast_52094d6e` ON `abcast_broadcast` (`name`);
CREATE INDEX `abcast_broadcast_a951d5d6` ON `abcast_broadcast` (`slug`);
CREATE INDEX `abcast_broadcast_fbfc09f1` ON `abcast_broadcast` (`user_id`);
CREATE INDEX `abcast_broadcast_448b1ea` ON `abcast_broadcast` (`playlist_id`);
CREATE INDEX `abcast_emission_52094d6e` ON `abcast_emission` (`name`);
CREATE INDEX `abcast_emission_a951d5d6` ON `abcast_emission` (`slug`);
CREATE INDEX `abcast_emission_fbfc09f1` ON `abcast_emission` (`user_id`);
CREATE INDEX `abcast_emission_f9972756` ON `abcast_emission` (`channel_id`);
CREATE INDEX `abcast_emission_e4470c6e` ON `abcast_emission` (`content_type_id`);
CREATE INDEX `abcast_daypartset_f9972756` ON `abcast_daypartset` (`channel_id`);
CREATE INDEX `abcast_daypart_80cdaa5` ON `abcast_daypart` (`daypartset_id`);
COMMIT;