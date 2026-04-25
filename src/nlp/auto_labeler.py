import pandas as pd
import re
import os
from pathlib import Path

def auto_label_review(text):
    if not isinstance(text, str):
        return "nötr/ çöp"
    
    text_lower = text.lower().strip()
    
    # Rule 2: Shortness (< 10 chars)
    if len(text_lower) < 10:
        return "nötr/ çöp"
    
    # Heuristic for ASCII art / drawings (common in Steam reviews)
    if re.search(r'[░▒▓█]{3,}', text) or text.count('\n') > 10:
        return "nötr/ çöp"

    # Keywords for categories
    # 1. bug(hata/hile)
    bug_keywords = [
        "hata", "bozuk", "çalışmıyor", "bug", "crash", "çöktü", "asılıyor", 
        "hile", "hacker", "vac", "ban", "anti-cheat", "anticheat", "adaletsiz",
        "mermi gitmiyor", "hit register", "seçkin hile", "fps", "drop", "donuyor", 
        "kasıyor", "optimizasyon", "lag", "ping", "ms", "takılıyor"
    ]
    
    # 2. feature request(istek)
    request_keywords = [
        "eklenmeli", "gelse", "olsa", "istiyoruz", "tavsiye", "fiyat", "pahalı", 
        "bedava", "olsun", "güncelleme bekliyoruz", "yenilik", "karakter", "harita"
    ]
    
    # Check for Bug (Highest Priority)
    for kw in bug_keywords:
        if kw in text_lower:
            return "bug(hata/hile)"
            
    # Check for Feature Request
    for kw in request_keywords:
        if kw in text_lower:
            return "feature request(istek)"
            
    # Default is neutral/trash
    return "nötr/ çöp"

def main():
    project_root = Path(__file__).parent.parent.parent
    input_path = project_root / "data" / "processed" / "label_ready_reviews.csv"
    output_dir = project_root / "data" / "labeled"
    output_path = output_dir / "labeled_reviews.csv"
    
    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        return

    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    
    print("Labeling reviews into 3 categories: bug(hata/hile), feature request(istek), nötr/ çöp...")
    df['label'] = df['review_text'].apply(auto_label_review)
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        
    print(f"Saving labeled data to {output_path}...")
    df.to_csv(output_path, index=False)
    
    print("New Label distribution:")
    print(df['label'].value_counts())
    print("\nLabeling complete!")

if __name__ == "__main__":
    main()
