import os, sqlite3
from functools import wraps
from flask import Flask, g, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("TASKFLOW_DB", os.path.join(BASE, "jira-demo.db"))
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "degistir-beni")

STATUSES = ["Development", "Testing", "Defect", "Fix", "Retest", "QA Approved", "Rejected", "Live"]
# durum -> [(hedef durum, izinli rol)]  (Defect'e geçiş, hata formu ile yapılır)
TRANSITIONS = {
    "Development": [("Testing", "developer")],
    "Testing": [("QA Approved", "qa"), ("Rejected", "qa")],
    "Defect": [("Fix", "developer")],
    "Fix": [("Retest", "developer")],
    "Retest": [("QA Approved", "qa"), ("Rejected", "qa")],
    "QA Approved": [("Live", "admin")],
    "Rejected": [("Development", "admin")],
}
DEFECT_FROM = {"Testing", "Retest"}

# ---------- DB ----------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d: d.close()

def init_db():
    con = sqlite3.connect(DB)
    con.executescript(open(os.path.join(BASE, "schema.sql"), encoding="utf-8").read())
    if not con.execute("SELECT 1 FROM users").fetchone():
        for u, n, p, r in [("admin", "Yönetici", "admin123", "admin"),
                           ("dev1", "Ali Yılmaz", "dev123", "developer"),
                           ("dev2", "Ayşe Demir", "dev123", "developer"),
                           ("qa1", "Mehmet Kaya", "qa123", "qa")]:
            con.execute("INSERT INTO users(username,full_name,password_hash,role) VALUES(?,?,?,?)",
                        (u, n, generate_password_hash(p), r))
    con.commit(); con.close()

