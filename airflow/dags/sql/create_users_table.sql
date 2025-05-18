USE movielens;

CREATE TABLE IF NOT EXISTS users (
    userId INT,
    gender STRING,
    age INT,
    occupation INT,
    zipcode STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '::'
STORED AS TEXTFILE; 