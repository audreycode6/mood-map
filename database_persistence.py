from contextlib import contextmanager
import logging
from textwrap import dedent
import psycopg2
from psycopg2.extras import DictCursor

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


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

    """
    ----------------
    USERS QUERIES:
    ----------------
    """

    def user_exists(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        logger.info(f"Executing query: {query}, with username: {username}")
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                return cursor.fetchone()

    def register_new_user(self, username, hashed_password):
        query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        logger.info(
            f"Executing query: {query}, with username: {username} and pwhash {hashed_password}"
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (username, hashed_password))

    """
    ----------------
    ENTRIES QUERIES:
    ----------------
    """

    def check_unique_date(self, user_id, entry_date):
        query = "SELECT * FROM entries WHERE user_id = %s and entry_date = %s"
        logger.info(
            f"Executing query: {query}, with user_id: {user_id} and entry_date {entry_date}"
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
        query_2 = "SELECT id FROM entries WHERE entry_date = %s and user_id = %s"

        logger.info(
            dedent(
                f"""
            Executing query: {query}, with user_id: {user_id},
            entry_date: {entry_date}, energy_level: {energy_level},
            mood_range: {mood_range}, and reflection: {reflection}
            """
            )
        )
        logger.info(
            dedent(
                f"""Executing query: {query_2}, 
              with entry_date: {entry_date} 
              and user_id: {user_id}"""
            )
        )
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
                cursor.execute(query_2, (entry_date, user_id))
                return cursor.fetchone()

    def get_entry(self, entry_id, user_id):
        query = "SELECT * FROM entries WHERE id = %s and user_id = %s"
        logger.info(
            dedent(
                f"""Executing query: {query}, 
              with entry_id: {entry_id} and user_id: {user_id}"""
            )
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (entry_id, user_id))
                return cursor.fetchone()

    def get_users_entries_ids_and_date(self, user_id, page_num, page_view_limit):
        query = """SELECT * FROM entries 
                WHERE user_id = %s 
                ORDER BY entry_date 
                DESC LIMIT %s OFFSET %s"""
        logger.info(
            dedent(
                f"""Executing query: {query}, 
            with user_id: {user_id}, limit: {page_view_limit}, offset: {page_num}"""
            )
        )
        offset_value = page_num * page_view_limit
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (user_id, page_view_limit, offset_value))
                entries = cursor.fetchall()

        return {entry[0]: entry[2] for entry in entries}

    def get_user_entry_count(self, user_id):
        query = "SELECT COUNT(id) FROM entries WHERE user_id = %s"
        logger.info(f"Executing query: {query}, with user_id: {user_id}")
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                return cursor.fetchone()

    def get_entry_date(self, entry_id, user_id):
        query = "SELECT entry_date FROM entries WHERE id = %s and user_id = %s"
        logger.info(
            dedent(
                f"""Executing query: {query},
              with entry_id: {entry_id} and user_id: {user_id}"""
            )
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        entry_id,
                        user_id,
                    ),
                )
                return cursor.fetchone()

    def delete_entry(self, entry_id, user_id):
        query = "DELETE FROM entries WHERE id = %s and user_id = %s"
        logger.info(
            f"Executing query: {query}, with entry_id: {entry_id} and user_id: {user_id}"
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        entry_id,
                        user_id,
                    ),
                )

    def update_entry(
        self, entry_id, entry_date, energy_level, mood_range, reflection, user_id
    ):

        query = """UPDATE entries 
        SET 
        entry_date = %s, 
        energy_level = %s, 
        mood_range = %s,
        reflection = %s
        WHERE id = %s
        and user_id = %s"""
        logger.info(
            dedent(
                f"""Executing query: {query}, 
              with entry_date: {entry_date}, 
              energy_level: {energy_level},
              mood_range: {mood_range}, 
              reflection: {reflection},
              entry_id: {entry_id},
              and user_id: {user_id}
            """
            )
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        entry_date,
                        energy_level,
                        mood_range,
                        reflection,
                        entry_id,
                        user_id,
                    ),
                )

    """
    ---------------------------------------
    Update individual entry attributes
    ---------------------------------------
    """

    def update_entry_entry_date(self, entry_date, entry_id, user_id):
        query = "UPDATE entries SET entry_date = %s WHERE id = %s and user_id = %s"
        logger.info(
            dedent(
                f"""Executing query: {query}, with entry_date: {entry_date},
                entry_id: {entry_id}, and user_id: {user_id}"""
            )
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (entry_date, entry_id, user_id))

    def update_entry_mood_range(self, mood_range, entry_id, user_id):
        query = "UPDATE entries SET mood_range = %s WHERE id = %s and user_id = %s"
        logger.info(
            dedent(
                f"""Executing query: {query}, with mood_range: {mood_range},
                entry_id: {entry_id}, and user_id: {user_id}"""
            )
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (mood_range, entry_id, user_id))

    def update_entry_energy_level(self, energy_level, entry_id, user_id):
        query = "UPDATE entries SET energy_level = %s WHERE id = %s and user_id = %s"
        logger.info(
            dedent(
                f"""Executing query: {query}, with energy_level: {energy_level},
                entry_id: {entry_id}, and user_id: {user_id}"""
            )
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (energy_level, entry_id, user_id))

    def update_entry_reflection(self, reflection, entry_id, user_id):
        query = "UPDATE entries SET reflection = %s WHERE id = %s and user_id = %s"
        logger.info(
            dedent(
                f"""Executing query: {query}, with reflection: {reflection},
                entry_id: {entry_id}, and user_id: {user_id}"""
            )
        )
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (reflection, entry_id, user_id))

    """
    ----------------
    EMOTION QUERIES:
    ----------------
    """

    def add_emotions(self, entry_id, emotions, user_id):
        query = """INSERT INTO emotions (entry_id, emotion)
                    SELECT id, %s FROM entries 
                    WHERE id = %s AND user_id = %s
                """
        logger.info(dedent(f"""Executing query: {query},
                with entry_id: {entry_id}, 
                 emotion: {emotions}, and
                 user_id: {user_id}"""))
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                for emotion in emotions.split():
                    cursor.execute(
                        query,
                        (emotion, entry_id, user_id),
                    )

    def delete_entries_emotions(self, entry_id, user_id):
        query = """
        DELETE FROM emotions 
        WHERE entry_id IN 
            (SELECT id FROM entries 
            WHERE id = %s and user_id = %s
        )"""
        logger.info(dedent(f"""Executing query: {query},
          with entry_id: {entry_id}
            and user_id: {user_id}"""))
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (entry_id, user_id))

    def delete_emotion(self, emotion_id, entry_id, user_id):
        query = """DELETE FROM emotions WHERE id = %s AND entry_id IN (
              SELECT id FROM entries
              WHERE id = %s AND user_id = %s
          )"""
        logger.info(dedent(f"""Executing query: {query}, 
            with emotion_id: {emotion_id},
            entry_id: {entry_id} and,
            user_id: {user_id}"""))
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (emotion_id, entry_id, user_id),
                )

    def get_entry_emotions(self, entry_id):
        query = "SELECT emotion FROM emotions WHERE entry_id = %s ORDER BY emotion"
        logger.info(f"Executing query: {query}, with entry_id: {entry_id}")
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (entry_id,))
                results = cursor.fetchall()

        emotions_list = []
        for result in results:
            emotions_list.extend(result)
        return emotions_list

    def get_emotions_id(self, emotion, entry_id, user_id):
        query = """
        SELECT id FROM emotions
        WHERE emotion = %s
          AND entry_id IN (
              SELECT id FROM entries
              WHERE id = %s AND user_id = %s
          )"""
        logger.info(dedent(f"""Executing query: {query},
              with emotion: {emotion}, entry_id: {entry_id}
              and user_id: {user_id}"""))
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (emotion, entry_id, user_id))
                emotions_id = cursor.fetchone()

                if emotions_id:
                    return emotions_id[0]
                return None

    """
    ----------------
    SET UP SCHEMA
    ----------------
    """

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
                    emotion text NOT NULL,
                    UNIQUE (emotion, entry_id)
                    );
                    """
                    )
