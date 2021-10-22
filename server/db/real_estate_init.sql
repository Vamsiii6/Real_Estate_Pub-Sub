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
  `created_by` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `cities` (
  `id` int PRIMARY KEY,
  `name` varchar(255)
);

CREATE TABLE `room_type` (
  `id` int PRIMARY KEY,
  `type` varchar(255)
);

CREATE TABLE `location` (
  `id` int PRIMARY KEY,
  `address_line1` varchar(255),
  `address_line2` varchar(255),
  `city` bigint,
  `state` varchar(255),
  `zip_code` varchar(255),
  `created_at` varchar(255)
);

CREATE TABLE `user_cities_rel` (
  `uid` bigint,
  `city_id` bigint
);

CREATE TABLE `user_room_types_rel` (
  `uid` bigint,
  `room_type_id` bigint
);