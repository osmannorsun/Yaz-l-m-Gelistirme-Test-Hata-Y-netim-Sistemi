import os, sys, tempfile
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Testler gerçek jira-demo.db'yi bozmasın diye geçici veritabanı kullanılır.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["TASKFLOW_DB"] = _tmp.name

import app as app_module  # noqa: E402


@pytest.fixture
def client():
    if os.path.exists(_tmp.name):
        os.remove(_tmp.name)
    app_module.app.config["TESTING"] = True
    app_module.init_db()
    with app_module.app.test_client() as c:
        yield c


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password})


@pytest.fixture
def admin(client):
    login(client, "admin", "admin123")
    return client


def make_task(client, title="Test task", assignee_id="2", priority="High"):
    """Admin olarak task açar, id'sini döner (dev1 id=2)."""
    r = client.post("/tasks/new", data={"title": title, "description": "aciklama",
                                        "priority": priority, "assignee_id": assignee_id})
    assert r.status_code == 302
    return int(r.headers["Location"].rstrip("/").split("/")[-1])


def as_user(client, username, password):
    client.get("/logout")
    login(client, username, password)


def db_one(sql, *args):
    import sqlite3
    con = sqlite3.connect(_tmp.name)
    try:
        return con.execute(sql, args).fetchone()
    finally:
        con.close()
