from contextlib import contextmanager

import logging
import os
import psycopg2
from psycopg2.extras import DictCursor


class DatabasePersistence:
    def __init__(self):
        self._setup_schema()

    @contextmanager
    def _database_connect(self):
        connection = psycopg2.connect(dbname="mood_map")

        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def user_exists(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        print(f"==> LOG: Executing query {query}, with username: {username}")
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                return cursor.fetchone()

    def register_new_user(self, username, hashed_password):
        query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        print(
            f"==> LOG: Executing query {query}, with username: {username} and pwhash {hashed_password}"
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username, hashed_password))

    def _setup_schema(self):
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                # check if "users" table exists
                cursor.execute(
                    """
                SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'users';
                    """
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        """
                    CREATE TABLE users (
                        id serial PRIMARY KEY,
                        username text UNIQUE NOT NULL CHECK (LENGTH(username) <= 30),
                        password_hash text NOT NULL);
                    """
                    )

                # check if "entries" table exists
                cursor.execute(
                    """
                SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'entries';
                """
                )

                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        """
                    CREATE TABLE entries (
                        id serial PRIMARY KEY,
                        user_id int NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        entry_date DATE NOT NULL DEFAULT CURRENT_DATE, 
                        energy_level int NOT NULL CHECK (energy_level BETWEEN 1 AND 5),
                        mood_range int NOT NULL CHECK (mood_range BETWEEN 1 AND 5),
                        reflection text,
                        UNIQUE (user_id, entry_date)
                    );
                    """
                    )

                # check if "emotions" table exists
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'emotions';
                """
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        """
                    CREATE TABLE emotions (
                    id serial PRIMARY KEY,
                    entry_id int NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
                    emotion text NOT NULL
                    );
                    """
                    )
