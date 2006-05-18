-- MySQL dump 9.11
--
-- Host: db0.osuosl.org    Database: manatee_data
-- ------------------------------------------------------
-- Server version	4.0.24_Debian-10sarge1-log

--
-- Table structure for table `blame`
--

CREATE TABLE `blame` (
  `id` int(10) NOT NULL auto_increment,
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  KEY `lastused` (`lastused`)
) TYPE=MyISAM;

--
-- Table structure for table `fire`
--

CREATE TABLE `fire` (
  `name` varchar(50) NOT NULL default '',
  `value` int(10) NOT NULL default '0',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
) TYPE=MyISAM;

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `id` int(10) NOT NULL auto_increment,
  `nick` varchar(20) NOT NULL default '',
  `chan` varchar(20) default NULL,
  `text` varchar(255) default NULL,
  `type` enum('msg','action','notice','join','part','quit') NOT NULL default 'msg',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Table structure for table `quotes`
--

CREATE TABLE `quotes` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `quote` varchar(255) NOT NULL default '',
  `nick` varchar(20) NOT NULL default '',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM;

--
-- Table structure for table `reminder`
--

CREATE TABLE `reminder` (
  `id` int(10) NOT NULL auto_increment,
  `time` varchar(20) NOT NULL default '',
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `created` varchar(20) default NULL,
  PRIMARY KEY  (`id`),
  KEY `time` (`time`)
) TYPE=MyISAM;

--
-- Table structure for table `score`
--

CREATE TABLE `score` (
  `name` varchar(50) NOT NULL default '',
  `value` int(10) NOT NULL default '0',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
) TYPE=MyISAM;

--
-- Table structure for table `topic`
--

CREATE TABLE `topic` (
  `id` int(10) NOT NULL auto_increment,
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  KEY `lastused` (`lastused`)
) TYPE=MyISAM;

--
-- Table structure for table `wtf`
--

CREATE TABLE `wtf` (
  `id` int(10) NOT NULL auto_increment,
  `acronym_i` varchar(20) NOT NULL default '',
  `acronym` varchar(20) NOT NULL default '',
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `acronym_i` (`acronym_i`),
  KEY `lastused` (`lastused`)
) TYPE=MyISAM;

