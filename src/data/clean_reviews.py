"""
clean_reviews.py
----------------
Ham Steam yorumlarını temizleyen ve işlenmiş veri setini üreten pipeline.

Adımlar:
    1. Tüm ham CSV'leri yükle ve birleştir
    2. Duplicate yorumları kaldır (review_id ve review_text bazında)
    3. Çok kısa yorumları kaldır
    4. Türkçe olmayan yorumları heuristik ile filtrele
    5. İşlenmiş dosyaları kaydet

Kullanım (terminal):
    python3 -m src.data.clean_reviews
"""

import logging
from pathlib import Path

import pandas as pd

from src.utils.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    GAME_IDS,
    MIN_REVIEW_LENGTH,
    COLUMNS,
    LABEL_COLUMN,
    CLEAN_REVIEWS_FILENAME,
    LABEL_READY_FILENAME,
)

logger = logging.getLogger(__name__)

# Türkçe'ye özgü karakterler — dil tespiti için heuristik
_TURKISH_CHARS = set("ğüşıöçĞÜŞİÖÇ")


# ── Yardımcı Fonksiyonlar ───────────────────────────────────────────────────────

def _ensure_directories() -> None:
    """Çıktı dizinlerinin var olduğundan emin olur."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _log_step(step: str, before: int, after: int) -> None:
    """Temizleme adımından önce/sonra satır sayısını loglar."""
    removed = before - after
    logger.info(
        "%-35s → %d satır kaldırıldı | kalan: %d", step, removed, after
    )


# ── Temizleme Fonksiyonları ─────────────────────────────────────────────────────

def load_raw_files(raw_dir: Path) -> pd.DataFrame:
    """
    Tüm oyunlara ait ham CSV dosyalarını yükler ve tek DataFrame'de birleştirir.

    Args:
        raw_dir: Ham CSV dosyalarının bulunduğu klasör yolu.

    Returns:
        Birleştirilmiş ham DataFrame.

    Raises:
        FileNotFoundError: Beklenilen bir CSV dosyası bulunamazsa.
    """
    frames: list[pd.DataFrame] = []

    for game_name in GAME_IDS:
        csv_path = raw_dir / f"{game_name}_raw.csv"
        if not csv_path.exists():
            raise FileNotFoundError(
                f"'{game_name}' için ham veri bulunamadı: {csv_path}\n"
                "Önce 'python3 -m src.data.collect_reviews' komutunu çalıştırın."
            )
        df = pd.read_csv(csv_path)
        logger.info("%-8s → %d yorum yüklendi.", game_name, len(df))
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    logger.info("Toplam birleştirilmiş: %d yorum", len(combined))
    return combined


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tekrar eden yorumları kaldırır.

    İki aşamalı:
        1. review_id üzerinden tam kopyalar
        2. review_text üzerinden içerik kopyaları (farklı ID, aynı metin)

    Args:
        df: Birleştirilmiş ham DataFrame.

    Returns:
        Duplicate'leri temizlenmiş DataFrame.
    """
    before = len(df)

    # 1. review_id üzerinden
    df = df.drop_duplicates(subset=["review_id"], keep="first")

    # 2. review_text üzerinden (boş olmayanlar arasında)
    non_empty_mask = df["review_text"].notna() & (df["review_text"].str.strip() != "")
    df_non_empty  = df[non_empty_mask].drop_duplicates(
        subset=["review_text"], keep="first"
    )
    df_empty = df[~non_empty_mask]
    df = pd.concat([df_non_empty, df_empty], ignore_index=True)

    _log_step("Duplicate kaldırma", before, len(df))
    return df


def remove_short_reviews(df: pd.DataFrame, min_length: int = MIN_REVIEW_LENGTH) -> pd.DataFrame:
    """
    Belirtilen minimum karakter sayısının altındaki yorumları kaldırır.

    Ayrıca boş veya NaN review_text içeren satırları da atar.

    Args:
        df:         Temizlenecek DataFrame.
        min_length: Minimum karakter sayısı (config'den varsayılan alınır).

    Returns:
        Kısa ve boş yorumları kaldırılmış DataFrame.
    """
    before = len(df)

    # Boş / NaN olanları kaldır
    df = df.dropna(subset=["review_text"])
    df = df[df["review_text"].str.strip() != ""]

    # Minimum uzunluk filtresi
    df = df[df["review_text"].str.len() >= min_length]

    _log_step(f"Kısa yorum filtresi (< {min_length} karakter)", before, len(df))
    return df.reset_index(drop=True)


