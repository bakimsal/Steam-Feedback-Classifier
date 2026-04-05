import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from TurkishStemmer import TurkishStemmer
from pathlib import Path
import sys
import numpy as np

# Proje kök dizinini ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.utils.config import (
    LABELED_DATA_DIR, 
    MODELS_DIR, 
    VECTORIZER_FILENAME, 
    VECTORIZED_DATA_FILENAME
)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def vectorize_labeled_reviews():
    """
    Etiketlenmiş temizlenmiş metinleri TF-IDF yöntemini kullanarak sayısal vektörlere dönüştürür
    ve eğitilen vektörizeri + vektörize edilmiş veriyi kaydeder.
    """
    input_path = LABELED_DATA_DIR / "labeled_reviews.csv"
    vectorizer_path = MODELS_DIR / VECTORIZER_FILENAME
    vectorized_data_path = MODELS_DIR / VECTORIZED_DATA_FILENAME # vectorized_reviews.npz
    
    if not input_path.exists():
        print(f"Hata: {input_path} bulunamadı! Lütfen önce etiketleme işlemini yapın.")
        return

    print(f"Etiketlenmiş veri okunuyor: {input_path}")
    df = pd.read_csv(input_path)
    
    # NLTK bileşenlerini hazırla
    try:
        stop_words = set(stopwords.words('turkish'))
    except Exception:
        print("Stopwords indiriliyor...")
        nltk.download('stopwords')
        nltk.download('punkt')
        stop_words = set(stopwords.words('turkish'))
        
    stemmer = TurkishStemmer()
    
    print("Metin temizleme ve stemming uygulanıyor...")
    def process_text(text):
        cleaned = clean_text(text)
        tokens = word_tokenize(cleaned)
        stemmed = [stemmer.stem(w) for w in tokens if w not in stop_words]
        return " ".join(stemmed)

    df['cleaned_text'] = df['review_text'].apply(process_text)
    
    # Boş kalanları temizle
    df = df[df['cleaned_text'].str.strip() != ""]
    
    if len(df) == 0:
        print("Hata: İşlenecek veri kalmadı.")
        return

    print("TF-IDF Vektörizasyonu başlatılıyor...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df['cleaned_text'])
    y = df['label'].values
    
    # Modeller dizininin varlığından emin ol
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True)
        
    # 1. Vektörizeri kaydet
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # 2. Vektörize edilmiş veriyi kaydet (X ve y)
    # Sparse matrisi ve etiketleri npz olarak kaydetmek model eğitimi için hız kazandırır
    from scipy.sparse import save_npz
    save_npz(str(MODELS_DIR / "X_features.npz"), X)
    np.save(str(MODELS_DIR / "y_labels.npy"), y)
    
    print("-" * 30)
    print(f"Başarılı! Vektörizer kaydedildi: {vectorizer_path}")
    print(f"Özellik matrisi kaydedildi: models/X_features.npz")
    print(f"Etiketler kaydedildi: models/y_labels.npy")
    print(f"Vektör Matrisi Şekli: {X.shape}")
    print("-" * 30)

if __name__ == "__main__":
    vectorize_labeled_reviews()
