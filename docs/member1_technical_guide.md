# 🛠 1. Üye Teknik Dokümantasyon (Veri Toplama ve Hazırlama)

Bu doküman, projenin veri hattını (data pipeline) oluşturan kodların fonksiyon bazlı açıklamalarını içerir.

---

## 1. `src/utils/config.py`
Projenin beyni burasıdır. Tüm sabitler burada tanımlanır.
- **`PROJECT_ROOT`**: Projenin ana dizinini dinamik olarak bulur (farklı bilgisayarlarda çalışabilmesi için).
- **`GAME_IDS`**: Hangi oyunlardan veri çekileceğini (AppID) belirler.
- **`MAX_REVIEWS_PER_GAME`**: Her oyundan maksimum kaç yorum çekileceğini kontrol eder.
- **`COLUMNS`**: Diğer üyelerle ortak kullanılan standart sütun yapısını (ID, Metin, Tarih vb.) belirler.

---

## 2. `src/data/steam_api.py` (API İstemcisi)
Steam Store API ile iletişim kuran dosyadır.

- **`_parse_review()`**: 
  - **Ne yapar?** Steam'den gelen karmaşık JSON verisini temizleyip bizim standart sütunlarımıza yerleştirir.
  - **Kritik İş:** UNIX zaman damgasını (timestamp) okunabilir tarihe çevirir.
- **`fetch_reviews_page()`**: 
  - **Ne yapar?** Steam API'ye tek bir HTTP isteği atar (sayfa başı 100 yorum).
  - **Kritik İş:** Steam'in sunduğu özel `cursor` (sayfalama imleci) değerini yakalar.
- **`fetch_all_reviews()`**: 
  - **Ne yapar?** Bir döngü kurarak hedef sayıya ulaşana kadar sayfaları çeker.
  - **Kritik İş:** `time.sleep` kullanarak Steam'in "Rate Limit" engelini aşar.

---

## 3. `src/data/collect_reviews.py` (Veri Toplayıcı)
Veri çekme işlemini otomatize eden ana scripttir.

- **`_ensure_directories()`**: Çıktı klasörleri (raw, processed) yoksa otomatik oluşturur.
- **`collect_game_reviews()`**: API'den gelen listeyi bir **Pandas DataFrame**'e çevirir ve sütunları hizalar.
- **`save_raw_data()`**: Veriyi `utf-8-sig` kodlamasıyla CSV olarak kaydeder (Türkçe karakterlerin Excel'de bozulmaması için).
- **`run_collection()`**: 
  - **Ne yapar?** Tüm oyunlar üzerinde döner.
  - **Kritik İş:** `skip_existing` mantığıyla, yarım kalan çekimlerin baştan başlamasını engeller, zaman kazandırır.

---

## 4. `src/data/clean_reviews.py` (Temizleme Pipeline)
Ham veriyi işlenmiş veriye dönüştüren en kritik kısımdır.

- **`load_raw_files()`**: 3 farklı oyunun CSV dosyasını birleştirip tek bir dev veri seti (78.000+ satır) oluşturur.
- **`remove_duplicates()`**: 
  - **Aşama 1:** Aynı `review_id`'li kopyaları siler.
  - **Aşama 2:** Farklı ID'ye sahip ama metni birebir aynı olan içerik kopyalarını siler.
- **`remove_short_reviews()`**: 10 karakterden kısa (anlamsız) yorumları temizler.
- **`filter_turkish()`**: 
  - **Heuristik Yöntem:** Eğer yorum kısa ise içinde Türkçe karakter (ğ, ü, ş, ı, ö, ç) olup olmadığına bakar. Yoksa siler. Bu, Steam'in dil filtresinden kaçan İngilizce yorumları eler.
- **`build_label_ready()`**: Temizlenmiş veriye 2. Üye'nin doldurması için boş bir `label` sütunu ekler.

---

## 💡 Hocanın Sorabileceği "Neden?" Soruları

1. **Neden `utf-8-sig` kullandın?**
   - "Hocam, normal UTF-8 bazen Excel'de Türkçe karakterleri bozabiliyor. `utf-8-sig` (Byte Order Mark) sayesinde dosya her ortamda hatasız açılıyor."
2. **Neden Rate Limiting (0.6s) koydun?**
   - "Steam API, saniyede çok fazla istek geldiğinde IP adresini geçici olarak banlıyor. Veri hattının kesilmemesi için bu bekleme süresini ekledim."
3. **Sentetik veri neden gerekli olabilir?**
   - "Hocam, çektiğimiz verilerde 'Bug' ve 'Feature Request' sınıfları az kalırsa, sınıf dengesini (class imbalance) sağlamak için NLP tabanlı veri artırımı yöntemleri kullanacağız."

---
