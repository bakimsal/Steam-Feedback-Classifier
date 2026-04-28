import numpy as np
import pickle
from scipy.sparse import load_npz
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from pathlib import Path
import sys
import time

# Proje kök dizinini ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.utils.config import MODELS_DIR

def train_svm_model():
    """
    Dengeli dataset ile SVM modeli eğitir
    """
    print("=" * 60)
    print("SVM MODEL EĞİTİMİ")
    print("=" * 60)
    
    # Verileri yükle
    X_path = MODELS_DIR / 'X_features_balanced.npz'
    y_path = MODELS_DIR / 'y_labels_balanced.npy'
    model_path = MODELS_DIR / 'svm_model.pkl'
    
    if not X_path.exists() or not y_path.exists():
        print("Hata: Vektörize edilmiş veriler bulunamadı!")
        print("Önce 'python src/models/vectorize_balanced.py' çalıştırın.")
        return
    
    print("\nVeriler yükleniyor...")
    X = load_npz(str(X_path))
    y = np.load(str(y_path), allow_pickle=True)
    
    print(f"X şekli: {X.shape}")
    print(f"y şekli: {y.shape}")
    print(f"Etiketler: {np.unique(y)}")
    
    # Train-test split
    print("\nTrain-test split yapılıyor (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train seti: {X_train.shape[0]} örnek")
    print(f"Test seti: {X_test.shape[0]} örnek")
    
    # SVM modelini eğit
    print("\nSVM modeli eğitiliyor...")
    print("Bu işlem birkaç dakika sürebilir...")
    start_time = time.time()
    
    svm_model = SVC(
        kernel='linear',  # Metin sınıflandırma için linear kernel genellikle en iyisi
        C=1.0,
        class_weight='balanced',  # Sınıf dengesini otomatik ayarla
        random_state=42,
        verbose=True
    )
    
    svm_model.fit(X_train, y_train)
    
    training_time = time.time() - start_time
    print(f"\nEğitim tamamlandı! Süre: {training_time:.2f} saniye")
    
    # Test seti üzerinde tahmin
    print("\nTest seti üzerinde değerlendirme yapılıyor...")
    y_pred = svm_model.predict(X_test)
    
    # Metrikleri hesapla
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "=" * 60)
    print("SVM MODEL SONUÇLARI")
    print("=" * 60)
    print(f"Accuracy: {accuracy:.4f} (%{accuracy*100:.2f})")
    print(f"Eğitim süresi: {training_time:.2f} saniye")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("=" * 60)
    
    # Modeli kaydet
    print("\nModel kaydediliyor...")
    with open(model_path, 'wb') as f:
        pickle.dump(svm_model, f)
    
    print(f"✓ SVM modeli kaydedildi: {model_path}")
    print("=" * 60)
    
    return svm_model, accuracy

if __name__ == "__main__":
    train_svm_model()
