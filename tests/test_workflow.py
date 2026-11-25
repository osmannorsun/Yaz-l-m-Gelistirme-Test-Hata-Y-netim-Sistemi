"""Issue #8 / #9 / #11 - Task, iş akışı ve defect yönetimi testleri."""
from conftest import make_task, as_user, db_one
import app as app_module


def move(client, tid, target):
    return client.post(f"/tasks/{tid}/move", data={"target": target, "note": "t"})


def test_task_saved_to_db_with_assignee(admin):
    tid = make_task(admin, title="Kayıt testi")
    row = db_one("SELECT title, status, assignee_id FROM tasks WHERE id=?", tid)
    assert row == ("Kayıt testi", "Development", 2)


def test_assignee_can_be_changed(admin):
    tid = make_task(admin, assignee_id="2")
    r = admin.post(f"/tasks/{tid}/assign", data={"assignee_id": "3"})
    assert r.status_code == 302
    assert db_one("SELECT assignee_id FROM tasks WHERE id=?", tid)[0] == 3


def test_invalid_transition_rejected(admin):
    tid = make_task(admin)
    # Development -> Live geçersiz (admin bile yapamaz)
    assert move(admin, tid, "Live").status_code == 403
    assert db_one("SELECT status FROM tasks WHERE id=?", tid)[0] == "Development"


def test_transition_logged_in_history(admin):
    tid = make_task(admin)
    as_user(admin, "dev1", "dev123")
    assert move(admin, tid, "Testing").status_code == 302
    row = db_one("SELECT from_status,to_status FROM history WHERE task_id=? ORDER BY id DESC", tid)
    assert row == ("Development", "Testing")


def test_other_developer_cannot_move_task(admin):
    tid = make_task(admin, assignee_id="2")      # dev1'e atanmış
    as_user(admin, "dev2", "dev123")
    assert move(admin, tid, "Testing").status_code == 403


def test_developer_cannot_approve(admin):
    tid = make_task(admin)
    as_user(admin, "dev1", "dev123")
    move(admin, tid, "Testing")
    assert move(admin, tid, "QA Approved").status_code == 403


def test_defect_changes_status_and_close_on_approval(admin):
    """Issue #11: defect açılınca durum değişir, onayda defect kapanır."""
    tid = make_task(admin)
    as_user(admin, "dev1", "dev123"); move(admin, tid, "Testing")
    as_user(admin, "qa1", "qa123")
    r = admin.post(f"/tasks/{tid}/defect", data={"title": "Buton çalışmıyor", "description": "x", "severity": "Critical"})
    assert r.status_code == 302
    assert db_one("SELECT status FROM tasks WHERE id=?", tid)[0] == "Defect"
    assert db_one("SELECT status, severity FROM defects WHERE task_id=?", tid) == ("Open", "Critical")
    as_user(admin, "dev1", "dev123"); move(admin, tid, "Fix"); move(admin, tid, "Retest")
    assert db_one("SELECT status FROM defects WHERE task_id=?", tid)[0] == "Fixed"
    as_user(admin, "qa1", "qa123"); move(admin, tid, "QA Approved")
    assert db_one("SELECT status FROM defects WHERE task_id=?", tid)[0] == "Closed"


def test_defect_not_allowed_in_wrong_status(admin):
    tid = make_task(admin)
    as_user(admin, "qa1", "qa123")
    r = admin.post(f"/tasks/{tid}/defect", data={"title": "h", "description": "", "severity": "Minor"})
    assert r.status_code == 403   # task henüz Testing'de değil


def test_full_flow_to_live(admin):
    """Issue #15: Task Live'a kadar tüm akıştan geçiyor (uçtan uca)."""
    tid = make_task(admin)
    as_user(admin, "dev1", "dev123"); assert move(admin, tid, "Testing").status_code == 302
    as_user(admin, "qa1", "qa123");   assert move(admin, tid, "QA Approved").status_code == 302
    as_user(admin, "admin", "admin123"); assert move(admin, tid, "Live").status_code == 302
    assert db_one("SELECT status, live_at IS NOT NULL FROM tasks WHERE id=?", tid) == ("Live", 1)


def test_rejected_returns_to_development(admin):
    tid = make_task(admin)
    as_user(admin, "dev1", "dev123"); move(admin, tid, "Testing")
    as_user(admin, "qa1", "qa123");   move(admin, tid, "Rejected")
    as_user(admin, "admin", "admin123"); move(admin, tid, "Development")
    assert db_one("SELECT status FROM tasks WHERE id=?", tid)[0] == "Development"


def test_transition_table_is_consistent():
    for src, targets in app_module.TRANSITIONS.items():
        assert src in app_module.STATUSES
        for tgt, role in targets:
            assert tgt in app_module.STATUSES and role in ("developer", "qa", "admin")
