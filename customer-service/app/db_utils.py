"""
Database utilities for handling connection retries and ensuring
database availability during container startup.
"""
import time
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


def wait_for_db(database_url: str, max_retries: int = 30, retry_interval: int = 2):
    """
    Wait for the database to become available.

    Args:
        database_url: SQLAlchemy database URL
        max_retries: Maximum number of connection attempts
        retry_interval: Seconds to wait between retries

    Raises:
        SystemExit: If database is not available after max_retries
    """
    print(f"Waiting for database to become available...")

    for attempt in range(1, max_retries + 1):
        try:
            # Create a temporary engine just for testing connection
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✓ Database connection established on attempt {attempt}")
            engine.dispose()
            return
        except OperationalError as e:
            if attempt == max_retries:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                print(f"Error: {e}")
                sys.exit(1)

            print(f"Attempt {attempt}/{max_retries}: Database not ready, retrying in {retry_interval}s...")
            print(f"  Error: {e}")
            time.sleep(retry_interval)
        except Exception as e:
            print(f"✗ Unexpected error while connecting to database: {e}")
            sys.exit(1)