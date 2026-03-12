import os
import sys
from collections import Counter
from unittest.mock import patch

# Adjust path to find src
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.llm.wrapper import get_random_api_key

def test_distribution():
    print("Testing API Key Distribution...")
    
    # Mock environment with two distinct keys
    mock_keys = "key_A, key_B"
    
    # We patch os.environ to simulate the user setting GEMINI_API_KEYS
    with patch.dict(os.environ, {"GEMINI_API_KEYS": mock_keys, "GOOGLE_API_KEY": "fallback_key"}):
        
        counts = Counter()
        for _ in range(100):
            key = get_random_api_key()
            counts[key] += 1
            
        print(f"Distribution over 100 calls: {counts}")
        
        # Verify both keys are used roughly equally (random distribution)
        if len(counts) == 2 and "key_A" in counts and "key_B" in counts:
            if 40 <= counts["key_A"] <= 60:
                print("SUCCESS: Keys distributed approximately evenly.")
            else:
                print("WARNING: Keys distributed but variance is high (this can happen randomly).")
        else:
            print(f"FAILURE: Did not distribute as expected. Got keys: {list(counts.keys())}")

if __name__ == "__main__":
    test_distribution()
