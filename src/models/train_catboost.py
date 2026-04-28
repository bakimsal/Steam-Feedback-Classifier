import numpy as np
import pickle
from scipy.sparse import load_npz
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from pathlib import Path
import sys
import time

# Proje kök dizinini ekle
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from src.utils.config import MODELS_DIR

def train_catboost_model():
    """
    Dengeli dataset ile CatBoost modeli eğitir
    """
    print("=" * 60)
    print("CATBOOST MODEL EĞİTİMİ")
    print("=" * 60)
    
    # Verileri yükle
    X_path = MODELS_DIR / 'X_features_balanced.npz'
    y_path = MODELS_DIR / 'y_labels_balanced.npy'
    model_path = MODELS_DIR / 'catboost_model.pkl'
    
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
    
    # CatBoost modelini eğit
    print("\nCatBoost modeli eğitiliyor...")
    print("Bu işlem birkaç dakika sürebilir...")
    start_time = time.time()
    
    catboost_model = CatBoostClassifier(
        iterations=500,
        learning_rate=0.1,
        depth=6,
        loss_function='MultiClass',
        verbose=100,
        random_seed=42,
        class_weights=None,  # Veri zaten dengeli
        task_type='CPU'
    )
    
    # CatBoost için scipy sparse matrisini dense array'e çevir
    X_train_dense = X_train.toarray()
    X_test_dense = X_test.toarray()
    
    catboost_model.fit(
        X_train_dense, y_train,
        eval_set=(X_test_dense, y_test),
        use_best_model=True,
        early_stopping_rounds=50
    )
    
    training_time = time.time() - start_time
    print(f"\nEğitim tamamlandı! Süre: {training_time:.2f} saniye")
    
    # Test seti üzerinde tahmin
    print("\nTest seti üzerinde değerlendirme yapılıyor...")
    y_pred = catboost_model.predict(X_test_dense)
    
    # Metrikleri hesapla
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "=" * 60)
    print("CATBOOST MODEL SONUÇLARI")
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
        pickle.dump(catboost_model, f)
    
    print(f"✓ CatBoost modeli kaydedildi: {model_path}")
    print("=" * 60)
    
    return catboost_model, accuracy

if __name__ == "__main__":
    train_catboost_model()
