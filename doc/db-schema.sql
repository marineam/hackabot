-- phpMyAdmin SQL Dump
-- version 2.7.0-pl2
-- http://www.phpmyadmin.net
-- 
-- Host: db0.osuosl.org
-- Generation Time: Mar 08, 2006 at 11:49 AM
-- Server version: 4.0.24
-- PHP Version: 4.3.10-16
-- 
-- Database: `manatee-data`
-- 

-- --------------------------------------------------------

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
  KEY `lastused` (`lastused`),
  KEY `lastused_2` (`lastused`)
) TYPE=MyISAM AUTO_INCREMENT=42 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `log`
-- 

CREATE TABLE `log` (
  `id` int(10) NOT NULL auto_increment,
  `nick` varchar(20) NOT NULL default '',
  `chan` varchar(20) default NULL,
  `text` varchar(255) NOT NULL default '',
  `type` enum('msg','action','notice') NOT NULL default 'msg',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM AUTO_INCREMENT=51788 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `quotes`
-- 

CREATE TABLE `quotes` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `quote` varchar(255) NOT NULL default '',
  `nick` varchar(20) NOT NULL default '',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

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
) TYPE=MyISAM AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

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

-- --------------------------------------------------------

-- 
-- Table structure for table `seen`
-- 

CREATE TABLE `seen` (
  `nick` varchar(20) NOT NULL default '',
  `quote_date` varchar(20) default NULL,
  `quote_chan` varchar(20) default NULL,
  `quote_txt` varchar(255) default NULL,
  `quote_id` int(10) default NULL,
  `quit_date` varchar(20) default NULL,
  `quit_txt` varchar(255) default NULL,
  PRIMARY KEY  (`nick`)
) TYPE=MyISAM;

-- --------------------------------------------------------

-- 
-- Table structure for table `seen_quotes`
-- 

CREATE TABLE `seen_quotes` (
  `id` int(10) NOT NULL auto_increment,
  `nick` varchar(20) NOT NULL default '',
  `chan` varchar(20) NOT NULL default '',
  `text` varchar(255) NOT NULL default '',
  `date` varchar(20) NOT NULL default '',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `INDEX` (`nick`,`chan`)
) TYPE=MyISAM AUTO_INCREMENT=520 ;

