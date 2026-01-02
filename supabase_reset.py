#!/usr/bin/env python3
"""
reset_supabase_database.py

This script:
1) Drops all tables (public schema reset),
2) Applies the hardcoded SQL file to recreate tables

Replace SQL_PATH with your .sql file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import psycopg

# === CONFIG ===
SQL_PATH = Path("./supabase_schema.sql")

# Supabase connection parameters
DB_HOST = "aws-1-eu-west-1.pooler.supabase.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = os.getenv("SUPABASE_DB_USER")  # In .env
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")  # In .env

# SQL to remove all tables by resetting the public schema
RESET_PUBLIC_SCHEMA_SQL = """
DO $$
BEGIN
  EXECUTE 'DROP SCHEMA IF EXISTS public CASCADE';
  EXECUTE 'CREATE SCHEMA public';
  EXECUTE 'GRANT ALL ON SCHEMA public TO postgres';
  EXECUTE 'GRANT ALL ON SCHEMA public TO public';
END $$;
"""

def reset_db():
    if DB_USER is None or DB_PASSWORD is None:
        raise RuntimeError("Set SUPABASE_DB_USER and SUPABASE_DB_PASSWORD environment variables first!")

    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL file path not found: {SQL_PATH}")

    print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}...")
    
    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require",
    ) as conn:
        conn.autocommit = False

        # Drop schema & recreate
        print("Dropping and recreating public schema...")
        with conn.cursor() as c:
            c.execute(RESET_PUBLIC_SCHEMA_SQL)

        # Load schema .sql file
        print(f"Applying schema from {SQL_PATH}...")
        sql = SQL_PATH.read_text(encoding="utf-8")
        with conn.cursor() as c:
            c.execute(sql)

        conn.commit()

    print("Database reset complete.")

if __name__ == "__main__":
    reset_db()
