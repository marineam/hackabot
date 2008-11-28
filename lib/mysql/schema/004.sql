TRUNCATE TABLE `hangman`;
ALTER TABLE `hangman`
  DROP `state`,
  DROP `nick`,
  CHANGE `phrase` `phrase` VARCHAR( 100 )
  CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
  CHANGE `guess` `guess` VARCHAR( 100 )
  CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
  CHANGE `wrong` `wrong` VARCHAR( 30 )
  CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
