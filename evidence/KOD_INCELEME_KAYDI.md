# Kod İnceleme Kaydı (Issue #10 – Kanıt: Review kaydı)

**Kapsam:** app.py, schema.sql, templates/*, static/style.css, tests/*
**Standart:** Coding Standards kontrol listesi (PEP 8 + proje kuralları)
**Araçlar:** `flake8 --max-line-length=130`, `pytest --cov`, manuel okuma
**Reviewer:** ______________ (doldur)  **Tarih:** ____/____/2026

## 1. Kontrol listesi

| # | Kontrol maddesi | Sonuç | Not |
|---|-----------------|-------|-----|
| 1 | Anlamlı değişken/fonksiyon isimleri | ✔ Uygun | `allowed_moves`, `add_defect`, `TRANSITIONS` |
| 2 | PEP 8 biçim uyumu | ✘ Uygun değil | flake8: 27 uyarı (bkz. B-01) |
| 3 | Fonksiyonlar tek sorumluluklu / kısa | ✔ Uygun | `reports()` görece uzun (B-08) |
| 4 | Sihirli sabit yok, durumlar sabit tanımlı | ✔ Uygun | `STATUSES`, `TRANSITIONS`, `DEFECT_FROM` |
| 5 | SQL parametreli (SQL injection yok) | ✔ Uygun | Tüm sorgular `?` ile; `move()` içindeki f-string yalnızca sabit metin ekliyor (B-07) |
| 6 | Parola düz metin saklanmıyor | ✔ Uygun | `generate_password_hash` |
| 7 | Yetki kontrolü her uçta var | ✔ Uygun | `before_request` + `@roles` + `allowed_moves` |
| 8 | Girdi doğrulama (sunucu tarafı) | ✘ Eksik | B-05, B-06 |
| 9 | Gizli anahtar / hata ayıklama ayarı güvenli | ✘ Eksik | B-02, B-03 |
| 10 | CSRF koruması | ✘ Yok | B-04 |
| 11 | Hata durumları yönetiliyor (403/404) | ✔ Uygun | `abort(403/404)` testli |
| 12 | Yorum / docstring | Kısmen | Karmaşık yerlerde yorum var, fonksiyon docstring'i yok |
| 13 | Birim/entegrasyon testi var | ✔ Uygun | 26 test, kapsam %98+ |
| 14 | Bağımlılıklar requirements.txt'de | ✔ Düzeltildi | pytest, pytest-cov eklendi |
| 15 | DB / __pycache__ repoda yok | ✔ Düzeltildi | `.gitignore` eklendi |

## 2. Bulgular

| ID | Önem | Dosya | Bulgu | Önerilen aksiyon | Durum |
|----|------|-------|-------|------------------|-------|
| B-01 | Minor | app.py | flake8 27 uyarı: 16×E302, 4×E501 (satır >130), E401, E701/E702, E731, W292 | Biçimlendir (`black` / elle) | Açık → Issue #17 |
| B-02 | Major | app.py | `SECRET_KEY` varsayılanı `"degistir-beni"` | Ortam değişkeni zorunlu yap / rastgele üret | Açık → Issue #17 |
| B-03 | Major | app.py | `app.run(debug=True)` sabit | `debug` env ile aç/kapat | Açık → Issue #17 |
| B-04 | Major | templates | POST formlarında CSRF token yok | Flask-WTF / elle token | Açık → Issue #17 |
| B-05 | Minor | app.py | `priority` ve `severity` değerleri sunucuda doğrulanmıyor | İzinli liste kontrolü | Açık → Issue #17 |
| B-06 | Minor | app.py | `assign()` atanan kişinin developer olduğunu doğrulamıyor | Rol kontrolü ekle | Açık → Issue #17 |
| B-07 | Info | app.py | `move()` içinde f-string SQL (şu an güvenli, sabit metin) | Parametreli yaz | Açık |
| B-08 | Info | app.py | `reports()` çok iş yapıyor | Sorguları yardımcı fonksiyona böl | Açık |
| B-09 | Info | reset.py | Onay sormadan tüm task'ları siler | Onay istemi ekle | Açık |
| B-10 | Info | app.py | `assign` geçmiş kaydında eski/yeni kişi yok | Notta isimleri yaz | Açık |

> Bu kayıttaki "Açık" bulgular Issue #17 (Hata düzeltme ve iyileştirme) kapsamında çözülecek; çözülünce bu tabloyu güncelle.
