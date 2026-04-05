import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from TurkishStemmer import TurkishStemmer
from pathlib import Path
import sys
import os

# Proje kök dizinini ekle
# C:\\Users\\nurul\\OneDrive\\Desktop\\PYTHON\\Steam-Feedback-Classifier\\src\\nlp\\preprocess.py -> parents[2] is PROJECT_ROOT
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.utils.config import PROCESSED_DATA_DIR, LABEL_READY_FILENAME, CLEAN_REVIEWS_FILENAME

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # Küçük harfe çevir
    text = text.lower()
    
    # URL'leri kaldır
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Noktalama işaretlerini kaldır
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Sayıları kaldır
    text = re.sub(r'\d+', '', text)
    
    # Gereksiz boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_reviews():
    input_path = PROCESSED_DATA_DIR / LABEL_READY_FILENAME
    output_path = PROCESSED_DATA_DIR / CLEAN_REVIEWS_FILENAME
    
    if not input_path.exists():
        print(f"Hata: {input_path} dosyası bulunamadı!")
        return

    print(f"Veri okunuyor: {input_path}")
    df = pd.read_csv(input_path)
    
    # Metin sütunu kontrolü
    if 'review_text' not in df.columns:
        print("Hata: 'review_text' sütunu CSV içinde bulunamadı!")
        return

    # NLTK bileşenlerini hazırla (zaten download edilmiş olmalı)
    try:
        stop_words = set(stopwords.words('turkish'))
    except Exception:
        print("NLTK stopwords indirilemedi, internet bağlantısını kontrol edin.")
        return
        
    stemmer = TurkishStemmer()
    
    print("Metin temizleme, tokenizasyon ve kök ayırma (stemming) başlatılıyor...")
    
    def process_row(text):
        cleaned = clean_text(text)
        tokens = word_tokenize(cleaned)
        # Stopwords kaldır ve Stemming yap
        stemmed = [stemmer.stem(w) for w in tokens if w not in stop_words]
        return " ".join(stemmed)

    df['cleaned_text'] = df['review_text'].apply(process_row)
    
    # Boş kalan satırları temizle (örneğin sadece stopword içeren kısa yorumlar)
    before_count = len(df)
    df = df[df['cleaned_text'].str.strip() != ""]
    after_count = len(df)
    
    print(f"İşlem tamamlandı. {before_count - after_count} adet çok kısa/boş yorum temizlendi.")
    
    # Kaydet
    df.to_csv(output_path, index=False)
    print(f"Temizlenmiş veri şuraya kaydedildi: {output_path}")

if __name__ == "__main__":
    preprocess_reviews()
