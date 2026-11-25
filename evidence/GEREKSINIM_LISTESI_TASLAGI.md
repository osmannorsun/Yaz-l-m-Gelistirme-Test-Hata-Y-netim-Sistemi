# Gereksinim Listesi Taslağı (Issue #4)

> Uygulamanın gerçek davranışından çıkarılmış taslaktır. Resmi SRS'indeki (Requirement_Spec_Doc.pdf) numaralarla birebir aynı olmalı; farklıysa SRS'ine göre düzelt.

## Kullanıcı rolleri
| Rol | Yetkiler |
|-----|----------|
| Admin | Task açar, developer atar/değiştirir, QA Approved → Live ve Rejected → Development geçişlerini yapar, tüm ekranları görür |
| Developer | Kendine atanan task'ı Development → Testing, Defect → Fix, Fix → Retest taşır |
| QA | Testing/Retest'teki task'ı QA Approved veya Rejected yapar, defect açar |

## Fonksiyonel gereksinimler
| No | Gereksinim | Öncelik |
|----|-----------|---------|
| FR-01 | Kullanıcı kullanıcı adı ve şifre ile giriş yapar | Yüksek |
| FR-02 | Giriş yapmayan kullanıcı hiçbir sayfaya erişemez | Yüksek |
| FR-03 | Sistem admin, developer ve qa rollerini farklı yetkilerle ayırır | Yüksek |
| FR-04 | Admin başlık, açıklama, öncelik ve developer ile task oluşturur | Yüksek |
| FR-05 | Admin task'ın atanan developer'ını değiştirebilir | Orta |
| FR-06 | Task şu durumlardan geçer: Development, Testing, Defect, Fix, Retest, QA Approved, Rejected, Live | Yüksek |
| FR-07 | Geçersiz durum geçişi reddedilir | Yüksek |
| FR-08 | Her durum geçişi (kim, ne zaman, not) geçmişe kaydedilir | Yüksek |
| FR-09 | QA, Testing/Retest'teki task için önem derecesiyle defect açar; task Defect durumuna geçer | Yüksek |
| FR-10 | Düzeltme tamamlanınca defect "Fixed", QA onayında "Closed" olur | Yüksek |
| FR-11 | Pano task'ları duruma göre sütunlarda gösterir; "Task'larım" filtresi vardır | Orta |
| FR-12 | Task detayında defect listesi ve durum geçmişi görünür | Orta |
| FR-13 | Raporlar sayfası KPI, durum/önem grafikleri ve developer bazında defect tablosu gösterir | Orta |

## Fonksiyonel olmayan gereksinimler
| No | Gereksinim | Öncelik |
|----|-----------|---------|
| NFR-01 | Parolalar hash'lenerek saklanır | Yüksek |
| NFR-02 | Arayüz mobil ekranda yatay taşma yapmaz | Orta |
| NFR-03 | Sistem tek komutla (`python app.py`) çalışır | Orta |
| NFR-04 | Otomatik testler tek komutla (`pytest`) çalışır | Orta |
| NFR-05 | Veri SQLite'ta tutulur; DB dosyası repoya girmez | Düşük |
| NFR-06 | Arayüz Türkçedir, açık/koyu temayı destekler | Düşük |
