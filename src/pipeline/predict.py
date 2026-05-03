import os
import pickle
import numpy as np
from pathlib import Path
import sys

# Proje kök dizinini ekle
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.nlp.preprocess import full_preprocess
from src.utils.config import MODELS_DIR
from transformers import pipeline

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
            
    if "BerTURK" not in _models:
        try:
            berturk_dir = MODELS_DIR / 'berturk_model'
            if berturk_dir.exists():
                _models["BerTURK"] = pipeline(
                    "text-classification",
                    model=str(berturk_dir),
                    tokenizer=str(berturk_dir),
                    device=-1 # CPU by default or change if needed
                )
            else:
                error_msgs.append("BerTURK modeli bulunamadı.")
        except Exception as e:
            error_msgs.append(f"BerTURK hatası: {str(e)}")
            
    return error_msgs

def predict_review(text: str, model_name: str) -> dict:
    """
    Gerçek modeli kullanarak Steam yorum sınıflandırması yapar.
    """
    try:
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
            
        if len(text.strip()) == 0:
             return {
                 "label": "Neutral", 
                 "confidence": 0.0, 
                 "model": model_name, 
                 "error": "Metin çok kısa veya geçersiz."
             }
             
        raw_label = None
        confidence = None
        
        if model_name == "BerTURK":
            # BerTURK doğrudan metin kullanır
            result = _models["BerTURK"](text[:512])[0] # Limit length to 512 roughly
            raw_label = result['label']
            confidence = float(result['score'])
        else:
            if _vectorizer is None:
                return {
                    "label": None,
                    "confidence": None,
                    "model": model_name,
                    "error": "Vectorizer yüklenemediğinden işlem yapılamıyor."
                }
                
            # 1. Metni temizle (SVM / CatBoost için tam preprocess)
            cleaned = full_preprocess(text)
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
            raw_label = pred[0]
            
            if isinstance(raw_label, (list, tuple, np.ndarray)):
                raw_label = raw_label[0]
                
            # 4. Güven skorunu hesapla
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)[0]
                confidence = float(np.max(proba))
            elif hasattr(model, "decision_function"):
                dec = model.decision_function(X)[0]
                confidence = float(1.0 / (1.0 + np.exp(-np.max(dec))))
            else:
                confidence = 0.85 # Fallback
                
        # Ham etiketi arayüzün beklediği formata dönüştür
        raw_label_str = str(raw_label).lower()
        clean_label = "Neutral"
        if "bug" in raw_label_str:
            clean_label = "Bug"
        elif "feature" in raw_label_str or "istek" in raw_label_str:
            clean_label = "Feature Request"
            
        return {
            "label": clean_label,
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
