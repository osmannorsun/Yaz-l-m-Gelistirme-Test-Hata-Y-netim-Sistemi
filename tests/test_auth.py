"""Issue #7 - Giriş ve rol yönetimi testleri."""
from conftest import login, as_user, make_task


def test_login_page_opens(client):
    assert client.get("/login").status_code == 200


def test_unauthenticated_redirects_to_login(client):
    for url in ("/", "/reports", "/tasks/new", "/tasks/1"):
        r = client.get(url)
        assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_login_success(client):
    r = login(client, "admin", "admin123")
    assert r.status_code == 302
    assert client.get("/").status_code == 200


def test_login_wrong_password(client):
    r = login(client, "admin", "yanlis")
    assert r.status_code == 200
    assert "hatalı" in r.get_data(as_text=True)
    assert client.get("/").status_code == 302


def test_logout_blocks_access(admin):
    admin.get("/logout")
    assert admin.get("/").status_code == 302


def test_developer_cannot_create_task(client):
    login(client, "dev1", "dev123")
    assert client.get("/tasks/new").status_code == 403


def test_qa_cannot_create_task(client):
    login(client, "qa1", "qa123")
    assert client.post("/tasks/new", data={"title": "x", "description": "", "priority": "Low",
                                           "assignee_id": ""}).status_code == 403


def test_developer_cannot_report_defect(admin):
    tid = make_task(admin)
    as_user(admin, "dev1", "dev123")
    r = admin.post(f"/tasks/{tid}/defect", data={"title": "h", "description": "", "severity": "Major"})
    assert r.status_code == 403
