"""Demo verisi üretir, uygulamayı açar, ekran görüntüsü + mobil taşma ölçümü alır."""
import os, sys, subprocess, time, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "evidence", "screenshots")
DBF = "/tmp/taskflow_demo.db"
if os.path.exists(DBF): os.remove(DBF)
os.environ["TASKFLOW_DB"] = DBF
sys.path.insert(0, ROOT)
import app as A
A.app.config["TESTING"] = True
A.init_db()
c = A.app.test_client()
def lg(u, p): c.get("/logout"); c.post("/login", data={"username": u, "password": p})
def mv(t, tgt): c.post(f"/tasks/{t}/move", data={"target": tgt, "note": ""})
lg("admin", "admin123")
ids = []
for title, pr, a in [("Giriş ekranı", "High", "2"), ("Task oluşturma formu", "Medium", "2"), ("Rapor sayfası", "High", "3"),
                     ("Defect formu", "Critical", "3"), ("Pano filtreleme", "Low", "2"), ("Mobil uyum", "Medium", "3")]:
    r = c.post("/tasks/new", data={"title": title, "description": f"{title} geliştirilecek", "priority": pr, "assignee_id": a})
    ids.append(int(r.headers["Location"].split("/")[-1]))
def devmv(t, tgt, who):
    lg(*who); mv(t, tgt)
d1, d2, qa, ad = ("dev1", "dev123"), ("dev2", "dev123"), ("qa1", "qa123"), ("admin", "admin123")
devmv(ids[0], "Testing", d1); devmv(ids[0], "QA Approved", qa); devmv(ids[0], "Live", ad)
devmv(ids[1], "Testing", d1); devmv(ids[1], "QA Approved", qa)
devmv(ids[2], "Testing", d2)
devmv(ids[3], "Testing", d2); lg(*qa)
c.post(f"/tasks/{ids[3]}/defect", data={"title": "Önem alanı kaydedilmiyor", "description": "1) Formu aç 2) Critical seç 3) Kaydet", "severity": "Critical"})
devmv(ids[4], "Testing", d1); lg(*qa)
c.post(f"/tasks/{ids[4]}/defect", data={"title": "Filtre sonuç dönmüyor", "description": "mine=1 boş", "severity": "Major"})
lg(*d1); mv(ids[4], "Fix")
devmv(ids[5], "Testing", d2); devmv(ids[5], "Rejected", qa)

srv = subprocess.Popen([sys.executable, "-c", "import app;app.app.run(port=5055)"], cwd=ROOT, env=os.environ.copy(),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
from playwright.sync_api import sync_playwright
B = "http://127.0.0.1:5055"
res = {}
with sync_playwright() as p:
    br = p.chromium.launch()
    for name, vp in (("masaustu", {"width": 1440, "height": 900}), ("mobil", {"width": 375, "height": 800})):
        ctx = br.new_context(viewport=vp, locale="tr-TR", color_scheme="light")
        pg = ctx.new_page()
        pg.goto(B + "/login"); pg.screenshot(path=f"{OUT}/{name}_1_giris.png", full_page=True)
        res[f"{name}_login_overflow"] = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        pg.fill("[name=username]", "admin"); pg.fill("[name=password]", "admin123"); pg.click("button")
        for key, url, fn in (("2_pano", "/", None), ("3_task_detay", f"/tasks/{ids[3]}", None),
                             ("4_raporlar", "/reports", None), ("5_yeni_task", "/tasks/new", None)):
            pg.goto(B + url); pg.wait_for_load_state()
            pg.screenshot(path=f"{OUT}/{name}_{key}.png", full_page=True)
            res[f"{name}_{key}_overflow"] = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        ctx.close()
    br.close()
srv.terminate()
json.dump(res, open(f"{ROOT}/evidence/mobil_tasma_olcumu.json", "w"), indent=2)
print(json.dumps(res, indent=2))
