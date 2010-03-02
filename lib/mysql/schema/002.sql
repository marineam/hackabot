ALTER TABLE `log`
CHANGE `nick` `sent_by` VARCHAR(50) CHARACTER SET utf8 NULL DEFAULT NULL ,
ADD `sent_to` VARCHAR(50) CHARACTER SET utf8 NULL DEFAULT NULL AFTER `sent_by`,
CHANGE `chan` `channel` VARCHAR(50) CHARACTER SET utf8 NULL DEFAULT NULL ,
CHANGE `num` `count` INT(11) NULL DEFAULT NULL ,
CHANGE `type` `type` ENUM( 'msg', 'action', 'notice', 'join', 'part',
    'quit', 'stats', 'topic', 'kick', 'rename' )
    CHARACTER SET utf8 NOT NULL DEFAULT 'msg',
CHANGE `date` `date` DATETIME NOT NULL;
