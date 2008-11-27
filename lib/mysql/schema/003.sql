ALTER TABLE `bar_adj`
 CHANGE `adj_id` `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
 CHANGE `adj_name` `name` VARCHAR( 100 )
 CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE `bar_n`
 RENAME TO `bar_noun` ,
 CHANGE `n_id` `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
 CHANGE `n_name` `name` VARCHAR( 100 )
 CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE `bar_location`
 CHANGE `location_id` `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
 CHANGE `location_name` `name` VARCHAR( 100 )
 CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE `lunch_adj`
 CHANGE `adj_id` `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
 CHANGE `adj_name` `name` VARCHAR( 100 )
 CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE `lunch_n`
 RENAME TO `lunch_noun` ,
 CHANGE `n_id` `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
 CHANGE `n_name` `name` VARCHAR( 100 )
 CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE `lunch_location`
 CHANGE `location_id` `id` INT UNSIGNED NOT NULL AUTO_INCREMENT ,
 CHANGE `location_name` `name` VARCHAR( 100 )
 CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
