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

from src.utils.config import MODELS_DIR

def clean_text(text):
    """Metni temizle"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def vectorize_balanced_reviews():
    """
    Dengeli dataseti (balanced_reviews.csv) TF-IDF ile vektörize eder
    """
    input_path = Path('data/processed/balanced_reviews.csv')
    vectorizer_path = MODELS_DIR / 'tfidf_vectorizer_balanced.pkl'
    X_path = MODELS_DIR / 'X_features_balanced.npz'
    y_path = MODELS_DIR / 'y_labels_balanced.npy'
    
    if not input_path.exists():
        print(f"Hata: {input_path} bulunamadı!")
        return

    print(f"=" * 60)
    print(f"Dengeli veri okunuyor: {input_path}")
    print(f"=" * 60)
    df = pd.read_csv(input_path)
    
    print(f"Toplam yorum: {len(df)}")
    print(f"\nEtiket dağılımı:")
    print(df['label'].value_counts())
    
    # NLTK bileşenlerini hazırla
    try:
        stop_words = set(stopwords.words('turkish'))
    except Exception:
        print("\nStopwords indiriliyor...")
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        stop_words = set(stopwords.words('turkish'))
        
    stemmer = TurkishStemmer()
    
    print("\nMetin temizleme ve stemming uygulanıyor...")
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

    print(f"\nİşlenen yorum sayısı: {len(df)}")
    print("TF-IDF Vektörizasyonu başlatılıyor...")
    
    # TF-IDF vektörizer
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df['cleaned_text'])
    y = df['label'].values
    
    # Modeller dizininin varlığından emin ol
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True)
        
    # 1. Vektörizeri kaydet
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # 2. Vektörize edilmiş veriyi kaydet
    from scipy.sparse import save_npz
    save_npz(str(X_path), X)
    np.save(str(y_path), y)
    
    print("\n" + "=" * 60)
    print(f"✓ BAŞARILI!")
    print("=" * 60)
    print(f"Vektörizer kaydedildi: {vectorizer_path}")
    print(f"Özellik matrisi: {X_path}")
    print(f"Etiketler: {y_path}")
    print(f"Vektör Matrisi Şekli: {X.shape}")
    print(f"Özellik sayısı: {X.shape[1]}")
    print("=" * 60)

if __name__ == "__main__":
    vectorize_balanced_reviews()
