from __future__ import annotations

from datetime import datetime

from app.api.db import cursor
from app.api.security import hash_password, verify_password


def create_user(name: str, email: str, password: str) -> dict:
    with cursor() as (conn, cur):
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            raise ValueError("Email já cadastrado.")
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id, name, email",
            (name, email, hash_password(password)),
        )
        user = cur.fetchone()
        conn.commit()
        return dict(user)


def authenticate_user(email: str, password: str) -> dict | None:
    with cursor() as (_, cur):
        cur.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if not user:
            return None
        if not verify_password(password, user["password"]):
            return None
        return {"id": user["id"], "name": user["name"], "email": user["email"]}


def create_task(user_id: int, description: str, task_datetime: str, status: str) -> dict:
    parsed = datetime.fromisoformat(task_datetime)
    with cursor() as (conn, cur):
        cur.execute(
            """
            INSERT INTO tasks (user_id, description, task_datetime, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, description, task_datetime, status
            """,
            (user_id, description, parsed, status),
        )
        task = cur.fetchone()
        conn.commit()
        return dict(task)


def list_tasks(user_id: int, search: str = "", page: int = 1, per_page: int = 10) -> dict:
    offset = (page - 1) * per_page
    like = f"%{search}%"
    with cursor() as (_, cur):
        cur.execute(
            """
            SELECT COUNT(*) AS total
            FROM tasks
            WHERE user_id = %s
              AND (%s = '' OR description ILIKE %s)
            """,
            (user_id, search, like),
        )
        total = cur.fetchone()["total"]
        cur.execute(
            """
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status = 'Pendente') AS pending,
                COUNT(*) FILTER (WHERE status = 'Em andamento') AS in_progress,
                COUNT(*) FILTER (WHERE status = 'Concluída') AS done
            FROM tasks
            WHERE user_id = %s
            """,
            (user_id,),
        )
        summary = dict(cur.fetchone())
        cur.execute(
            """
            SELECT id, description, task_datetime, status
            FROM tasks
            WHERE user_id = %s
              AND (%s = '' OR description ILIKE %s)
            ORDER BY task_datetime DESC
            LIMIT %s OFFSET %s
            """,
            (user_id, search, like, per_page, offset),
        )
        items = [dict(row) for row in cur.fetchall()]
        return {
            "items": items,
            "total": total,
            "page": page,
            "pages": max(1, (total + per_page - 1) // per_page),
            "summary": summary,
        }


def update_task(task_id: int, user_id: int, description: str, task_datetime: str, status: str) -> dict | None:
    parsed = datetime.fromisoformat(task_datetime)
    with cursor() as (conn, cur):
        cur.execute(
            """
            UPDATE tasks
               SET description = %s,
                   task_datetime = %s,
                   status = %s
             WHERE id = %s AND user_id = %s
         RETURNING id, description, task_datetime, status
            """,
            (description, parsed, status, task_id, user_id),
        )
        task = cur.fetchone()
        conn.commit()
        return dict(task) if task else None


def delete_task(task_id: int, user_id: int) -> bool:
    with cursor() as (conn, cur):
        cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s RETURNING id", (task_id, user_id))
        deleted = cur.fetchone() is not None
        conn.commit()
        return deleted
