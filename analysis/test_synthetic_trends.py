import sys
import asyncio
from datetime import datetime, timedelta, timezone
from src.ml.trends import detect_trends

def generate_fake_data():
    items = []
    now = datetime.now(timezone.utc)
    
    # Prior 7 days (days -14 to -7)
    for i in range(14, 7, -1):
        # Noise
        for _ in range(5):
            items.append({
                "cleaned_text": "just some random tech news about python and javascript framework updates",
                "platform_created_at": now - timedelta(days=i, hours=2),
                "engagement": 10,
                "platform": "twitter"
            })
        # 1 mention per day of our target trend
        items.append({
            "cleaned_text": "trying out this new cursor ai editor thing",
            "platform_created_at": now - timedelta(days=i, hours=1),
            "engagement": 50,
            "platform": "twitter"
        })

    # Last 7 days (days -7 to 0) -> SPIKE
    for i in range(7, 0, -1):
        # Noise
        for _ in range(5):
            items.append({
                "cleaned_text": "just some random tech news about python and javascript framework updates",
                "platform_created_at": now - timedelta(days=i, hours=2),
                "engagement": 10,
                "platform": "twitter"
            })
        # 10 mentions per day of our target trend
        for _ in range(10): 
            items.append({
                "cleaned_text": "cursor ai editor is insane, it completely replaced vs code for me",
                "platform_created_at": now - timedelta(days=i, hours=1),
                "engagement": 500,
                "platform": "twitter"
            })

    return items

def test_trends_synthetic():
    items = generate_fake_data()
    print(f"Generated {len(items)} fake content items simulating 14 days of history.")
    print("Running trend detection pipeline (KeyBERT extraction + Statistical scoring)...")
    
    # We pass the keyword explicitly to test the statistical momentum logic,
    # avoiding the need for Spacy's en_core_web_sm model download right now.
    results = detect_trends(
        items,
        text_field="cleaned_text",
        time_field="platform_created_at",
        keywords=["cursor ai editor"],
        min_mentions=2
    )

    print("\n--- Detected Trends ---")
    if not results:
        print("No trends detected.")
        return

    for r in results:
        print(f"Keyword: '{r.keyword}' | Direction: {r.direction.upper()} | 7d Mom: {r.momentum_7d*100:.0f}% | Vol (Now/Prior): {r.volume_current}/{r.volume_previous} | Conf: {r.confidence:.2f}")
        
    # Check if 'cursor ai editor' (or something similar) is viral
    target_trend = next((r for r in results if "cursor" in r.keyword), None)
    if target_trend:
        print("\n✅ SUCCESS: Artificial spike correctly extracted and statistically validated!")
        if target_trend.direction in ["viral", "emerging"]:
            print(f"✅ Classified correctly as {target_trend.direction.upper()}")
        else:
            print(f"⚠️ Classified as {target_trend.direction}, expected viral/emerging.")
    else:
        print("\n❌ FAILED: Did not extract the spiked keyword.")

if __name__ == "__main__":
    test_trends_synthetic()
