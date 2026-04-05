# Steam Yorumları Sınıflandırma Kılavuzu (Labeling Guideline)

Bu belge, Steam kullanıcı yorumlarının hangi kategorilere (etiketlere) ayrılacağını ve bu işlemin nasıl yapılacağını açıklar. Projenin amacı, geliştiricilere anlamlı geri bildirimler sunan bir sınıflandırıcı eğitmektir.

## Etiket Kategorileri

| Etiket | Açıklama | Örnek |
| :--- | :--- | :--- |
| **Bug** | Teknik hatalar, çökmeler (crash), grafik bozulmaları veya oynanışı engelleyen aksaklıklar. | "Oyuna girdiğimde ekran siyah oluyor.", "Bölüm sonunda kapı açılmıyor." |
| **Feature Request** | Oyunda olmayan yenilikler, mekanik değişiklikleri veya içerik talepleri. | "Keşke gece gündüz döngüsü olsa.", "Yeni bir karakter eklenmeli." |
| **Performance** | FPS düşüşleri, lag (gecikme), optimizasyon sorunları veya uzun yükleme süreleri. | "FPS 30'un üzerine çıkmıyor.", "Aşırı donma var." |
| **Praise** | Oyunu öven, memnuniyet belirten genel pozitif geri bildirimler. | "Harika bir oyun olmuş.", "Grafikleri çok beğendim." |
| **Spam / Irrelevant** | Oyunla ilgisi olmayan, sadece ödül almak için yazılan veya boş içerikler. | "Nokta.", "Jester farm.", "Buraya bir kedi çiziyorum." |

## Etiketleme Kuralları

1. **Öncelik Sırası:** Bir yorumda hem bir hata (Bug) hem de bir övgü (Praise) varsa, teknik olarak daha değerli olan **Bug** etiketini tercih edin.
2. **Kısalık:** 10 karakterden kısa olan ve anlam ifade etmeyen yorumları doğrudan **Spam** olarak işaretleyin.
3. **Dil:** Sadece Türkçe yorumlar üzerinden işlem yapın. İngilizce veya diğer dillerdeki yorumları veri setinden ayıklayın veya uygunsa **Spam** olarak işaretleyin.
4. **Alaycı Yorumlar:** "Müthiş optimizasyon (!)" gibi alaycı (sarcastic) ifadeler performans şikayeti içerdiği için **Performance** olarak etiketlenmelidir.

## İş Akışı

1. `data/processed/label_ready_reviews.csv` dosyasını açın.
2. `review_text` sütununu okuyun.
3. `label` sütununa yukarıdaki kategorilerden birini yazın.
4. Düzenlenen dosyayı `data/labeled/` altına kaydedin.