def filter_turkish(df: pd.DataFrame, min_turkish_ratio: float = 0.0) -> pd.DataFrame:
    """
    Türkçe olmayan yorumları filtreler.

    Steam API zaten `language=turkish` parametresiyle çektiği için
    çoğunluk Türkçe'dir. Bu fonksiyon ek bir güvenlik katmanıdır:
    Tamamen Latin karakterlerden oluşan ve hiç Türkçe karakter içermeyen
    çok kısa yorumları (< 15 karakter) atar. Uzun yorumlar korunur çünkü
    çok dilli ya da karma yorumlar değerli olabilir.

    Args:
        df:                 Temizlenecek DataFrame.
        min_turkish_ratio:  Şu an kullanılmıyor; ileride sıkılaştırılabilir.

    Returns:
        Türkçe olmayan kısa yorumları kaldırılmış DataFrame.
    """
    before = len(df)

    def _is_acceptable(text: str) -> bool:
        """Kısa ve tamamen Türkçe karakter içermeyen yorumları reddeder."""
        if len(text) >= 15:
            return True  # Uzun yorumlar korunur
        has_turkish = any(ch in _TURKISH_CHARS for ch in text)
        return has_turkish

    mask = df["review_text"].apply(_is_acceptable)
    df   = df[mask].reset_index(drop=True)

    _log_step("Türkçe olmayan kısa yorum filtresi", before, len(df))
    return df


def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tüm temizleme adımlarını sırayla uygulayan ana pipeline.

    Args:
        df: Birleştirilmiş ham DataFrame.

    Returns:
        Temizlenmiş DataFrame.
    """
    logger.info("=" * 55)
    logger.info("TEMİZLEME PIPELINE BAŞLIYOR — toplam: %d yorum", len(df))
    logger.info("=" * 55)

    df = remove_duplicates(df)
    df = remove_short_reviews(df)
    df = filter_turkish(df)

    # Sütun sıralamasını standartlaştır
    df = df[COLUMNS].copy()

    logger.info("=" * 55)
    logger.info("TEMİZLEME TAMAMLANDI — kalan: %d yorum", len(df))
    logger.info("=" * 55)
    return df


# ── Kaydetme Fonksiyonları ──────────────────────────────────────────────────────

def save_processed(df: pd.DataFrame, output_path: Path) -> None:
    """
    DataFrame'i belirtilen yola CSV olarak kaydeder.

    Args:
        df:          Kaydedilecek DataFrame.
        output_path: Çıktı dosyasının tam Path nesnesi.
    """
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info("Kaydedildi → %s (%d satır)", output_path, len(df))


def build_label_ready(df: pd.DataFrame) -> pd.DataFrame:
    """
    Temizlenmiş DataFrame'e boş `label` sütunu ekleyerek
    etiketlemeye hazır versiyonu üretir.

    Not: Bu dosya 2. Üye'ye teslim edilecektir.
         `label` sütunu kasıtlı olarak boş bırakılmıştır.

    Args:
        df: Temizlenmiş DataFrame (COLUMNS sütunlarına sahip).

    Returns:
        `label` sütunu eklenmiş DataFrame.
    """
    label_ready = df.copy()
    label_ready[LABEL_COLUMN] = ""   # 2. Üye dolduracak
    return label_ready


# ── Ana Giriş Noktası ───────────────────────────────────────────────────────────

def run_cleaning() -> None:
    """
    Tüm temizleme pipeline'ını çalıştırır:
        1. Ham dosyaları yükle ve birleştir
        2. Temizle
        3. clean_reviews.csv kaydet
        4. label_ready_reviews.csv kaydet
    """
    _ensure_directories()

    # 1. Yükle
    raw_df = load_raw_files(raw_dir=RAW_DATA_DIR)

    # 2. Temizle
    clean_df = clean_pipeline(raw_df)

    # 3. Temizlenmiş veriyi kaydet
    clean_path = PROCESSED_DATA_DIR / CLEAN_REVIEWS_FILENAME
    save_processed(clean_df, clean_path)

    # 4. Etiketlemeye hazır veriyi kaydet
    label_ready_df    = build_label_ready(clean_df)
    label_ready_path  = PROCESSED_DATA_DIR / LABEL_READY_FILENAME
    save_processed(label_ready_df, label_ready_path)

    # Özet istatistikler
    logger.info("")
    logger.info("ÖZET")
    logger.info("  Ham toplam          : %d", len(raw_df))
    logger.info("  Temizleme sonrası   : %d", len(clean_df))
    logger.info("  Elenen yorum        : %d", len(raw_df) - len(clean_df))

    # Oyun bazında dağılım
    logger.info("")
    logger.info("Oyun bazında dağılım:")
    for game, count in clean_df["game_name"].value_counts().items():
        logger.info("  %-8s → %d yorum", game, count)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    run_cleaning()
