# Steam Feedback Classifier — Veri Toplama & Temizleme Raporu
**Hazırlayan:** 1. Üye (Ogulcan)
**Tarih:** 2 Nisan 2026
**Sprint:** 1 (Veri Toplama) + 2 (Veri Temizleme)

---

## 📁 Dosya Konumları

| Dosya | Yol | Açıklama |
|-------|-----|----------|
| Ham CS2 | `data/raw/cs2_raw.csv` | 2000 ham yorum |
| Ham Dota2 | `data/raw/dota2_raw.csv` | 2000 ham yorum |
| Ham PUBG | `data/raw/pubg_raw.csv` | 2000 ham yorum |
| Temizlenmiş | `data/processed/clean_reviews.csv` | 3502 yorum |
| **Etiketlemeye Hazır** | `data/processed/label_ready_reviews.csv` | **3502 yorum, label boş** |

---

## 📊 İstatistikler

### Ham Veri (Sprint 1)
| Oyun | AppID | Çekilen Yorum |
|------|-------|---------------|
| CS2 | 730 | 2000 |
| Dota 2 | 570 | 2000 |
| PUBG | 578080 | 2000 |
| **Toplam** | | **6000** |

### Temizleme Süreci (Sprint 2)

| Adım | Elenen | Kalan |
|------|--------|-------|
| Başlangıç | — | 6.000 |
| Duplicate kaldırma (review_id + metin) | 1.179 | 4.821 |
| Kısa yorum filtresi (< 10 karakter) | 1.040 | 3.781 |
| Türkçe olmayan kısa yorum filtresi | 279 | **3.502** |

### Temizlenmiş Veri Oyun Dağılımı
| Oyun | Yorum Sayısı | Oran |
|------|-------------|------|
| Dota 2 | 1.294 | %37 |
| CS2 | 1.117 | %32 |
| PUBG | 1.091 | %31 |
| **Toplam** | **3.502** | %100 |

---

## 📋 Veri Sütunları

`label_ready_reviews.csv` dosyasındaki sütunlar:

| Sütun | Tür | Açıklama |
|-------|-----|----------|
| `review_id` | int | Steam yorum ID'si (unique) |
| `game_name` | str | `cs2` / `dota2` / `pubg` |
| `game_id` | int | Steam AppID |
| `review_text` | str | Yorum metni |
| `voted_up` | bool | Oyuncu olumlu mu değerlendirdi |
| `votes_helpful` | int | Faydalı bulan sayısı |
| `review_date` | date | Yorum tarihi (YYYY-MM-DD) |
| `review_length` | int | Yorum karakter sayısı |
| **`label`** | str | **⬅ 2. Üye dolduracak (boş)** |

---

## 🏷️ 2. Üye İçin — Etiketleme Talimatları

### Teslim Edilen Dosya
`data/processed/label_ready_reviews.csv`

### Kullanılacak Etiketler

| Etiket | Türkçe | Örnek Yorum |
|--------|--------|-------------|
| `bug` | Hata / Teknik sorun | *"Oyun sürekli kapanıyor, optimizasyon berbat"* |
| `feature_request` | Özellik isteği | *"Türkiye sunucusu olsa çok iyi olurdu"* |
| `neutral` | Genel görüş / Diğer | *"Güzel oyun, arkadaşlarla oynayınca daha eğlenceli"* |

### Kurallar
1. Her satır için `label` sütununa **sadece** şu 3 değerden birini yaz: `bug`, `feature_request`, `neutral`
2. Emin olamadığın yorumları `neutral` olarak işaretle
3. Yorum çok kısa veya anlamsızsa `neutral` yaz
4. Tamamlayınca dosyayı `ogulcan` branch'ine push et

### Örnek Etiketlenmiş Satır
```
review_id,game_name,...,label
222277336,pubg,...,"10 saat sonunda...",bug
221923293,pubg,...,"oyuna aykırı program kullananları...",feature_request
221807518,pubg,...,"PUBG hala o eski gerginliğini...",neutral
```

---

## 🛠️ Teknik Detaylar

### Kullanılan Teknolojiler
- **Python 3.13** + virtual environment (`venv/`)
- `requests` — Steam API HTTP istemcisi
- `pandas` — Veri işleme
- `tqdm` — İlerleme çubuğu

### API Bilgileri
- **Endpoint:** `https://store.steampowered.com/appreviews/{appid}`
- **Dil filtresi:** `language=turkish`
- **Sayfalama:** Cursor tabanlı
- **Rate limiting:** 0.6 saniye bekleme (ban önleme)

### Önemli Notlar
> **CSV Görüntüleme:** VS Code'da dosyayı açtığında satır sayısı yanlış görünebilir.
> Bunun nedeni yorum metinlerinin içindeki satır sonlarıdır. Gerçek kayıt sayısını
> şu komutla doğrulayabilirsin:
> ```bash
> python3 -c "import pandas as pd; df = pd.read_csv('data/processed/label_ready_reviews.csv'); print(len(df))"
> ```

---

## ✅ Kontrol Listesi

- [x] CS2 ham verisi çekildi (2000 yorum)
- [x] Dota2 ham verisi çekildi (2000 yorum)
- [x] PUBG ham verisi çekildi (2000 yorum)
- [x] Duplicate yorumlar kaldırıldı
- [x] Kısa yorumlar filtrelendi
- [x] Türkçe olmayan kısa yorumlar filtrelendi
- [x] `clean_reviews.csv` üretildi (3502 satır)
- [x] `label_ready_reviews.csv` üretildi (label sütunu boş)
- [x] Değişiklikler `ogulcan` branch'ine push edildi
- [ ] 2. Üye etiketlemeyi tamamladı
- [ ] Etiketlenmiş veri merge edildi
