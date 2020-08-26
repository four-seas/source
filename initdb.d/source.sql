CREATE TABLE `four_seas`.`houses` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `master_id` bigint(11) NOT NULL COMMENT '数据在主体网站的标识id',
  `title` varchar(255) NOT NULL DEFAULT '' COMMENT '标题',
  `total_price` decimal(10,2) NOT NULL COMMENT '挂牌总价',
  `total_area` decimal(8,2) NOT NULL COMMENT '建筑面积（平方米）',
  `unit_price_value` decimal(10,2) NOT NULL COMMENT '挂牌单价/平方米',
  `community_name` varchar(100) NOT NULL DEFAULT '' COMMENT '小区名',
  `area` varchar(50) NOT NULL DEFAULT '' COMMENT '区域，例如（海珠区）',
  `addr` varchar(255) NOT NULL DEFAULT '' COMMENT '详细地址',
  `door_model` varchar(255) NOT NULL DEFAULT '' COMMENT '户型',
  `has_elevator` tinyint(4) NOT NULL COMMENT '是否有电梯。0=没有，1=有，2=不确定',
  `has_subway` tinyint(4) NOT NULL COMMENT '是否近地铁。0=没有，1=有，2=不确定',
  `toward` varchar(20) NOT NULL DEFAULT '' COMMENT '房屋朝向',
  `establish` int(11) NOT NULL COMMENT '建立年份',
  `spider_src_url` varchar(500) NOT NULL DEFAULT '' COMMENT '数据原始url',
  `spider_type` tinyint(4) NOT NULL COMMENT '数据来源。1=贝壳，2=安居客',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `updated_at` (`updated_at`),
  KEY `uniq_idx` (`master_id`,`spider_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='爬虫数据表';

CREATE TABLE `four_seas`.`images` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `house_id` int(11) NOT NULL,
  `path` varchar(255) NOT NULL DEFAULT '',
  `url` varchar(255) NOT NULL DEFAULT '',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `house_id_idx` (`house_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='房子照片信息表';

