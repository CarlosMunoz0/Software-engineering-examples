import os

os.environ.setdefault("DATABASE_URL", "postgres://localhost/unused")

import app


def test_placeholder():
    pagina = app.render_page([], "")
    assert "Escribe algo para guardar" in pagina
