from __future__ import annotations

from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from app.api.config import settings


def get_connection():
    if not settings.database_url:
        raise RuntimeError("DATABASE_STRING ou DATABASE_URL não foi definido.")
    return psycopg.connect(settings.database_url, row_factory=dict_row)


@contextmanager
def cursor():
    with get_connection() as conn:
        with conn.cursor() as cur:
            yield conn, cur


def init_db() -> None:
    with cursor() as (conn, cur):
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                description TEXT NOT NULL,
                task_datetime TIMESTAMP NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
        conn.commit()
