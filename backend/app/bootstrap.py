"""Wait for PostgreSQL and serialize startup migrations across API replicas."""

import os
import subprocess
import time

import psycopg

from .seed import seed


def main() -> None:
    database_url = os.environ["DATABASE_URL"].replace(
        "postgresql+psycopg://", "postgresql://", 1
    )
    for attempt in range(45):
        try:
            connection = psycopg.connect(database_url, connect_timeout=3)
            break
        except psycopg.OperationalError:
            if attempt == 44:
                raise
            time.sleep(2)

    with connection:
        # Only one replica may migrate or load demo data at a time.
        connection.execute("SELECT pg_advisory_lock(588031)")
        try:
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            if os.environ.get("DEMO_SEED") == "1":
                seed()
        finally:
            connection.execute("SELECT pg_advisory_unlock(588031)")


if __name__ == "__main__":
    main()
