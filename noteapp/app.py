import html
import os
import time

import psycopg
from flask import Flask, redirect, request, url_for

PAGE_TITLE = "Notas en revisión"
# Si es True, /health responde 500 aunque la base de datos esté bien.
FORCE_UNHEALTHY = True

DATABASE_URL = os.environ["DATABASE_URL"]
READY_AFTER_SECONDS = int(os.environ.get("READY_AFTER_SECONDS", "0"))
PORT = int(os.environ.get("PORT", "3000"))

app = Flask(__name__)
started = time.monotonic()


def connect():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def ensure_table():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id serial PRIMARY KEY,
                body text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )


def ready():
    return time.monotonic() - started >= READY_AFTER_SECONDS


@app.get("/health")
def health():
    if FORCE_UNHEALTHY or not ready():
        return "unhealthy", 500
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except Exception:
        return "unhealthy", 500
    return "ok", 200


@app.get("/")
def index():
    notes = []
    error = ""
    try:
        ensure_table()
        with connect() as conn:
            rows = conn.execute(
                "SELECT body, created_at FROM notes ORDER BY id DESC"
            ).fetchall()
        notes = rows
    except Exception:
        error = "No se pudo leer la base de datos."
    return render_page(notes, error)


@app.post("/")
def create():
    body = (request.form.get("body") or "").strip()
    if body:
        ensure_table()
        with connect() as conn:
            conn.execute("INSERT INTO notes (body) VALUES (%s)", (body,))
    return redirect(url_for("index"))


def render_page(notes, error):
    if notes:
        items = "".join(
            f"""<li class="list-group-item d-flex justify-content-between align-items-start gap-3">
              <span>{html.escape(body)}</span>
              <small class="text-body-secondary text-nowrap">{created:%Y-%m-%d %H:%M}</small>
            </li>"""
            for body, created in notes
        )
        note_list = f'<ul class="list-group">{items}</ul>'
    else:
        note_list = '<p class="text-body-secondary mb-0">Todavía no hay notas.</p>'
    message = (
        f'<div class="alert alert-warning" role="alert">{html.escape(error)}</div>'
        if error
        else ""
    )
    title = html.escape(PAGE_TITLE)
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-body-tertiary">
  <main class="container py-5" style="max-width: 40rem">
    <h1 class="h3 mb-4">{title}</h1>
    {message}
    <form method="post" class="card shadow-sm mb-4">
      <div class="card-body">
        <label class="form-label" for="body">Nueva nota</label>
        <div class="input-group">
          <input class="form-control" id="body" name="body" required placeholder="Escribe algo para guardar">
          <button class="btn btn-primary" type="submit">Guardar</button>
        </div>
      </div>
    </form>
    {note_list}
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
