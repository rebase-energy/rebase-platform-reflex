#!/usr/bin/env python3
"""
supabase_schema_manager.py

One script for both:
- Apply schema without dropping anything
- Reset (drop public schema) + apply schema

Usage:
  python supabase_schema_manager.py 1   # apply only (no drop)
  python supabase_schema_manager.py 0   # reset public schema + apply

Required env vars (set in .env):
- SUPABASE_DB_USER
- SUPABASE_DB_PASSWORD

Optional env vars:
- SUPABASE_DB_HOST (default: aws-1-eu-west-1.pooler.supabase.com)
- SUPABASE_DB_PORT (default: depends on mode; 5432 for apply, 6543 for reset)
- SUPABASE_DB_NAME (default: postgres)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import psycopg  # noqa: E402


RESET_PUBLIC_SCHEMA_SQL = """
DO $$
BEGIN
  EXECUTE 'DROP SCHEMA IF EXISTS public CASCADE';
  EXECUTE 'CREATE SCHEMA public';
  EXECUTE 'GRANT ALL ON SCHEMA public TO postgres';
  EXECUTE 'GRANT ALL ON SCHEMA public TO public';
END $$;
"""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> "NoReturn":  # type: ignore[name-defined]
        # Print the default usage line, then our explicit explanation.
        self.print_usage(sys.stderr)
        sys.stderr.write(
            "\n"
            "Error: missing required argument MODE.\n\n"
            "MODE is required to avoid accidental destructive resets:\n"
            "  1 = apply schema only (no drop)\n"
            "  0 = RESET public schema (drops all tables) then apply schema\n\n"
            "Examples:\n"
            "  python supabase_schema_manager.py 1\n"
            "  python supabase_schema_manager.py 0\n\n"
        )
        # Keep argparse's original error message for debugging clarity.
        sys.stderr.write(f"Argparse detail: {message}\n")
        raise SystemExit(2)


def _parse_args() -> argparse.Namespace:
    p = _Parser(
        description="Apply Supabase schema (optionally reset public schema first).",
    )
    p.add_argument(
        "mode",
        choices=["0", "1"],
        help=(
            "Required. "
            "1 = apply schema only (no drop). "
            "0 = RESET public schema (drops all tables) then apply schema. "
            "We require this explicitly to prevent accidental destructive resets."
        ),
    )
    p.add_argument(
        "--sql-path",
        default="./supabase_schema.sql",
        help="Path to schema SQL file (default: ./supabase_schema.sql)",
    )
    return p.parse_args()


def run(mode: str, sql_path: str) -> None:
    sql_file = Path(sql_path)
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file path not found: {sql_file}")

    db_user = os.getenv("SUPABASE_DB_USER")
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    if not db_user or not db_password:
        raise RuntimeError("Set SUPABASE_DB_USER and SUPABASE_DB_PASSWORD environment variables first!")

    db_host = os.getenv("SUPABASE_DB_HOST", "aws-1-eu-west-1.pooler.supabase.com")
    # Default port differs by mode (matches prior scripts)
    default_port = "6543" if mode == "0" else "5432"
    db_port = int(os.getenv("SUPABASE_DB_PORT", default_port))
    db_name = os.getenv("SUPABASE_DB_NAME", "postgres")

    print(f"Connecting to {db_host}:{db_port}/{db_name} as {db_user}...")
    with psycopg.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        sslmode="require",
    ) as conn:
        conn.autocommit = False

        if mode == "0":
            print("Dropping and recreating public schema...")
            with conn.cursor() as c:
                c.execute(RESET_PUBLIC_SCHEMA_SQL)

        print(f"Applying schema from {sql_file}...")
        sql = sql_file.read_text(encoding="utf-8")
        with conn.cursor() as c:
            c.execute(sql)

        conn.commit()

    if mode == "0":
        print("Database reset + schema apply complete.")
    else:
        print("Schema apply complete.")


def main() -> None:
    args = _parse_args()
    run(mode=args.mode, sql_path=args.sql_path)


if __name__ == "__main__":
    main()


