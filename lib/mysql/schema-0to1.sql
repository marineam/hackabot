CREATE TABLE `hackabot`.`metadata` (
	`name` VARCHAR( 20 ) NOT NULL ,
	`value` VARCHAR( 20 ) NOT NULL ,
	PRIMARY KEY ( `name` )
);
INSERT INTO `hackabot`.`metadata` (`name` , `value`) VALUES ('schema', '1');
