CREATE DATABASE ds_project1;
USE ds_project1;
CREATE TABLE `users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `email` varchar(255),
  `phone` varchar(255),
  `password` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `property` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `description` varchar(255),
  `price` bigint,
  `location` bigint,
  `add_info` bigint,
  `created_by` bigint,
  `created_at` timestamp
);

CREATE TABLE `cities` (
  `id` int PRIMARY KEY,
  `name` varchar(255)
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
  `user_id` bigint,
  `city_id` bigint
);