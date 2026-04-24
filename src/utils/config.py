"""
config.py
---------
Proje genelinde kullanılan tüm sabit değerlerin merkezi yapılandırma dosyası.
Kodun içine magic number veya hardcoded string yazmak yerine buradan okunur.
"""

from pathlib import Path

# ── Proje Kök Dizini ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ── Veri Dizinleri ──────────────────────────────────────────────────────────────
RAW_DATA_DIR       = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
LABELED_DATA_DIR   = PROJECT_ROOT / "data" / "labeled"
MODELS_DIR         = PROJECT_ROOT / "models"

# ── Steam Oyun Listesi ──────────────────────────────────────────────────────────
# Key: dosya adında kullanılacak kısa isim
# Value: Steam AppID
GAME_IDS: dict[str, int] = {
    "cs2":   730,
    "dota2": 570,
    "pubg":  578080,
}

# ── Steam API Parametreleri ─────────────────────────────────────────────────────
STEAM_REVIEW_URL    = "https://store.steampowered.com/appreviews/{app_id}"
REVIEW_LANGUAGE     = "turkish"
REVIEWS_PER_PAGE    = 100          # Steam API maksimumu
MAX_REVIEWS_PER_GAME = 35000        # Oyun başına çekilecek maksimum yorum
REQUEST_DELAY_SEC   = 0.6          # Rate limiting: istek arası bekleme süresi

# ── Veri Temizleme Eşikleri ─────────────────────────────────────────────────────
MIN_REVIEW_LENGTH   = 10           # Karakter cinsinden minimum yorum uzunluğu
MAX_REVIEW_LENGTH   = 5000         # Karakter cinsinden maksimum yorum uzunluğu

# ── Çıktı Dosya Adları ──────────────────────────────────────────────────────────
CLEAN_REVIEWS_FILENAME      = "clean_reviews.csv"
LABEL_READY_FILENAME        = "label_ready_reviews.csv"
VECTORIZER_FILENAME         = "tfidf_vectorizer.pkl"
VECTORIZED_DATA_FILENAME    = "vectorized_reviews.npz"

# ── Sütun Adları (Diğer üyelerle ortak standart) ────────────────────────────────
COLUMNS = [
    "review_id",
    "game_name",
    "game_id",
    "review_text",
    "voted_up",
    "votes_helpful",
    "review_date",
    "review_length",
]
LABEL_COLUMN = "label"
