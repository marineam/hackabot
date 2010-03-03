CREATE TABLE `ass` (
    `name` varchar(50) NOT NULL default '',
    `ass` tinyint(1) NOT NULL default '0',
    `value` int(10) NOT NULL default '0',
    `nick` varchar(20) default NULL,
    `chan` varchar(20) default NULL,
    `date` varchar(20) default NULL,
    PRIMARY KEY  (`name`)
) DEFAULT CHARSET = utf8;
CREATE TABLE `fail` (
    `name` varchar(50) NOT NULL default '',
    `fail` tinyint(1) NOT NULL default '0',
    `value` int(10) NOT NULL default '0',
    `nick` varchar(20) default NULL,
    `chan` varchar(20) default NULL,
    `date` varchar(20) default NULL,
    PRIMARY KEY  (`name`)
) DEFAULT CHARSET = utf8;
CREATE TABLE `fob` (
    `name` varchar(50) NOT NULL default '',
    `fob` tinyint(1) NOT NULL default '0',
    `value` int(10) NOT NULL default '0',
    `nick` varchar(20) default NULL,
    `chan` varchar(20) default NULL,
    `date` varchar(20) default NULL,
    PRIMARY KEY  (`name`)
) DEFAULT CHARSET=utf8;
DROP TABLE `quotes`;
CREATE TABLE `quote` (
    `id` int(10) NOT NULL auto_increment,
    `text` varchar(255) NOT NULL default '',
    `nick` varchar(20) default NULL,
    `chan` varchar(20) default NULL,
    `date` varchar(20) default NULL,
    `lastused` int(10) NOT NULL default '1',
    PRIMARY KEY  (`id`),
    KEY `lastused` (`lastused`)
) DEFAULT CHARSET = utf8;
CREATE TABLE `win` (
    `name` varchar(50) NOT NULL default '',
    `win` tinyint(1) NOT NULL default '0',
    `value` int(10) NOT NULL default '0',
    `nick` varchar(20) default NULL,
    `chan` varchar(20) default NULL,
    `date` varchar(20) default NULL,
    PRIMARY KEY  (`name`)
) DEFAULT CHARSET=utf8;
