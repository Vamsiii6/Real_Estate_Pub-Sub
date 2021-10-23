CREATE DATABASE ds_project1;
USE ds_project1;
CREATE TABLE `users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `email` varchar(255),
  `phone` varchar(255),
  `roles` varchar(255),
  `uid` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `properties` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `description` varchar(255),
  `price` bigint,
  `city_id` bigint,
  `room_type_id` bigint,
  `add_info` bigint,
  `created_by_uid` varchar(255),
  `created_by_name` varchar(255),
  `created_at` timestamp,
  `image_url` varchar(1000),
  `listing_id` varchar(255)
);

CREATE TABLE `cities` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255)
);
INSERT INTO `cities` (`name`) VALUES ('Buffalo');
INSERT INTO `cities` (`name`) VALUES ('Syracuse');
INSERT INTO `cities` (`name`) VALUES ('Albany');
INSERT INTO `cities` (`name`) VALUES ('NYC');

CREATE TABLE `room_type` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `type` varchar(255)
);

INSERT INTO `room_type` (`type`) VALUES ('1 BHK');
INSERT INTO `room_type` (`type`) VALUES ('2 BHK');
INSERT INTO `room_type` (`type`) VALUES ('3 BHK');
INSERT INTO `room_type` (`type`) VALUES ('4 BHK');
INSERT INTO `room_type` (`type`) VALUES ('5 BHK');
INSERT INTO `room_type` (`type`) VALUES ('6 BHK');

CREATE TABLE `user_cities_rel` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `uid` varchar(255),
  `city_id` bigint
);

CREATE TABLE `user_room_types_rel` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `uid` varchar(255),
  `room_type_id` bigint
);