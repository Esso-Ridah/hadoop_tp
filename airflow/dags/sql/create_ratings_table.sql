USE movielens;

CREATE TABLE IF NOT EXISTS ratings (
    userId INT,
    movieId INT,
    rating INT,
    timestamp BIGINT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '::'
STORED AS TEXTFILE; 