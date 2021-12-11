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

insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Admin', 'admin@rps.com', 'Admin', '6', 'VwioudRBkCZFvEyNXmNKK7qHZpy1');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Publisher 1', 'publisher1@rps.com', 'Publisher 1', '2', 'IOxyt7H2ytMouuekKiKELoykGKH2');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 1', 'subscriber1@rps.com', 'Subscriber 1', '4', 'XJxTONpve7hwXPz90pmMq7HAEFz1');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 2', 'subscriber2@rps.com', 'Subscriber 2', '4', 'IiagWPMXnQNFsPErdDzESv4Tr5p1');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 3', 'subscriber3@rps.com', 'Subscriber 3', '4', 'qovOHkTmOfTTaNGElnMLNYUpgmJ3');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 4', 'subscriber4@rps.com', 'Subscriber 4', '4', 'ybIClJEidkX8m2jnDwFTPDZbkd13');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 5', 'subscriber5@rps.com', 'Subscriber 5', '4', 'dpgTThbmcPYyDvlTYzxXw1b6qfn1');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 6', 'subscriber6@rps.com', 'Subscriber 6', '4', '2usQuLfuyXTN7G5CD8g2mBergFz1');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 7', 'subscriber7@rps.com', 'Subscriber 7', '4', 'EJLENx1mLdYL6D57PuAa9uwxuZO2');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 8', 'subscriber8@rps.com', 'Subscriber 8', '4', 'JXGbmHXn7PVMchr6lKQzCm9yhps2');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 9', 'subscriber9@rps.com', 'Subscriber 9', '4', 'zG9hFb7oeeZ0jFaVZY979LlFU9X2');
insert into `users` (`name`, `email`, `phone`, `roles`, `uid`) VALUES ('Subscriber 10', 'subscriber10@rps.com', 'Subscriber 10', '4', 'GgoI3wGruveZxfjB7nkbQHjwJyG2');


CREATE TABLE `properties` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255),
  `description` varchar(255),
  `price` bigint,
  `city_id` bigint,
  `room_type_id` bigint,
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

CREATE TABLE `adv_cities_rel` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `uid` varchar(255),
  `city_id` bigint
);

CREATE TABLE `adv_room_types_rel` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `uid` varchar(255),
  `room_type_id` bigint
);

CREATE TABLE `broker_vs_topics` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `broker_port` varchar(255),
  `topic_id` bigint
);

INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5005','1');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5005','2');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5005','3');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5006','4');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5006','5');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5006','6');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5007','7');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5007','8');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5007','9');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5008','1');
INSERT INTO `broker_vs_topics` (`broker_port`,`topic_id`) VALUES ( '5008','4');