def predict_review(text: str, model_name: str) -> dict:
    """
    Basit kural tabanlı dummy tahmin sistemi.
    Gerçek model kullanılmaz, sadece akış test edilir.
    """
    textString = text.lower()
    
    if any(keyword in textString for keyword in ["çök", "hata", "bug"]):
        label = "Bug"
    elif any(keyword in textString for keyword in ["ekle", "olsun", "gelsin"]):
        label = "Feature Request"
    else:
        label = "Neutral"
        
    return {
        "label": label,
        "confidence": 0.85,
        "model": model_name
    }
