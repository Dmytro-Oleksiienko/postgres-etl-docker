# postgres-etl-docker

A simple ETL (Extract, Transform, Load) pipeline built with **Python** and **PostgreSQL**, fully containerized with **Docker Compose**.

The script connects to a PostgreSQL database, creates two tables (`source_users` and `target_users`), seeds the source table with sample data, and migrates the records to the target table — printing a summary of rows read and written.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | ETL script |
| psycopg2 | PostgreSQL adapter |
| python-dotenv | Environment variable management |
| PostgreSQL 16 | Database |
| Docker & Docker Compose | Containerization & orchestration |

---

## Project Structure

```
.
├── main.py              # ETL script
├── requirements.txt     # Python dependencies
├── Dockerfile           # App container image
├── docker-compose.yml   # Multi-service orchestration
├── .env.example         # Environment variable template
└── .gitignore
```

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed

### 1. Clone the repository

```bash
git clone https://github.com/Dmytro-Oleksiienko/postgres-etl-docker.git
cd postgres-etl-docker
```

### 2. Configure environment variables

```bash
cp ".env.example " .env
# Edit .env and set your DB credentials
```

### 3. Run with Docker Compose

```bash
docker compose up --build
```

Docker Compose will:
1. Start a **PostgreSQL 16** container and wait until it is healthy
2. Build and run the **Python ETL app** container

### 4. Expected output

```
Source table:
('Alice', 'alice@mail.com')
('Bob', 'bob@mail.com')
('Charlie', 'charlie@mail.com')

 Target_table:
('Alice', 'alice@mail.com')
('Bob', 'bob@mail.com')
('Charlie', 'charlie@mail.com')
Rows read: 3
Rows written: 3
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | Database hostname | `localhost` |
| `DB_PORT` | Database port | `1234` |
| `DB_NAME` | Database name | `mydb` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `change_me` |

> **Never commit your `.env` file** — it is listed in `.gitignore`.

---

## How It Works

1. **Connection** — connects to PostgreSQL using credentials from environment variables
2. **Schema setup** — creates `source_users` and `target_users` tables (idempotent via `IF NOT EXISTS`)
3. **Seeding** — inserts sample users into `source_users` (ignores duplicates via `ON CONFLICT DO NOTHING`)
4. **Migration** — reads all rows from `source_users` and inserts them into `target_users`
5. **Reporting** — prints both tables and a summary of rows read/written
6. **Cleanup** — commits the transaction and closes the connection

---

## License

This project is for educational purposes.