# ---------- Auth ----------
@app.before_request
def load_user():
    g.user = None
    if session.get("uid"):
        g.user = db().execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()
    if not g.user and request.endpoint not in ("login", "static"):
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = db().execute("SELECT * FROM users WHERE username=?", (request.form["username"],)).fetchone()
        if u and check_password_hash(u["password_hash"], request.form["password"]):
            session["uid"] = u["id"]
            return redirect(url_for("board"))
        flash("Kullanıcı adı veya şifre hatalı.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def roles(*r):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            if g.user["role"] not in r and g.user["role"] != "admin":
                abort(403)
            return f(*a, **k)
        return w
    return deco

def allowed_moves(task):
    u = g.user
    out = []
    for target, role in TRANSITIONS.get(task["status"], []):
        if u["role"] == "admin" or (u["role"] == role and (role != "developer" or task["assignee_id"] == u["id"])):
            out.append(target)
    return out

def log(task_id, frm, to, note=""):
    db().execute("INSERT INTO history(task_id,user_id,from_status,to_status,note) VALUES(?,?,?,?,?)",
                 (task_id, g.user["id"], frm, to, note))

# ---------- Sayfalar ----------
@app.route("/")
def board():
    q = "SELECT t.*, u.full_name AS assignee FROM tasks t LEFT JOIN users u ON u.id=t.assignee_id"
    args = []
    if request.args.get("mine"):
        q += " WHERE t.assignee_id=?"; args.append(g.user["id"])
    rows = db().execute(q + " ORDER BY t.id DESC", args).fetchall()
    cols = {s: [r for r in rows if r["status"] == s] for s in STATUSES}
    return render_template("board.html", cols=cols)

@app.route("/tasks/new", methods=["GET", "POST"])
@roles("admin")
def new_task():
    devs = db().execute("SELECT * FROM users WHERE role='developer'").fetchall()
    if request.method == "POST":
        f = request.form
        cur = db().execute("INSERT INTO tasks(title,description,priority,assignee_id,creator_id) VALUES(?,?,?,?,?)",
                           (f["title"], f["description"], f["priority"], f["assignee_id"] or None, g.user["id"]))
        log(cur.lastrowid, None, "Development", "Task oluşturuldu")
        db().commit()
        return redirect(url_for("task", tid=cur.lastrowid))
    return render_template("new_task.html", devs=devs)

@app.route("/tasks/<int:tid>")
def task(tid):
    t = db().execute("SELECT t.*, u.full_name AS assignee FROM tasks t LEFT JOIN users u ON u.id=t.assignee_id WHERE t.id=?", (tid,)).fetchone() or abort(404)
    defects = db().execute("SELECT d.*, u.full_name AS reporter FROM defects d LEFT JOIN users u ON u.id=d.reporter_id WHERE task_id=? ORDER BY d.id DESC", (tid,)).fetchall()
    hist = db().execute("SELECT h.*, u.full_name FROM history h LEFT JOIN users u ON u.id=h.user_id WHERE task_id=? ORDER BY h.id DESC", (tid,)).fetchall()
    devs = db().execute("SELECT * FROM users WHERE role='developer'").fetchall()
    can_defect = t["status"] in DEFECT_FROM and g.user["role"] in ("qa", "admin")
    return render_template("task.html", t=t, defects=defects, hist=hist, moves=allowed_moves(t), can_defect=can_defect, devs=devs)

@app.post("/tasks/<int:tid>/move")
def move(tid):
    t = db().execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone() or abort(404)
    target = request.form["target"]
    if target not in allowed_moves(t):
        abort(403)
    d = db()
    if t["status"] == "Fix":          # düzeltme tamam -> açık hatalar 'Fixed'
        d.execute("UPDATE defects SET status='Fixed', fixed_at=CURRENT_TIMESTAMP WHERE task_id=? AND status='Open'", (tid,))
    if target == "QA Approved":
        d.execute("UPDATE defects SET status='Closed' WHERE task_id=? AND status!='Closed'", (tid,))
    extra = ", live_at=CURRENT_TIMESTAMP" if target == "Live" else ""
    d.execute(f"UPDATE tasks SET status=?, updated_at=CURRENT_TIMESTAMP{extra} WHERE id=?", (target, tid))
    log(tid, t["status"], target, request.form.get("note", ""))
    d.commit()
    return redirect(url_for("task", tid=tid))

@app.post("/tasks/<int:tid>/defect")
@roles("qa")
def add_defect(tid):
    t = db().execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone() or abort(404)
    if t["status"] not in DEFECT_FROM:
        abort(403)
    f = request.form
    db().execute("INSERT INTO defects(task_id,title,description,severity,reporter_id) VALUES(?,?,?,?,?)",
                 (tid, f["title"], f["description"], f["severity"], g.user["id"]))
    db().execute("UPDATE tasks SET status='Defect', updated_at=CURRENT_TIMESTAMP WHERE id=?", (tid,))
    log(tid, t["status"], "Defect", f"Hata: {f['title']} ({f['severity']})")
    db().commit()
    return redirect(url_for("task", tid=tid))

@app.post("/tasks/<int:tid>/assign")
@roles("admin")
def assign(tid):
    db().execute("UPDATE tasks SET assignee_id=? WHERE id=?", (request.form["assignee_id"] or None, tid))
    log(tid, None, None, "Atanan kişi değiştirildi")
    db().commit()
    return redirect(url_for("task", tid=tid))

@app.route("/reports")
def reports():
    d = db()
    one = lambda q: d.execute(q).fetchone()[0]
    by_status = d.execute("SELECT status, COUNT(*) c FROM tasks GROUP BY status").fetchall()
    by_sev = d.execute("SELECT severity, COUNT(*) c FROM defects GROUP BY severity").fetchall()
    by_dev = d.execute("""SELECT u.full_name, COUNT(DISTINCT t.id) tasks, COUNT(df.id) defects,
        ROUND(1.0*COUNT(df.id)/MAX(COUNT(DISTINCT t.id),1),2) per_task
        FROM users u LEFT JOIN tasks t ON t.assignee_id=u.id LEFT JOIN defects df ON df.task_id=t.id
        WHERE u.role='developer' GROUP BY u.id""").fetchall()
    total = one("SELECT COUNT(*) FROM tasks")
    passed = one("SELECT COUNT(*) FROM tasks WHERE status IN ('QA Approved','Live')")
    clean = one("""SELECT COUNT(*) FROM tasks t WHERE status IN ('QA Approved','Live')
                   AND NOT EXISTS(SELECT 1 FROM defects WHERE task_id=t.id)""")
    rejected = one("SELECT COUNT(*) FROM tasks WHERE status='Rejected'")
    kpi = {
        "total": total, "live": one("SELECT COUNT(*) FROM tasks WHERE status='Live'"),
        "open_defects": one("SELECT COUNT(*) FROM defects WHERE status='Open'"),
        "all_defects": one("SELECT COUNT(*) FROM defects"),
        "first_pass": round(100 * clean / passed) if passed else 0,
        "approval": round(100 * passed / (passed + rejected)) if passed + rejected else 0,
        "avg_fix": d.execute("SELECT ROUND(AVG((julianday(fixed_at)-julianday(created_at))*24),1) FROM defects WHERE fixed_at IS NOT NULL").fetchone()[0],
    }
    return render_template("reports.html", by_status=by_status, by_sev=by_sev, by_dev=by_dev, kpi=kpi)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)