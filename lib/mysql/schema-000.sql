-- MySQL dump 10.11
--
-- Host: db2.osuosl.org    Database: manatee_data
-- ------------------------------------------------------
-- Server version	5.0.46-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bar_adj`
--

CREATE TABLE `bar_adj` (
  `adj_id` int(10) unsigned NOT NULL auto_increment,
  `adj_name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`adj_id`),
  UNIQUE KEY `adj_name` (`adj_name`)
);

--
-- Table structure for table `bar_location`
--

CREATE TABLE `bar_location` (
  `location_id` int(10) unsigned NOT NULL auto_increment,
  `location_name` varchar(255) NOT NULL default '',
  `lastused` int(11) NOT NULL default '1',
  PRIMARY KEY  (`location_id`),
  UNIQUE KEY `location_name` (`location_name`),
  KEY `lastused` (`lastused`)
);

--
-- Table structure for table `bar_n`
--

CREATE TABLE `bar_n` (
  `n_id` int(10) unsigned NOT NULL auto_increment,
  `n_name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`n_id`),
  UNIQUE KEY `n_name` (`n_name`)
);

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
);

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
);

--
-- Table structure for table `group`
--

CREATE TABLE `group` (
  `name` varchar(50) NOT NULL default '',
  `names` varchar(200) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
);

--
-- Table structure for table `hangman`
--

CREATE TABLE `hangman` (
  `chan` varchar(20) NOT NULL default '',
  `state` tinyint(4) NOT NULL default '0',
  `final` enum('win','lose') default NULL,
  `phrase` varchar(255) NOT NULL default '',
  `guess` varchar(255) NOT NULL default '',
  `wrong` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  PRIMARY KEY  (`chan`,`state`)
);

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `id` int(10) NOT NULL auto_increment,
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `text` text,
  `num` int(11) default NULL,
  `type` enum('msg','action','notice','join','part','quit','stats','topic') NOT NULL default 'msg',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`)
);

--
-- Table structure for table `lunch_adj`
--

CREATE TABLE `lunch_adj` (
  `adj_id` int(10) unsigned NOT NULL auto_increment,
  `adj_name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`adj_id`),
  UNIQUE KEY `adj_name` (`adj_name`)
);

--
-- Table structure for table `lunch_location`
--

CREATE TABLE `lunch_location` (
  `location_id` int(10) unsigned NOT NULL auto_increment,
  `location_name` varchar(255) NOT NULL default '',
  `lastused` int(11) NOT NULL default '1',
  PRIMARY KEY  (`location_id`),
  UNIQUE KEY `location_name` (`location_name`),
  KEY `lastused` (`lastused`)
);

--
-- Table structure for table `lunch_n`
--

CREATE TABLE `lunch_n` (
  `n_id` int(10) unsigned NOT NULL auto_increment,
  `n_name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`n_id`),
  UNIQUE KEY `n_name` (`n_name`)
);

--
-- Table structure for table `quotes`
--

CREATE TABLE `quotes` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `quote` varchar(255) NOT NULL default '',
  `nick` varchar(20) NOT NULL default '',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`)
);

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
);

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
);

--
-- Table structure for table `tard`
--

CREATE TABLE `tard` (
  `name` varchar(50) NOT NULL default '',
  `tard` tinyint(1) NOT NULL default '0',
  `value` int(10) NOT NULL default '0',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
);

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
);

--
-- Table structure for table `whip`
--

CREATE TABLE `whip` (
  `id` int(10) NOT NULL auto_increment,
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  KEY `lastused` (`lastused`)
);

--
-- Table structure for table `wtf`
--

CREATE TABLE `wtf` (
  `id` int(10) NOT NULL auto_increment,
  `acronym_i` varchar(50) NOT NULL default '',
  `acronym` varchar(50) NOT NULL default '',
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `acronym_i` (`acronym_i`),
  KEY `lastused` (`lastused`)
);
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-03-04  6:16:10
