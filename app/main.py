from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from app.api.config import settings
from app.api.db import init_db
from app.api.service import authenticate_user, create_task, create_user, delete_task, list_tasks, update_task


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="web/templates",
        static_folder="web/static",
    )
    app.secret_key = settings.secret_key

    with app.app_context():
        init_db()

    @app.get("/")
    def index() -> str:
        return render_template("login.html")

    @app.get("/login")
    def login() -> str:
        return render_template("login.html")

    @app.get("/register")
    def register() -> str:
        return render_template("register.html")

    @app.get("/dashboard")
    def dashboard() -> str:
        tasks = []
        summary = {"total": 0, "pending": 0, "in_progress": 0, "done": 0}
        page = max(1, int(request.args.get("page", 1)))
        search = request.args.get("search", "").strip()
        pages = 1
        if session.get("user_id"):
            data = list_tasks(session["user_id"], search=search, page=page)
            tasks = data["items"]
            summary = data["summary"]
            page = data["page"]
            pages = data["pages"]
        return render_template(
            "dashboard.html",
            tasks=tasks,
            summary=summary,
            current_user=session.get("user_name"),
            success_message=request.args.get("success"),
            current_page=page,
            total_pages=pages,
            search_query=search,
        )

    @app.post("/api/register")
    def api_register():
        payload = request.get_json(silent=True) or request.form
        password = payload.get("password", "").strip()
        password_confirm = payload.get("password_confirm", "").strip()
        if password != password_confirm:
            return jsonify({"ok": False, "message": "As senhas não conferem."}), 400
        try:
            user = create_user(
                payload.get("name", "").strip(),
                payload.get("email", "").strip(),
                password,
            )
        except ValueError as exc:
            return jsonify({"ok": False, "message": str(exc)}), 400
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return jsonify({"ok": True, "user": user})

    @app.post("/api/login")
    def api_login():
        payload = request.get_json(silent=True) or request.form
        user = authenticate_user(
            payload.get("email", "").strip(),
            payload.get("password", "").strip(),
        )
        if not user:
            return jsonify({"ok": False, "message": "Credenciais inválidas."}), 401
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return jsonify({"ok": True, "user": user})

    @app.post("/api/logout")
    def api_logout():
        session.clear()
        return jsonify({"ok": True})

    @app.get("/api/tasks")
    def api_tasks_list():
        if not session.get("user_id"):
            return jsonify({"ok": False, "message": "Não autenticado."}), 401
        page = max(1, int(request.args.get("page", 1)))
        search = request.args.get("search", "").strip()
        return jsonify({"ok": True, **list_tasks(session["user_id"], search=search, page=page)})

    @app.post("/api/tasks")
    def api_tasks_create():
        if not session.get("user_id"):
            return jsonify({"ok": False, "message": "Não autenticado."}), 401
        payload = request.get_json(silent=True) or request.form
        description = payload.get("description", "").strip()
        task_datetime = payload.get("task_datetime", "").strip()
        if not description or not task_datetime:
            return jsonify({"ok": False, "message": "Descrição e data/hora são obrigatórias."}), 400
        task = create_task(
            session["user_id"],
            description,
            task_datetime,
            payload.get("status", "Pendente").strip(),
        )
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": True, "message": "Tarefa cadastrada com sucesso.", "task": task}), 201
        return redirect(url_for("dashboard", success="Tarefa cadastrada com sucesso."))

    @app.put("/api/tasks/<int:task_id>")
    def api_tasks_update(task_id: int):
        if not session.get("user_id"):
            return jsonify({"ok": False, "message": "Não autenticado."}), 401
        payload = request.get_json(silent=True) or request.form
        task = update_task(
            task_id,
            session["user_id"],
            payload.get("description", "").strip(),
            payload.get("task_datetime", "").strip(),
            payload.get("status", "Pendente").strip(),
        )
        if not task:
            return jsonify({"ok": False, "message": "Tarefa não encontrada."}), 404
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": True, "message": "Tarefa atualizada com sucesso.", "task": task})
        return redirect(url_for("dashboard", success="Tarefa atualizada com sucesso."))

    @app.delete("/api/tasks/<int:task_id>")
    def api_tasks_delete(task_id: int):
        if not session.get("user_id"):
            return jsonify({"ok": False, "message": "Não autenticado."}), 401
        if not delete_task(task_id, session["user_id"]):
            return jsonify({"ok": False, "message": "Tarefa não encontrada."}), 404
        return jsonify({"ok": True, "message": "Tarefa excluída com sucesso."})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
