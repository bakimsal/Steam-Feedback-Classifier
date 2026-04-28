import os
from pathlib import Path

def predict_review(text: str, model_name: str) -> dict:
    """
    Kullanıcının girdiği metni belirtilen modele göre tahmin eder.
    Gerçek model dosyaları klasörde ise yükler, yoksa hata döndürür.
    """
    
    # 1. BerTURK için özel durum
    if model_name == "BerTURK":
        return {
            "label": None,
            "confidence": None,
            "model": model_name,
            "error": "BerTURK entegrasyonu henüz hazır değil."
        }
        
    # 2. Model ve Vectorizer dosya yollarını belirleme
    base_dir = Path(__file__).resolve().parent.parent.parent
    
    # Modeller src/models/ içinde değil de muhtemelen train sonrası artifacts veya dışa aktarım klasöründe.
    # Şimdilik standart olarak artifacts klasörünü ve kök dizin çevresini arayabiliriz:
    artifacts_dir = base_dir / "artifacts"
    
    model_filenames = {
        "SVM": "svm_model.pkl",
        "CatBoost": "catboost_model.joblib"
    }
    
    expected_file = model_filenames.get(model_name)
    if not expected_file:
        return {
            "label": None,
            "confidence": None,
            "model": model_name,
            "error": f"Bilinmeyen model tipi: {model_name}"
        }
        
    model_path = artifacts_dir / expected_file
    vectorizer_path = artifacts_dir / "vectorizer.pkl"
    
    # 3. Dosya varlık kontrolü
    if not model_path.exists():
        return {
            "label": None,
            "confidence": None,
            "model": model_name,
            "error": f"{model_name} model dosyası bulunamadı. Lütfen modeli eğitip '{model_path.name}' ismiyle '{artifacts_dir.name}' klasörüne ekleyin."
        }
        
    if not vectorizer_path.exists():
        return {
            "label": None,
            "confidence": None,
            "model": model_name,
            "error": f"Vectorizer (vektörizer) dosyası bulunamadı. Lütfen metin işleme pipeline'ını çalıştırıp '{vectorizer_path.name}' ismiyle '{artifacts_dir.name}' klasörüne ekleyin."
        }
        
    # 4. İleride model yükleme kodları buraya gelecek
    # ...
    # return {"label": predicted_label, "confidence": prob, "model": model_name, "error": None}
    
    # Modeller olduğu halde bu prototipte yükleme fonksiyonu tamamlanmamışsa
    return {
        "label": "Gelecekte gerçek sonuç",
        "confidence": 0.0,
        "model": model_name,
        "error": "Model dosyaları bulundu ancak yükleme/tahmin kodları pipeline içine henüz entegre edilmedi."
    }
