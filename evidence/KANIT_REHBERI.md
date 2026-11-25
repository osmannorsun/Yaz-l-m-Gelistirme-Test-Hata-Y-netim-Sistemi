# Kanıt Rehberi – Kartlar ve Eklenecek Kanıtlar

Durum: ✅ = bu pakette hazır (karta ekle) · 🟡 = sen yapacaksın (GitHub/Word/PDF tarafı)

## IN PROGRESS kartları

| Issue | Kart | Projede durum | Kanıt (kartta istenen) | Ne ekleyeceksin |
|-------|------|---------------|------------------------|-----------------|
| #10 | Kod gözden geçirme | ✅ Kontrol listesi + 10 bulgu yazıldı | Review kaydı | ✅ `evidence/KOD_INCELEME_KAYDI.md` (reviewer adı/tarihini doldur) |
| #11 | Defect yönetimi | ✅ Kod vardı; testi eklendi (`test_defect_changes_status_and_close_on_approval`) | Commit linki, test sonucu | 🟡 Commit linki · ✅ `evidence/test_ciktisi.txt` |
| #12 | Arayüz ve bileşenler | ✅ Mobil taşma düzeltildi (`style.css`, nav + tablo) | Ekran görüntüleri | ✅ `evidence/screenshots/` (masaüstü + mobil, 4 ana ekran + yeni task) · ✅ `mobil_tasma_olcumu.json` (tüm sayfalarda taşma = 0 px) |
| #13 | Kalite raporları | ✅ Kod vardı; gerçek veriyle test edildi | Commit linki, ekran görüntüsü | 🟡 Commit linki · ✅ `masaustu_4_raporlar.png`, `mobil_4_raporlar.png` |
| #14 | Testleri otomatikleştir | ✅ Eksikti: tek dosyada 2 test vardı. Şimdi `tests/` içinde 26 test, tek komut `pytest` | tests/ klasörü, test çıktısı | 🟡 `tests/` klasörünü commit'le · ✅ `evidence/test_ciktisi.txt` (26 geçti, kapsam %99) |
| #15 | Modüllerin entegrasyonu | ✅ `test_full_flow_to_live` + rol/defect akış testleri | Entegrasyon test sonucu | ✅ `evidence/test_ciktisi.txt` (`test_workflow.py`, `test_auth.py`, `test_ui_reports.py`) |

## DONE kartları

| Issue | Kart | Projede durum | Kanıt (kartta istenen) | Ne ekleyeceksin |
|-------|------|---------------|------------------------|-----------------|
| #1 | Project Description.txt | – | Dosya | 🟡 Dosyayı repoya koy/linkle (zipte yok) |
| #2 | Git deposu kurulumu | ✅ `.gitignore` EKSİKTİ, eklendi (`*.db`, `__pycache__`) | Repo linki, ilk commit | 🟡 Repo linki · ilk commit linki · iki öğrencinin de push ettiğini gösteren commit geçmişi ekran görüntüsü. Not: `jira-demo.db` zipte vardı; daha önce commit'lendiyse `git rm --cached jira-demo.db` yap |
| #3 | Kanban panosunu kur | – | Pano URL'si, Hafta 1 ekran görüntüsü | 🟡 GitHub Projects pano linki + Hafta 1 görüntüsü (pano.json'da 26 kart var, etiketler DEV/DOC/SQA/Git mevcut) |
| #4 | Gereksinim analizi | ✅ Taslak çıkarıldı | Gereksinim listesi taslağı | ✅ `evidence/GEREKSINIM_LISTESI_TASLAGI.md` (SRS numaralarıyla eşleştir) |
| #5 | SRS | – | Requirement_Spec_Doc.pdf | 🟡 Kendi PDF'in (mockup içerdiğinden emin ol; ekran görüntülerim mockup için kaynak olabilir) |
| #26 | SQAP | – | SQAP.docx | 🟡 Kendi dosyan |
| #25 | SDD | – | SDD.docx | 🟡 Kendi dosyan. İçine `evidence/mimari_sema.png` koyabilirsin |
| #6 | Mimari ve veri modeli | ✅ schema.sql zaten vardı (4 tablo + durum tablosu kodda) | Mimari şema, schema.sql | ✅ `evidence/mimari_sema.png` · `schema.sql` (repodan link) |
| #7 | Giriş ve rol yönetimi | ✅ Kod vardı, testi yoktu → `tests/test_auth.py` (8 test) | Commit linki, giriş testi sonucu | 🟡 Commit linki · ✅ test_ciktisi.txt (`test_auth.py` satırları) |
| #8 | Task oluşturma ve atama | ✅ Kod vardı → testler eklendi | Commit linki, test sonucu | 🟡 Commit linki · ✅ `test_task_saved_to_db_with_assignee`, `test_assignee_can_be_changed` |
| #9 | İş akışı | ✅ Kod vardı → testler eklendi | Commit linki, birim testleri | 🟡 Commit linki · ✅ `test_invalid_transition_rejected`, `test_transition_logged_in_history`, `test_transition_table_is_consistent` |

## Önemli notlar
1. **Hiçbir şey commit'lenmedi.** Değişen/yeni dosyalar: `app.py` (DB yolu env ile ayarlanabilir, 1 satır), `static/style.css` (mobil), `requirements.txt`, `.gitignore`, `tests/` (yeni), `evidence/` (yeni). Eski `test_app.py` silindi (testleri `tests/` içinde).
2. Commit linklerini kendi commit'inden alacaksın; ben GitHub'a erişemiyorum. Öneri: commit mesajında issue numarası kullan (`#14 testler eklendi`).
3. Ekran görüntüleri **demo verisiyle** üretildi (senin `jira-demo.db`'ne dokunulmadı). Hocaya "canlı" kanıt gerekiyorsa `python app.py` ile kendi ekranından çekmek en güvenlisi.
4. Kod inceleme bulguları (secret key, debug, CSRF vb.) **düzeltilmedi**, çünkü Issue #17 To Do'da; bulgu olarak kayıtlı.
5. Pano kartlarını güncellemek için: #10–#15, commit + kanıtı karta ekledikten sonra Done'a taşınabilir (#10 reviewer adı doldurulunca).
