CREATE TABLE users (
id serial PRIMARY KEY,
username text UNIQUE NOT NULL CHECK (LENGTH(username) <= 30),
password_hash text NOT NULL);

CREATE TABLE entries (
id serial PRIMARY KEY,
user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
entry_date DATE NOT NULL DEFAULT CURRENT_DATE, 
energy_level int NOT NULL CHECK (energy_level BETWEEN 1 AND 5),
mood_range int NOT NULL CHECK (mood_range BETWEEN 1 AND 5),
reflection text,
UNIQUE (user_id, entry_date)
);

CREATE TABLE emotions (
id serial PRIMARY KEY,
entry_id int NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
emotion text NOT NULL
);