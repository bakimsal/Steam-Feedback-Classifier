"""
collect_reviews.py
------------------
Steam'den 3 oyun için yorum çeken ve data/raw/ dizinine kaydeden orkestrasyon scripti.

Kullanım (terminal):
    python -m src.data.collect_reviews
"""

import logging
from pathlib import Path

import pandas as pd

from src.data.steam_api import fetch_all_reviews
from src.utils.config import (
    GAME_IDS,
    RAW_DATA_DIR,
    MAX_REVIEWS_PER_GAME,
    COLUMNS,
)

logger = logging.getLogger(__name__)


# ── Yardımcı Fonksiyonlar ───────────────────────────────────────────────────────

def _ensure_directories() -> None:
    """Gerekli çıktı dizinlerinin var olduğundan emin olur; yoksa oluşturur."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Çıktı dizini hazır: %s", RAW_DATA_DIR)


def _validate_dataframe(df: pd.DataFrame, game_name: str) -> None:
    """
    Çekilen DataFrame'in beklenen sütunlara sahip olduğunu doğrular.
    Eksik sütun varsa uyarı logu atar.
    """
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        logger.warning("'%s' verisinde eksik sütunlar: %s", game_name, missing)


# ── Ana Fonksiyonlar ────────────────────────────────────────────────────────────

def collect_game_reviews(game_name: str, app_id: int) -> pd.DataFrame:
    """
    Tek bir oyun için Steam yorumlarını çekip DataFrame olarak döner.

    Args:
        game_name: Config'deki kısa oyun adı (ör. "cs2").
        app_id:    Steam AppID (ör. 730).

    Returns:
        Standart sütunlara sahip pandas DataFrame.
    """
    logger.info("=== '%s' (AppID: %d) veri çekimi başlıyor ===", game_name, app_id)

    reviews = fetch_all_reviews(
        app_id=app_id,
        game_name=game_name,
        max_count=MAX_REVIEWS_PER_GAME,
    )

    if not reviews:
        logger.warning("'%s' için hiç yorum çekilemedi!", game_name)
        return pd.DataFrame(columns=COLUMNS)

    df = pd.DataFrame(reviews)

    # Sütun sıralamasını standartlaştır
    df = df[COLUMNS]

    _validate_dataframe(df, game_name)
    logger.info("'%s' tamamlandı — %d yorum çekildi.", game_name, len(df))

    return df


def save_raw_data(df: pd.DataFrame, game_name: str) -> Path:
    """
    DataFrame'i data/raw/{game_name}_raw.csv olarak kaydeder.

    Args:
        df:        Kaydedilecek DataFrame.
        game_name: Dosya adında kullanılacak oyun kısa adı.

    Returns:
        Kaydedilen dosyanın tam Path nesnesi.
    """
    output_path = RAW_DATA_DIR / f"{game_name}_raw.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info("Kaydedildi → %s (%d satır)", output_path, len(df))
    return output_path


def run_collection(skip_existing: bool = True) -> dict[str, int]:
    """
    Tüm oyunlar için veri çekimini sırayla çalıştırır.
    Her oyunun çıktısını ayrı CSV olarak kaydeder.

    Args:
        skip_existing: True ise zaten dolu CSV'si olan oyunları atlar.
                       Bu sayede yarıda kalan çekim kaldığı yerden devam eder.

    Returns:
        {game_name: yorum_sayısı} şeklinde özet dict.
    """
    _ensure_directories()

    summary: dict[str, int] = {}

    for game_name, app_id in GAME_IDS.items():
        existing_path = RAW_DATA_DIR / f"{game_name}_raw.csv"

        if skip_existing and existing_path.exists():
            try:
                existing_df = pd.read_csv(existing_path)
                if len(existing_df) > 0:
                    logger.info(
                        "'%s' zaten mevcut (%d satır) — atlanıyor.",
                        game_name, len(existing_df),
                    )
                    summary[game_name] = len(existing_df)
                    continue
            except Exception:
                pass  # Bozuk dosya varsa yeniden çek

        df = collect_game_reviews(game_name=game_name, app_id=app_id)
        save_raw_data(df=df, game_name=game_name)
        summary[game_name] = len(df)

    logger.info("=" * 50)
    logger.info("VERİ ÇEKME TAMAMLANDI")
    logger.info("=" * 50)
    total = 0
    for game, count in summary.items():
        logger.info("  %-10s → %d yorum", game, count)
        total += count
    logger.info("  TOPLAM     → %d yorum", total)
    logger.info("=" * 50)

    return summary


# ── Giriş Noktası ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
    run_collection()
