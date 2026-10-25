import logging
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("etl")

try:
    logger.info(
        "Connecting to database %s at %s:%s",
        os.environ["DB_NAME"], os.environ["DB_HOST"], os.environ["DB_PORT"],
    )
    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )
    logger.info("Connection established")
except KeyError as e:
    logger.error("Missing environment variable: %s", e)
    sys.exit(1)
except (psycopg2.Error, ValueError):
    logger.exception("Database connection failed")
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
        logger.info("Creating tables if not exist")
        cursor.execute(create_source_users_table)
        cursor.execute(create_target_users_table)

        logger.info("Inserting %d users into source_users", len(users))
        cursor.executemany(insert_source, users)

        logger.info("Extracting rows from source_users")
        cursor.execute(select_source)
        rows = cursor.fetchall()
        rows_read = len(rows)
        logger.info("Rows read: %d", rows_read)
        for row in rows:
            logger.debug("Source row: %s", row)

        logger.info("Loading rows into target_users")
        for name, email in rows:
            cursor.execute(insert_target, (name, email))
            if cursor.rowcount == 0:
                logger.warning("Skipped duplicate: %s", email)
            rows_written += cursor.rowcount

        cursor.execute(select_target)
        target_rows = cursor.fetchall()
        for row in target_rows:
            logger.debug("Target row: %s", row)
        logger.info("Target table now has %d rows", len(target_rows))

    connection.commit()
    logger.info("Transaction committed")
    logger.info("ETL finished | read=%d written=%d skipped=%d",
                rows_read, rows_written, rows_read - rows_written)

except Exception:
    connection.rollback()
    logger.exception("ETL failed, transaction rolled back")
    sys.exit(1)

finally:
    connection.close()
    logger.info("Connection closed")