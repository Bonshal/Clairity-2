import sys
import os
import logging

# Adjust path to find src
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.ml.trends import extract_candidates_semantic

def test_semantic_extraction():
    print("\n--- Testing Semantic Extraction (KeyBERT + SpaCy POS) ---\n")
    
    # 1. Sample Text with a mix of valid tech terms and junk phrases
    sample_texts = [
        "Artificial intelligence is transforming the world.",
        "Generative AI tools like ChatGPT are becoming popular.",
        "This is hard to believe but machine learning is cool.",
        "Click here to read more about the new update.",
        "Instead of using old methods, try deep learning models.",
        "The best way to do this is using neural networks.",
        "I want to know how to use large language models efficiently."
    ]
    
    print(f"Input Texts ({len(sample_texts)}):")
    for t in sample_texts:
        print(f"  - {t}")
        
    print("\nExtracting candidates...")
    
    # 2. Run Extraction
    candidates = extract_candidates_semantic(sample_texts, top_n=10)
    
    print(f"\nExtracted Candidates ({len(candidates)}):")
    for c in candidates:
        print(f"  - {c}")
        
    # 3. Verification Logic
    junk_phrases = ["this is", "hard to believe", "click here", "read more", "instead of", "best way", "want to know"]
    valid_terms = ["artificial intelligence", "generative ai", "machine learning", "neural networks", "deep learning", "large language models"]
    
    print("\nVerification:")
    
    # Check for Junk
    found_junk = [c for c in candidates if c in junk_phrases]
    if found_junk:
        print(f"❌ FAILED: Found junk phrases: {found_junk}")
    else:
        print("✅ SUCCESS: No known junk phrases found.")
        
    # Check for Valid Terms (some might be missed due to top_n, but we expect some)
    found_valid = [c for c in candidates if any(v in c for v in valid_terms)]
    if found_valid:
        print(f"✅ SUCCESS: Found valid technical terms: {found_valid}")
    else:
        print("⚠️ WARNING: Did not find expected technical terms. Check model performance.")

if __name__ == "__main__":
    test_semantic_extraction()
