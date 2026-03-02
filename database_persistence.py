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

    def check_unique_date(self, user_id, entry_date):
        query = "SELECT * FROM entries WHERE user_id = %s and entry_date = %s"
        print(
            f"==> LOG: Executing query {query}, with user_id: {user_id} and entry_date {entry_date}"
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id,
                        entry_date,
                    ),
                )
                return cursor.fetchone()

    def create_new_entry(
        self, user_id, entry_date, energy_level, mood_range, reflection
    ):
        query = """
        INSERT INTO entries 
        (user_id, entry_date, energy_level, mood_range, reflection)
        VALUES
        (%s, %s, %s, %s, %s)"""
        query_2 = "SELECT id FROM entries WHERE entry_date = %s"

        print(
            f"""
            ==> LOG: Executing query {query}, with user_id: {user_id},
            entry_date: {entry_date}, energy_level: {energy_level},
            mood_range: {mood_range}, and reflection: {reflection}
            """
        )
        print(f"""==> LOG: Executing query {query_2}, with entry_date: {entry_date}""")
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        user_id,
                        entry_date,
                        energy_level,
                        mood_range,
                        reflection,
                    ),
                )
                cursor.execute(query_2, (entry_date,))
                return cursor.fetchone()

    def get_entry(self, entry_id):
        query = "SELECT * FROM entries WHERE id = %s"
        print(f"""==> LOG: Executing query {query}, with entry_id: {entry_id}""")
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (entry_id,))
                return cursor.fetchone()

    def get_entry_date(self, entry_id):
        query = "SELECT entry_date FROM entries WHERE id = %s"
        print(f"""==> LOG: Executing query {query}, with entry_id: {entry_id}""")
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (entry_id,))
                return cursor.fetchone()

    def update_entry(self, entry_id, entry_date, energy_level, mood_range, reflection):

        query = """UPDATE entries 
        SET 
        entry_date = %s, 
        energy_level = %s, 
        mood_range = %s,
        reflection = %s
        WHERE id = %s"""
        print(
            f"""==> LOG: Executing query {query}, 
              with entry_date: {entry_date}, 
              energy_level: {energy_level},
              mood_range: {mood_range}, 
              reflection: {reflection},
              entry_id: {entry_id}"""
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (entry_date, energy_level, mood_range, reflection, entry_id),
                )

    def delete_entry(self, entry_id):
        query = "DELETE FROM entries WHERE id = %s"
        print(f"==> LOG: Executing query {query}, with entry_id: {entry_id}")
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (entry_id,))

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
                        energy_level text NOT NULL,
                        mood_range text NOT NULL,
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
