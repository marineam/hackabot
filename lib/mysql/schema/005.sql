CREATE TABLE `brain_chains` (
    `key_1` varchar( 20 ) NOT NULL ,
    `sep_1` varchar( 5 ) NOT NULL ,
    `key_2` varchar( 20 ) NOT NULL ,
    `sep_2` varchar( 5 ) NOT NULL ,
    `key_3` varchar( 20 ) NOT NULL ,
    `sep_3` varchar( 5 ) NOT NULL ,
    `key_4` varchar( 20 ) NOT NULL ,
    `sep_4` varchar( 5 ) NOT NULL ,
    `key_5` varchar( 20 ) NOT NULL ,
    `weight` int( 11 ) NOT NULL default '1',
    `date` datetime NOT NULL ,
    UNIQUE KEY `all` ( `key_1` , `key_2` , `key_3` , `key_4` , `key_5` ) ,
    KEY `keyword` ( `key_1` ),
    KEY `next` ( `key_1` , `key_2` , `key_3` , `key_4` ) ,
    KEY `prev` ( `key_2` , `key_3` , `key_4` , `key_5` )
) DEFAULT CHARSET = utf8;
CREATE TABLE `brain_keywords` (
    `word` VARCHAR( 20 ) NOT NULL ,
    `weight` INT NOT NULL DEFAULT '1',
    `date` DATETIME NOT NULL ,
    PRIMARY KEY ( `word` ) ,
    KEY `weight` ( `weight` )
) DEFAULT CHARSET = utf8;
