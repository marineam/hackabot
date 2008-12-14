-- MySQL dump 10.11
--
-- Host: billybob    Database: manatee
-- ------------------------------------------------------
-- Server version	5.0.70

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

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `bar_adj` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `adj_name` (`name`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `bar_location`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `bar_location` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  `lastused` int(11) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `location_name` (`name`),
  KEY `lastused` (`lastused`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `bar_noun`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `bar_noun` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `n_name` (`name`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `blame`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `blame` (
  `id` int(10) NOT NULL auto_increment,
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  KEY `lastused` (`lastused`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `brain_chains`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `brain_chains` (
  `key_1` varchar(20) NOT NULL,
  `sep_1` varchar(5) NOT NULL,
  `key_2` varchar(20) NOT NULL,
  `sep_2` varchar(5) NOT NULL,
  `key_3` varchar(20) NOT NULL,
  `sep_3` varchar(5) NOT NULL,
  `key_4` varchar(20) NOT NULL,
  `sep_4` varchar(5) NOT NULL,
  `key_5` varchar(20) NOT NULL,
  `weight` int(11) NOT NULL default '1',
  `date` datetime NOT NULL,
  UNIQUE KEY `all` (`key_1`,`key_2`,`key_3`,`key_4`,`key_5`),
  KEY `keyword` (`key_1`),
  KEY `next` (`key_1`,`key_2`,`key_3`,`key_4`),
  KEY `prev` (`key_2`,`key_3`,`key_4`,`key_5`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `brain_keywords`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `brain_keywords` (
  `word` varchar(20) NOT NULL,
  `weight` int(11) NOT NULL default '1',
  `date` datetime NOT NULL,
  PRIMARY KEY  (`word`),
  KEY `weight` (`weight`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `fire`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `fire` (
  `name` varchar(50) NOT NULL default '',
  `value` int(10) NOT NULL default '0',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `group`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `group` (
  `name` varchar(50) NOT NULL default '',
  `names` varchar(200) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `hangman`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `hangman` (
  `chan` varchar(20) NOT NULL default '',
  `final` enum('win','lose') default NULL,
  `phrase` varchar(100) NOT NULL,
  `guess` varchar(100) NOT NULL,
  `wrong` varchar(30) NOT NULL,
  PRIMARY KEY  (`chan`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `log`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `log` (
  `id` int(10) NOT NULL auto_increment,
  `sent_by` varchar(50) default NULL,
  `sent_to` varchar(50) default NULL,
  `channel` varchar(50) default NULL,
  `text` text,
  `count` int(11) default NULL,
  `type` enum('msg','action','notice','join','part','quit','stats','topic','kick','rename') NOT NULL default 'msg',
  `date` datetime NOT NULL,
  PRIMARY KEY  (`id`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `lunch_adj`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `lunch_adj` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `adj_name` (`name`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `lunch_location`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `lunch_location` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  `lastused` int(11) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `location_name` (`name`),
  KEY `lastused` (`lastused`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `lunch_noun`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `lunch_noun` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `n_name` (`name`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `metadata`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `metadata` (
  `name` varchar(20) NOT NULL,
  `value` varchar(20) NOT NULL,
  PRIMARY KEY  (`name`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `quotes`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `quotes` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `quote` varchar(255) NOT NULL default '',
  `nick` varchar(20) NOT NULL default '',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `reminder`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `reminder` (
  `id` int(10) NOT NULL auto_increment,
  `time` varchar(20) NOT NULL default '',
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `created` varchar(20) default NULL,
  PRIMARY KEY  (`id`),
  KEY `time` (`time`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `score`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `score` (
  `name` varchar(50) NOT NULL default '',
  `value` int(10) NOT NULL default '0',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `tard`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `tard` (
  `name` varchar(50) NOT NULL default '',
  `tard` tinyint(1) NOT NULL default '0',
  `value` int(10) NOT NULL default '0',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  PRIMARY KEY  (`name`)
) DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `topic`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `topic` (
  `id` int(10) NOT NULL auto_increment,
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  KEY `lastused` (`lastused`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `whip`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `whip` (
  `id` int(10) NOT NULL auto_increment,
  `text` varchar(255) NOT NULL default '',
  `nick` varchar(20) default NULL,
  `chan` varchar(20) default NULL,
  `date` varchar(20) default NULL,
  `lastused` int(10) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  KEY `lastused` (`lastused`)
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `wtf`
--

SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
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
)  DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-12-14 19:43:50
