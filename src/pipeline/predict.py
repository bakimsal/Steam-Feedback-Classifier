import os
import pickle
import numpy as np
from pathlib import Path
import sys

# Proje kök dizinini ekle
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.nlp.preprocess import clean_text
from src.utils.config import MODELS_DIR

# Modelleri önbellekte tutmak için global değişkenler
_models = {}
_vectorizer = None

def _load_model(filename):
    """Yardımcı model yükleme fonksiyonu."""
    model_path = MODELS_DIR / filename
    if not model_path.exists():
        raise FileNotFoundError(f"{filename} bulunamadı.")
    with open(model_path, 'rb') as f:
        return pickle.load(f)

def load_models():
    global _models, _vectorizer
    error_msgs = []
    
    if _vectorizer is None:
        try:
            _vectorizer = _load_model('tfidf_vectorizer_balanced.pkl')
        except Exception as e:
            error_msgs.append(f"Vectorizer hatası: {str(e)}")
            
    if "SVM" not in _models:
        try:
            _models["SVM"] = _load_model('svm_model.pkl')
        except Exception as e:
            error_msgs.append(f"SVM hatası: {str(e)}")
            
    if "CatBoost" not in _models:
        try:
            _models["CatBoost"] = _load_model('catboost_model.pkl')
        except Exception as e:
            error_msgs.append(f"CatBoost hatası: {str(e)}")
            
    return error_msgs

def predict_review(text: str, model_name: str) -> dict:
    """
    Gerçek modeli kullanarak Steam yorum sınıflandırması yapar.
    """
    global _models, _vectorizer
    
    # Modelleri yükle
    load_errors = load_models()
    
    # İstenen model yüklenememişse hata dön
    if model_name not in _models or _models[model_name] is None:
        err_str = " Model yüklenemedi."
        if load_errors:
            err_str = " " + " | ".join(load_errors)
        return {
            "label": None,
            "confidence": None,
            "model": model_name,
            "error": f"{model_name} modeli kullanılamıyor.{err_str}"
        }
        
    if _vectorizer is None:
        return {
            "label": None,
            "confidence": None,
            "model": model_name,
            "error": "Vectorizer yüklenemediğinden işlem yapılamıyor."
        }
        
    try:
        # 1. Metni temizle
        cleaned = clean_text(text)
        if not cleaned or len(cleaned.strip()) == 0:
             return {
                 "label": "Neutral", 
                 "confidence": 0.0, 
                 "model": model_name, 
                 "error": "Metin çok kısa veya geçersiz (örneğin sadece noktalama)."
             }
             
        # 2. Vektörize et
        X = _vectorizer.transform([cleaned])
        
        # CatBoost eğitimde dense array kullanıldıysa dense'e çevir
        if model_name == "CatBoost":
            X = X.toarray()
            
        model = _models[model_name]
        
        # 3. Tahmin yap
        pred = model.predict(X)
        label = pred[0]
        
        if isinstance(label, (list, tuple, np.ndarray)):
            label = label[0]
            
        # 4. Güven skorunu hesapla
        confidence = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            confidence = float(np.max(proba))
        elif hasattr(model, "decision_function"):
            # SVM predict_proba olmadan (kernel=linear, probability=False) eğitilmişse
            # kaba bir sigmoid güveni üretebiliriz
            dec = model.decision_function(X)[0]
            confidence = float(1.0 / (1.0 + np.exp(-np.max(dec))))
        else:
            confidence = 0.85 # Fallback
            
        return {
            "label": str(label),
            "confidence": confidence,
            "model": model_name,
            "error": None
        }
    except Exception as e:
        return {
            "label": None,
            "confidence": None,
            "model": model_name,
            "error": str(e)
        }
