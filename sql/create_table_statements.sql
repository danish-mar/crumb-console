-- First, create all tables without foreign keys
CREATE TABLE `users` (
                         `id` int NOT NULL AUTO_INCREMENT,
                         `first_name` varchar(50) NOT NULL,
                         `last_name` varchar(50) DEFAULT NULL,
                         `email` varchar(100) NOT NULL,
                         `phone` varchar(15) DEFAULT NULL,
                         `password` varchar(255) DEFAULT NULL,
                         `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                         `default_location` varchar(255) DEFAULT NULL,
                         `role` varchar(20) DEFAULT 'customer',
                         `status` varchar(20) DEFAULT 'active',
                         `cart_id` varchar(25) DEFAULT NULL,
                         `auth_provider` enum('google','manual') DEFAULT 'manual',
                         `profile_pic_url` varchar(255) DEFAULT 'none',
                         `address_lat` double DEFAULT NULL,
                         `address_lon` double DEFAULT NULL,
                         PRIMARY KEY (`id`),
                         UNIQUE KEY `email` (`email`),
                         KEY `cart_id` (`cart_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `product_category` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL UNIQUE,
    `description` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `products` (
                            `id` int NOT NULL AUTO_INCREMENT,
                            `name` varchar(255) NOT NULL,
                            `description` text,
                            `category` int DEFAULT NULL,
                            `price` decimal(10,2) NOT NULL,
                            `stock_quantity` int NOT NULL,
                            `weight` decimal(10,2) NOT NULL,
                            `image_url` varchar(255) DEFAULT NULL,
                            `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                            `is_available` tinyint(1) DEFAULT '1',
                            `is_featured` tinyint(1) DEFAULT '0' COMMENT 'checks if the products is on featured or not',
                            `is_popular` tinyint(1) DEFAULT '0' COMMENT 'is the product sells mostly',
                            `tags` text COMMENT 'tags of the product',
                            PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `payment_methods` (
                                   `id` int NOT NULL AUTO_INCREMENT,
                                   `method_name` varchar(50) NOT NULL,
                                   `details` text,
                                   `is_active` tinyint(1) DEFAULT '0',
                                   PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `orders` (
                          `id` int NOT NULL AUTO_INCREMENT,
                          `user_id` int DEFAULT NULL,
                          `payment_method` int DEFAULT NULL,
                          `order_place_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                          `expected_delivery_date` timestamp NULL DEFAULT NULL,
                          `actual_delivery_date` timestamp NULL DEFAULT NULL,
                          `is_completed` tinyint(1) DEFAULT '0',
                          `total` float DEFAULT NULL,
                          `shipping_address` varchar(255) DEFAULT NULL,
                          `status` varchar(20) DEFAULT 'pending',
                          `delivery_charges` decimal(10,2) DEFAULT '0.00',
                          PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `order_details` (
                                 `id` int NOT NULL AUTO_INCREMENT,
                                 `order_id` int DEFAULT NULL,
                                 `product_id` int DEFAULT NULL,
                                 `quantity` int NOT NULL,
                                 `price` float NOT NULL,
                                 `subtotal` float DEFAULT NULL,
                                 PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `featured_product` (
                                    `id` int NOT NULL,
                                    `from` timestamp NOT NULL,
                                    `to` timestamp NOT NULL,
                                    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `carts` (
                         `id` varchar(25) NOT NULL,
                         `user_id` int DEFAULT NULL,
                         `product_id` int DEFAULT NULL,
                         `quantity` int DEFAULT '1',
                         `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                         `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `product_reviews` (
                                   `id` bigint unsigned NOT NULL AUTO_INCREMENT,
                                   `user_id` int NOT NULL,
                                   `product_id` int NOT NULL,
                                   `rating` int DEFAULT NULL,
                                   `review_text` text,
                                   `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                                   `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                                   PRIMARY KEY (`id`),
                                   UNIQUE KEY `id` (`id`),
                                   CONSTRAINT `product_reviews_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `review` (
                          `revId` int NOT NULL AUTO_INCREMENT,
                          `product` int DEFAULT NULL,
                          `star` int NOT NULL,
                          `description` varchar(255) DEFAULT NULL,
                          `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                          PRIMARY KEY (`revId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sessions` (
                            `id` int NOT NULL AUTO_INCREMENT,
                            `session_id` varchar(255) NOT NULL,
                            `user_id` int NOT NULL,
                            `expires_at` datetime NOT NULL,
                            `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                            PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Now add all foreign key constraints
ALTER TABLE `products`
    ADD KEY `category` (`category`),
    ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category`) REFERENCES `product_category` (`id`);

ALTER TABLE `orders`
    ADD KEY `user_id` (`user_id`),
    ADD KEY `payment_method` (`payment_method`),
    ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
    ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`payment_method`) REFERENCES `payment_methods` (`id`);

ALTER TABLE `order_details`
    ADD KEY `order_id` (`order_id`),
    ADD KEY `product_id` (`product_id`),
    ADD CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
    ADD CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

ALTER TABLE `featured_product`
    ADD CONSTRAINT `featured_product_ibfk_1` FOREIGN KEY (`id`) REFERENCES `products` (`id`);

ALTER TABLE `carts`
    ADD UNIQUE KEY `unique_cart_item` (`user_id`,`product_id`),
    ADD KEY `product_id` (`product_id`),
    ADD CONSTRAINT `carts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
    ADD CONSTRAINT `carts_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

ALTER TABLE `product_reviews`
    ADD UNIQUE KEY `user_id` (`user_id`,`product_id`),
    ADD KEY `product_id` (`product_id`),
    ADD CONSTRAINT `product_reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    ADD CONSTRAINT `product_reviews_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

ALTER TABLE `review`
    ADD KEY `product` (`product`),
    ADD CONSTRAINT `review_ibfk_1` FOREIGN KEY (`product`) REFERENCES `products` (`id`);

ALTER TABLE `sessions`
    ADD KEY `user_id` (`user_id`),
    ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;