import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )
except KeyError as e:
    print(f"Missing environment variable: {e}")
    sys.exit(1)
except psycopg2.Error as e:
    print(f"Database connection failed: {e}")
    sys.exit(1)

create_source_users_table = """
CREATE TABLE IF NOT EXISTS source_users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
)
"""

create_target_users_table = """
CREATE TABLE IF NOT EXISTS target_users (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
)
"""

insert_source = """
INSERT INTO source_users (name, email)
VALUES (%s, %s)
ON CONFLICT (email) DO NOTHING
"""

select_source = "SELECT name, email FROM source_users ORDER BY id"

select_target = "SELECT name, email FROM target_users ORDER BY id"

insert_target = """
INSERT INTO target_users (name, email)
VALUES (%s, %s)
ON CONFLICT (email) DO NOTHING
"""

users = [
    ("Alice", "alice@mail.com"),
    ("Bob", "bob@mail.com"),
    ("Charlie", "charlie@mail.com"),
]

rows_read = 0
rows_written = 0

try:
    with connection.cursor() as cursor:
        cursor.execute(create_source_users_table)
        cursor.execute(create_target_users_table)

        cursor.executemany(insert_source, users)

        cursor.execute(select_source)
        rows = cursor.fetchall()
        rows_read = len(rows)
        print("Source table:")
        for row in rows:
            print(row)

        for name, email in rows:
            cursor.execute(insert_target, (name, email))
            rows_written += cursor.rowcount
            
        cursor.execute(select_target)
        rows = cursor.fetchall()
        print("\n Target_table:")
        for row in rows:
            print(row)

    connection.commit()

    print(f"Rows read: {rows_read}")
    print(f"Rows written: {rows_written}")

except psycopg2.Error as e:
    connection.rollback()
    print(f"Database error: {e}")

finally:
    connection.close()