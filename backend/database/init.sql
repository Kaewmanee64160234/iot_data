-- db/init.sql

CREATE DATABASE IF NOT EXISTS iot_db;

USE iot_db;

CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    temperature FLOAT,
    humidity FLOAT,
    air_quality FLOAT
);

INSERT INTO sensor_data (timestamp, temperature, humidity, air_quality) VALUES
('2025-04-01 10:00:00', 25.5, 45.0, 80.0),
('2025-04-01 10:01:00', 25.6, 46.0, 82.0),
('2025-04-01 10:02:00', 25.7, 47.0, 83.0);
