"""Issue #12 / #13 / #15 - Ekranlar ve raporlar."""
from conftest import make_task, as_user


def test_board_page_opens_with_all_columns(admin):
    html = admin.get("/").get_data(as_text=True)
    for s in ("Development", "Testing", "Defect", "Fix", "Retest", "QA Approved", "Rejected", "Live"):
        assert s in html


def test_four_main_screens_open(admin):
    tid = make_task(admin)
    for url in ("/", f"/tasks/{tid}", "/reports", "/tasks/new"):
        assert admin.get(url).status_code == 200


def test_unknown_task_returns_404(admin):
    assert admin.get("/tasks/9999").status_code == 404


def test_reports_open_on_empty_db(admin):
    r = admin.get("/reports")
    assert r.status_code == 200 and "Kalite Raporları" in r.get_data(as_text=True)


def test_reports_use_real_data(admin):
    tid = make_task(admin)
    as_user(admin, "dev1", "dev123")
    admin.post(f"/tasks/{tid}/move", data={"target": "Testing"})
    as_user(admin, "qa1", "qa123")
    admin.post(f"/tasks/{tid}/defect", data={"title": "h", "description": "", "severity": "Major"})
    html = admin.get("/reports").get_data(as_text=True)
    assert "Ali Yılmaz" in html           # developer tablosu
    assert "Toplam Defect" in html
    from conftest import db_one
    assert db_one("SELECT COUNT(*) FROM defects")[0] == 1


def test_viewport_meta_for_mobile(admin):
    assert 'name="viewport"' in admin.get("/").get_data(as_text=True)


def test_my_tasks_filter(admin):
    make_task(admin, title="Alinin isi", assignee_id="2")
    make_task(admin, title="Aysenin isi", assignee_id="3")
    as_user(admin, "dev1", "dev123")
    html = admin.get("/?mine=1").get_data(as_text=True)
    assert "Alinin isi" in html and "Aysenin isi" not in html
