CREATE DATABASE car_analytics;
USE car_analytics;


DROP TABLE IF EXISTS cars;

CREATE TABLE cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(50),
    car_brand VARCHAR(50),
    car_model VARCHAR(50),
    car_color VARCHAR(30),
    year_of_manufacture INT,
    credit_card_type VARCHAR(30)
);


SELECT COUNT(*) FROM cars;

SELECT * FROM cars LIMIT 10;

# Top 5 car brands

SELECT car_brand, COUNT(*) AS total
FROM cars
GROUP BY car_brand
ORDER BY total DESC
LIMIT 5;

# Most popular car models

SELECT car_model, COUNT(*) AS total
FROM cars
GROUP BY car_model
ORDER BY total DESC
LIMIT 5;


# Country-wise distribution

SELECT country, COUNT(*) AS total
FROM cars
GROUP BY country
ORDER BY total DESC;

# Year-wise distribution

SELECT year_of_manufacture, COUNT(*) AS total
FROM cars
GROUP BY year_of_manufacture
ORDER BY year_of_manufacture;

# Most popular car color

SELECT car_color, COUNT(*) AS total
FROM cars
GROUP BY car_color
ORDER BY total DESC;

# Car brand popularity by country

SELECT country, car_brand, COUNT(*) AS total
FROM cars
GROUP BY country, car_brand
ORDER BY country, total DESC;

# Credit card usage by car brand

SELECT car_brand, credit_card_type, COUNT(*) AS total
FROM cars
GROUP BY car_brand, credit_card_type
ORDER BY car_brand, total DESC;

# Most common car brand per country

SELECT country, car_brand, COUNT(*) AS total
FROM cars
GROUP BY country, car_brand
ORDER BY country, total DESC;

# Oldest and newest cars in the dataset

SELECT 
    MIN(year_of_manufacture) AS oldest_car_year,
    MAX(year_of_manufacture) AS newest_car_year
FROM cars;

