CREATE DATABASE IF NOT EXISTS ev_project;
USE ev_project;

DROP TABLE IF EXISTS state_features_2022;
CREATE TABLE state_features_2022 (
    State CHAR(2),
    state_name VARCHAR(80),
    population INT,
    median_household_income INT,
    renter_occupied_pct DECIMAL(10,4),
    mean_travel_time_to_work_minutes DECIMAL(10,4),
    stations INT,
    level1_ports DECIMAL(18,4),
    level2_ports DECIMAL(18,4),
    dcfc_ports DECIMAL(18,4),
    chargers_per_100k DECIMAL(18,6)
);

-- Run this from the project root so the relative path resolves
LOAD DATA LOCAL INFILE 'data/processed/state_features_2022_sql.csv'
INTO TABLE state_features_2022
FIELDS TERMINATED BY ',' ENCLOSED BY '\"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(State, state_name, population, median_household_income, renter_occupied_pct, mean_travel_time_to_work_minutes, stations, level1_ports, level2_ports, dcfc_ports, chargers_per_100k);

CREATE INDEX idx_state_features_state ON state_features_2022(State);
