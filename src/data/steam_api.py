"""
steam_api.py
------------
Steam Store Review API için düşük seviyeli HTTP istemcisi.
Sayfalama (cursor), rate limiting ve hata yönetimini üstlenir.

Kullanım:
    reviews = fetch_all_reviews(app_id=730, game_name="cs2", max_count=2000)
"""

import time
import logging
from datetime import datetime, timezone

import requests

from src.utils.config import (
    STEAM_REVIEW_URL,
    REVIEW_LANGUAGE,
    REVIEWS_PER_PAGE,
    REQUEST_DELAY_SEC,
)

logger = logging.getLogger(__name__)


# ── Yardımcı Fonksiyonlar ───────────────────────────────────────────────────────

def _parse_review(raw: dict, game_name: str, game_id: int) -> dict:
    """
    Steam API'den gelen ham yorum dict'ini projeye ait standart formata dönüştürür.

    Args:
        raw:       Steam API'den gelen tek yorum objesi.
        game_name: Config'deki kısa oyun adı (ör. "cs2").
        game_id:   Steam AppID (ör. 730).

    Returns:
        Standart alanlara sahip düzleştirilmiş yorum dict'i.
    """
    review_text: str = raw.get("review", "")
    timestamp: int   = raw.get("timestamp_created", 0)

    return {
        "review_id":     raw.get("recommendationid", ""),
        "game_name":     game_name,
        "game_id":       game_id,
        "review_text":   review_text,
        "voted_up":      raw.get("voted_up", None),
        "votes_helpful": raw.get("votes_helpful", 0),
        "review_date":   datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d"),
        "review_length": len(review_text),
    }


# ── Ana API Fonksiyonları ───────────────────────────────────────────────────────

def fetch_reviews_page(
    app_id: int,
    cursor: str = "*",
    language: str = REVIEW_LANGUAGE,
) -> tuple[list[dict], str]:
    """
    Steam Store Review API'den tek bir sayfa yorum çeker.

    Args:
        app_id:   Steam AppID.
        cursor:   Sayfalama için Steam cursor değeri (ilk istek için "*").
        language: İstenilen yorum dili (varsayılan: config'den okunur).

    Returns:
        (reviews, next_cursor) tuple'ı.
        reviews:     Bu sayfadaki ham yorum listesi.
        next_cursor: Bir sonraki sayfa için cursor değeri.

    Raises:
        requests.HTTPError: HTTP 4xx/5xx alındığında.
        ValueError:         API success=0 döndürdüğünde.
    """
    url = STEAM_REVIEW_URL.format(app_id=app_id)
    params = {
        "json":          1,
        "language":      language,
        "filter":        "recent",
        "review_type":   "all",
        "purchase_type": "all",
        "num_per_page":  REVIEWS_PER_PAGE,
        "cursor":        cursor,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data: dict = response.json()

    if not data.get("success"):
        raise ValueError(f"Steam API success=0 döndürdü. AppID: {app_id}")

    reviews: list[dict] = data.get("reviews", [])
    next_cursor: str    = data.get("cursor", "")

    return reviews, next_cursor


def fetch_all_reviews(
    app_id: int,
    game_name: str,
    max_count: int,
) -> list[dict]:
    """
    Belirtilen oyun için cursor tabanlı sayfalama ile maksimum `max_count`
    kadar yorum çeker.

    Args:
        app_id:    Steam AppID.
        game_name: Config'deki kısa oyun adı (dosya adında kullanılır).
        max_count: Çekilecek maksimum yorum sayısı.

    Returns:
        Standart formattaki yorum dict listesi.
    """
    all_reviews: list[dict] = []
    cursor: str = "*"
    page: int   = 1

    logger.info("'%s' (AppID: %d) için veri çekimi başlıyor — hedef: %d yorum",
                game_name, app_id, max_count)

    while len(all_reviews) < max_count:
        try:
            raw_reviews, cursor = fetch_reviews_page(app_id=app_id, cursor=cursor)
        except (requests.HTTPError, ValueError, requests.RequestException) as exc:
            logger.error("Sayfa %d alınamadı (%s): %s", page, game_name, exc)
            break

        if not raw_reviews:
            logger.info("'%s' için daha fazla yorum bulunamadı. Duruluyor.", game_name)
            break

        parsed = [_parse_review(r, game_name, app_id) for r in raw_reviews]
        all_reviews.extend(parsed)

        remaining = max_count - len(all_reviews)
        logger.info(
            "Sayfa %d — çekilen: %d | toplam: %d | kalan: %d",
            page, len(raw_reviews), len(all_reviews), max(remaining, 0),
        )

        # Cursor boşsa ya da bir öncekiyle aynıysa son sayfaya ulaşıldı
        if not cursor or cursor == "*":
            logger.info("'%s' için tüm sayfalar tükendi.", game_name)
            break

        page += 1
        time.sleep(REQUEST_DELAY_SEC)

    # max_count'u aşmamak için kes
    return all_reviews[:max_count]


# ── Hızlı Test (doğrudan çalıştırma) ───────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # CS2'den 10 yorum çekip yapıyı kontrol et
    TEST_APP_ID   = 730
    TEST_GAME     = "cs2"
    TEST_COUNT    = 10

    sample = fetch_all_reviews(
        app_id=TEST_APP_ID,
        game_name=TEST_GAME,
        max_count=TEST_COUNT,
    )

    print(f"\n✅ {len(sample)} yorum başarıyla çekildi.")
    if sample:
        print("İlk yorum örneği:")
        for key, value in sample[0].items():
            print(f"  {key:15s}: {value}")
