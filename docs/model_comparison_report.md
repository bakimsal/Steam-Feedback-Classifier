# 📊 Model Karşılaştırma Raporu

**Proje:** Steam Feedback Classifier  
**Tarih:** 28 Nisan 2026  
**Hazırlayan:** Musa  
**Veri Seti:** 8.700 dengeli yorum (2.900 bug + 2.900 feature request + 2.900 nötr)

---

## 🏆 Sonuç Tablosu

| Model | Accuracy | Eğitim Süresi | Model Tipi |
|-------|----------|---------------|------------|
| **CatBoost** | **%94.87** 🥇 | 33.36 sn | Gradient Boosting |
| **BerTURK** | **%93.97** 🥈 | ~5-10 dk (GPU) | Deep Learning (Transformer) |
| **SVM** | **%92.86** 🥉 | 3.39 sn | Geleneksel ML |

---

## 📈 Detaylı Model Sonuçları

### 1. SVM (Support Vector Machine)
- **Accuracy:** %92.86
- **Öznitelik:** TF-IDF vektörizasyonu
- **Eğitim Süresi:** 3.39 saniye
- **Avantaj:** En hızlı eğitim, düşük kaynak tüketimi
- **Dezavantaj:** Bağlam (context) bilgisini yakalayamaz

### 2. CatBoost
- **Accuracy:** %94.87
- **Öznitelik:** TF-IDF vektörizasyonu
- **Eğitim Süresi:** 33.36 saniye
- **Avantaj:** Kategorik verilerle güçlü, overfitting'e dayanıklı
- **Dezavantaj:** Kelime sırasını (word order) dikkate almaz

### 3. BerTURK (BERT-base Turkish Cased)
- **Accuracy:** %93.97
- **Model:** `dbmdz/bert-base-turkish-cased`
- **Eğitim:** Google Colab (T4 GPU), 3 epoch
- **Hiperparametreler:**
  - Learning Rate: 2e-5
  - Batch Size: 16 (train), 32 (eval)
  - Max Length: 128 token
  - Warmup Steps: 100
  - Weight Decay: 0.01
- **Avantaj:** Bağlamsal anlam çıkarımı, transfer öğrenme
- **Dezavantaj:** Yüksek kaynak gereksinimi (GPU zorunlu)

### BerTURK Örnek Tahminleri

| Yorum | Tahmin | Güven |
|-------|--------|-------|
| "Oyun sürekli çöküyor, FPS 10'a düşüyor, optimizasyon berbat" | bug(hata/hile) | %99.92 |
| "Türkiye sunucusu eklerseniz çok sevinirim" | feature request(istek) | %81.69 |
| "Güzel oyun arkadaşlarla oynayınca daha eğlenceli" | nötr/çöp | %99.79 |
| "Hileciler yüzünden oyun oynanmıyor, anti-cheat sistemi geliştirmelisiniz" | bug(hata/hile) | %99.93 |
| "Silah skinsleri için yeni bir market sistemi olmalı" | feature request(istek) | %99.70 |

---

## 🔍 CatBoost Neden BerTURK'ü Geçti?

BerTURK gibi büyük bir Transformer modelin CatBoost'un gerisinde kalması ilk bakışta şaşırtıcı görünebilir. Ancak bu, NLP literatüründe sıkça karşılaşılan bir durumdur. Nedenleri:

### 1. Veri Seti Boyutu Küçük (8.700 örnek)
BerTURK gibi 110 milyon parametreli bir model, en iyi performansını **on binlerce–yüz binlerce** örnekle verir. 8.700 örnek, bu ölçekteki bir modeli tam kapasiteyle eğitmek için yetersizdir. CatBoost gibi geleneksel modeller ise küçük veri setlerinde çok daha verimli öğrenir.

### 2. Görev Karmaşıklığı Düşük
Üç sınıflı (bug / feature request / nötr) basit bir sınıflandırma görevinde, BerTURK'ün derin bağlamsal anlam çıkarma yeteneği tam olarak gerekli olmayabilir. CatBoost, TF-IDF ile elde edilen anahtar kelime kalıplarını (ör: "çöküyor", "sunucu ekleyin", "güzel oyun") yakalamak için yeterlidir.

### 3. TF-IDF Zaten Güçlü Sinyaller Veriyor
"Bug" sınıfı genellikle "çöküyor", "kasıyor", "hata" gibi belirgin kelimeler içerir. Bu kalıpları TF-IDF rahatlıkla yakalar ve CatBoost bunları çok iyi kullanır.

### 4. BerTURK Hiperparametre Optimizasyonu Yapılmadı
BerTURK varsayılan parametrelerle (3 epoch, lr=2e-5) eğitildi. Epoch sayısı artırılması, learning rate schedule değiştirilmesi veya data augmentation uygulanması ile %95+ sonuçlar elde edilebilir.

---

## 💡 BerTURK Performansını Artırma Önerileri

| Yöntem | Beklenen Etki |
|--------|---------------|
| Epoch sayısını 5-7'ye çıkarmak | +%0.5-1.0 |
| Learning rate warmup + cosine decay | +%0.3-0.5 |
| Veri artırımı (data augmentation) | +%1.0-2.0 |
| Max length'i 256'ya çıkarmak | +%0.2-0.5 |
| Cross-validation ile hiperparametre arama | +%0.5-1.0 |

---

## 🎯 Sonuç ve Yorum

Her üç model de **%90 üzeri başarı** oranıyla görev için yeterli performansı göstermiştir. 

- **Hız ve basitlik** öncelikse → **SVM** (%92.86)
- **En yüksek doğruluk** isteniyorsa → **CatBoost** (%94.87)
- **Ölçeklenebilirlik ve gelecekteki gelişim** düşünülüyorsa → **BerTURK** (%93.97)

BerTURK'ün gerçek gücü, veri seti büyüdükçe ve görev karmaşıklaştıkça ortaya çıkar. Mevcut sonuçlar, 8.700 örneklik küçük bir veri setiyle bile BerTURK'ün rekabetçi olduğunu göstermektedir.

---

## 📁 Model Dosyaları

| Model | Dosya Yolu |
|-------|-----------|
| SVM | `models/svm_model.pkl` |
| CatBoost | `models/catboost_model.pkl` |
| BerTURK | `models/berturk_model/` |
| TF-IDF Vectorizer | `models/tfidf_vectorizer_balanced.pkl` |

---

## 🔧 Eğitim Scriptleri

| Script | Açıklama |
|--------|----------|
| `src/models/train_svm.py` | SVM model eğitimi |
| `src/models/train_catboost.py` | CatBoost model eğitimi |
| `src/models/train_berturk.py` | BerTURK model eğitimi (lokal) |
| `notebooks/berturk_training.ipynb` | BerTURK Colab notebook'u |
| `src/models/vectorize_balanced.py` | TF-IDF vektörizasyon |
