CREATE TABLE `metadata` (
	`name` VARCHAR( 20 ) NOT NULL ,
	`value` VARCHAR( 20 ) NOT NULL ,
	PRIMARY KEY ( `name` )
);
INSERT INTO `metadata` (`name` , `value`) VALUES ('schema', '1');
