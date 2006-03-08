-- phpMyAdmin SQL Dump
-- version 2.7.0-pl2
-- http://www.phpmyadmin.net
-- 
-- Host: db0.osuosl.org
-- Generation Time: Mar 08, 2006 at 11:53 AM
-- Server version: 4.0.24
-- PHP Version: 4.3.10-16
-- 
-- Database: `manatee-lunch`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `lunch_adj`
-- 

CREATE TABLE `lunch_adj` (
  `adj_id` int(10) unsigned NOT NULL auto_increment,
  `adj_name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`adj_id`,`adj_name`)
) TYPE=MyISAM AUTO_INCREMENT=14 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `lunch_bar`
-- 

CREATE TABLE `lunch_bar` (
  `bar_id` int(10) unsigned NOT NULL auto_increment,
  `bar_name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`bar_id`,`bar_name`)
) TYPE=MyISAM AUTO_INCREMENT=3 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `lunch_location`
-- 

CREATE TABLE `lunch_location` (
  `location_id` int(10) unsigned NOT NULL auto_increment,
  `location_name` varchar(255) NOT NULL default '',
  `date_added` varchar(20) NOT NULL default '',
  `last_visit` varchar(20) NOT NULL default '',
  `visit_count` int(5) NOT NULL default '0',
  PRIMARY KEY  (`location_id`,`location_name`)
) TYPE=MyISAM AUTO_INCREMENT=23 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `lunch_n`
-- 

CREATE TABLE `lunch_n` (
  `n_id` int(10) unsigned NOT NULL auto_increment,
  `n_name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`n_id`,`n_name`)
) TYPE=MyISAM AUTO_INCREMENT=11 ;

