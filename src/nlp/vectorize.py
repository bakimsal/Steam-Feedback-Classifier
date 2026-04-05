import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
from pathlib import Path
import sys

# Proje kök dizinini ekle
# C:\\Users\\nurul\\OneDrive\\Desktop\\PYTHON\\Steam-Feedback-Classifier\\src\\nlp\\vectorize.py -> parents[2] is PROJECT_ROOT
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.utils.config import PROCESSED_DATA_DIR, MODELS_DIR, CLEAN_REVIEWS_FILENAME, VECTORIZER_FILENAME

def vectorize_reviews():
    """
    Temizlenmiş metinleri TF-IDF yöntemini kullanarak sayısal vektörlere dönüştürür
    ve eğitilen vektörizeri 'models/' klasörüne kaydeder.
    """
    input_path = PROCESSED_DATA_DIR / CLEAN_REVIEWS_FILENAME
    vectorizer_path = MODELS_DIR / VECTORIZER_FILENAME
    
    if not input_path.exists():
        print(f"Hata: {input_path} bulunamadı! Lütfen önce preprocess.py çalıştırın.")
        return

    print(f"Temizlenmiş veri okunuyor: {input_path}")
    df = pd.read_csv(input_path)
    
    # NaN değerleri kontrol et ve temizle (preprocess aşamasında temizlenmiş olmalı ama güvenli kalalım)
    df = df.dropna(subset=['cleaned_text'])
    
    if len(df) == 0:
        print("Hata: İşlenecek veri kalmadı (tüm metinler boş olabilir).")
        return

    print("TF-IDF Vektörizasyonu başlatılıyor (unigram + bigram)...")
    # max_features=5000: En sık geçen 5000 kelimeyi/ikiliyi baz al
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    
    # Veriyi fit et ve dönüştür
    X = vectorizer.fit_transform(df['cleaned_text'])
    
    # Modeller dizininin varlığından emin ol
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True)
        
    # Vektörizeri (pickle formatında) kaydet
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("-" * 30)
    print(f"Başarılı! Vektörizer şuraya kaydedildi: {vectorizer_path}")
    print(f"Vektör Matrisi Şekli: {X.shape} (Satır: {X.shape[0]}, Sütun/Öznitelik: {X.shape[1]})")
    print("-" * 30)
    
    # İlk 10 kelimeyi/bileşeni yazdır (kontrol amaçlı)
    feature_names = vectorizer.get_feature_names_out()
    print("Örnek kelime dağarcığı (ilk 10):", feature_names[:10])

if __name__ == "__main__":
    vectorize_reviews()
