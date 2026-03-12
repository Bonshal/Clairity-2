"""
Benchmark: Compare 5 Trending Keyword Extraction Techniques
============================================================
Techniques tested (each used by credible companies/research):
  1. TF-IDF n-grams       — Google Trends style (relative term importance)
  2. YAKE                  — Unsupervised statistical (position + frequency + casing)
  3. RAKE                  — Graph-based (co-occurrence of content words)  
  4. KeyBERT              — BERT semantic ranking (used by Hugging Face ecosystem)
  5. BERTopic c-TF-IDF    — Topic cluster labels (used by research/BERTrend)

Each technique extracts top-20 keywords from the SAME corpus.
We then score them on 3 criteria:
  - Specificity: % multi-word phrases (2+ words) — more specific = better
  - Relevance: Average semantic similarity to niche keywords (cosine w/ MiniLM)
  - Junk rate: % of keywords that are generic/stop-like (manual heuristic check)

Usage: uv run python benchmark_trends.py
"""

import asyncio
import time
import logging
import re
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("benchmark")

# ── Data loading ───────────────────────────────────────────────────────

async def load_corpus() -> list[dict]:
    """Load content_items from Neon DB."""
    from src.db.neon import async_session
    from sqlalchemy import text

    items = []
    async with async_session() as session:
        r = await session.execute(text(
            "SELECT id, platform, title, body, likes, shares, comments_count "
            "FROM content_items ORDER BY fetched_at DESC LIMIT 2000"
        ))
        for row in r.fetchall():
            text_content = (row[3] or row[2] or "").strip()
            if len(text_content) > 20:
                items.append({
                    "text": text_content,
                    "platform": row[1],
                    "engagement": (row[4] or 0) + (row[5] or 0) + (row[6] or 0),
                })
    return items


# ── Text cleaning (shared) ────────────────────────────────────────────

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_SPECIAL = re.compile(r"[^\w\s'-]")
_MULTI_SPACE = re.compile(r"\s{2,}")

def clean(text: str) -> str:
    text = _URL_RE.sub("", text)
    text = _SPECIAL.sub(" ", text)
    text = _MULTI_SPACE.sub(" ", text)
    return text.strip().lower()


# ── Technique 1: TF-IDF bigrams/trigrams ───────────────────────────────

def extract_tfidf(texts: list[str], top_n: int = 20) -> list[str]:
    """Google Trends-inspired: TF-IDF on bigrams/trigrams."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    vec = TfidfVectorizer(
        ngram_range=(2, 3),       # only multi-word phrases
        max_features=500,
        stop_words="english",
        min_df=3,                 # must appear in 3+ docs
        max_df=0.7,               # ignore if in >70% of docs
    )
    X = vec.fit_transform(texts)
    
    # Sum TF-IDF scores across all documents for each term
    scores = X.sum(axis=0).A1
    feature_names = vec.get_feature_names_out()
    
    ranked = sorted(zip(feature_names, scores), key=lambda x: -x[1])
    return [term for term, _ in ranked[:top_n]]


# ── Technique 2: YAKE ─────────────────────────────────────────────────

def extract_yake(texts: list[str], top_n: int = 20) -> list[str]:
    """YAKE: Unsupervised statistical keyword extraction."""
    import yake

    combined = " ".join(texts[:300])  # YAKE works on single doc
    kw = yake.KeywordExtractor(
        lan="en",
        n=3,           # up to trigrams
        dedupLim=0.7,  # dedup threshold
        top=top_n * 2, # extract more, filter later
        features=None,
    )
    keywords = kw.extract_keywords(combined)
    # YAKE: lower score = more important
    return [kw for kw, score in keywords[:top_n]]


# ── Technique 3: RAKE ─────────────────────────────────────────────────

def extract_rake(texts: list[str], top_n: int = 20) -> list[str]:
    """RAKE: Rapid Automatic Keyword Extraction (graph-based)."""
    from rake_nltk import Rake

    r = Rake(
        min_length=2,   # minimum 2 words
        max_length=4,   # maximum 4 words
    )
    combined = " ".join(texts[:300])
    r.extract_keywords_from_text(combined)
    ranked = r.get_ranked_phrases()
    
    # Filter out very long/noisy phrases
    filtered = [p for p in ranked if len(p.split()) <= 4 and len(p) > 5]
    return filtered[:top_n]


# ── Technique 4: KeyBERT ───────────────────────────────────────────────

def extract_keybert(texts: list[str], top_n: int = 20) -> list[str]:
    """KeyBERT: BERT-based semantic keyword extraction."""
    from keybert import KeyBERT

    model = KeyBERT(model="all-MiniLM-L6-v2")
    combined = " ".join(texts[:200])
    
    keywords = model.extract_keywords(
        combined,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        top_n=top_n,
        use_mmr=True,
        diversity=0.5,
    )
    return [kw for kw, score in keywords]


# ── Technique 5: BERTopic c-TF-IDF ────────────────────────────────────

def extract_bertopic(texts: list[str], top_n: int = 20) -> list[str]:
    """BERTopic: Topic cluster labels via c-TF-IDF."""
    from bertopic import BERTopic

    model = BERTopic(
        nr_topics="auto",
        min_topic_size=5,
        verbose=False,
    )
    topics, _ = model.fit_transform(texts)
    
    # Extract labels from discovered topics
    topic_info = model.get_topic_info()
    keywords = []
    for _, row in topic_info.iterrows():
        tid = row["Topic"]
        if tid == -1:
            continue
        topic_words = model.get_topic(tid)
        if topic_words:
            # Use top 2-3 words as the label (like BERTopic does)
            label = " ".join([w for w, _ in topic_words[:3]])
            keywords.append(label)
    
    return keywords[:top_n]


# ── Evaluation metrics ────────────────────────────────────────────────

def compute_specificity(keywords: list[str]) -> float:
    """% of keywords that are multi-word (2+ words). Higher = better."""
    if not keywords:
        return 0.0
    multi = sum(1 for k in keywords if len(k.split()) >= 2)
    return multi / len(keywords)


# Generic junk words — used for automated junk detection
JUNK_WORDS = {
    "code", "model", "ai", "ml", "llm", "app", "tool", "data", "web",
    "use", "new", "best", "top", "good", "great", "real", "don", "doesn",
    "get", "make", "way", "lot", "time", "thing", "stuff", "kind",
    "people", "work", "need", "help", "want", "like", "know", "think",
    "look", "see", "try", "say", "go", "take", "come", "give",
}

def compute_junk_rate(keywords: list[str]) -> float:
    """% of keywords that are single generic/junk words. Lower = better."""
    if not keywords:
        return 0.0
    junk = 0
    for kw in keywords:
        words = kw.lower().split()
        if len(words) == 1 and words[0] in JUNK_WORDS:
            junk += 1
    return junk / len(keywords)


def compute_niche_relevance(keywords: list[str], niche_terms: list[str]) -> float:
    """Average semantic similarity of keywords to niche terms using MiniLM."""
    if not keywords or not niche_terms:
        return 0.0
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        kw_embeddings = model.encode(keywords)
        niche_embeddings = model.encode(niche_terms)
        
        # Cosine similarity
        import numpy as np
        kw_norm = kw_embeddings / np.linalg.norm(kw_embeddings, axis=1, keepdims=True)
        niche_norm = niche_embeddings / np.linalg.norm(niche_embeddings, axis=1, keepdims=True)
        
        similarity_matrix = kw_norm @ niche_norm.T
        # For each keyword, take max similarity to any niche term
        max_sims = similarity_matrix.max(axis=1)
        return float(np.mean(max_sims))
    except Exception as e:
        logger.warning(f"Could not compute niche relevance: {e}")
        return 0.0


# ── Main benchmark ────────────────────────────────────────────────────

async def main():
    print("=" * 70)
    print("TRENDING KEYWORD EXTRACTION — TECHNIQUE BENCHMARK")
    print("=" * 70)
    
    # Load data
    print("\n📦 Loading corpus from database...")
    items = await load_corpus()
    print(f"   Loaded {len(items)} items")
    
    texts = [clean(item["text"]) for item in items]
    
    # Define niche terms (from your niche config / what the platform is about)
    niche_terms = [
        "AI tools", "content creation", "market research",
        "social media analytics", "machine learning", 
        "competitor analysis", "trend detection",
        "startup", "SaaS", "automation",
    ]
    
    # Run each technique
    techniques = {
        "1. TF-IDF bigrams": extract_tfidf,
        "2. YAKE statistical": extract_yake,
        "3. RAKE graph-based": extract_rake,
        "4. KeyBERT semantic": extract_keybert,
        "5. BERTopic clusters": extract_bertopic,
    }
    
    results = {}
    
    for name, func in techniques.items():
        print(f"\n🔬 Running {name}...")
        try:
            t0 = time.time()
            keywords = func(texts)
            elapsed = time.time() - t0
            results[name] = {
                "keywords": keywords,
                "time": elapsed,
            }
            print(f"   ✅ Extracted {len(keywords)} keywords in {elapsed:.1f}s")
            print(f"   Top 10: {keywords[:10]}")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            results[name] = {"keywords": [], "time": 0, "error": str(e)}
    
    # Evaluate all
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)
    
    print(f"\n{'Technique':<25} {'Specificity':>12} {'Junk Rate':>12} {'Niche Sim':>12} {'Time':>8} {'Score':>8}")
    print("-" * 80)
    
    best_name = None
    best_score = -1
    
    for name, data in results.items():
        kws = data["keywords"]
        if not kws:
            print(f"{name:<25} {'FAILED':>12}")
            continue
            
        spec = compute_specificity(kws)
        junk = compute_junk_rate(kws)
        relevance = compute_niche_relevance(kws, niche_terms)
        elapsed = data["time"]
        
        # Composite score: maximize specificity + relevance, minimize junk
        score = (spec * 0.35) + (relevance * 0.35) + ((1 - junk) * 0.3)
        
        if score > best_score:
            best_score = score
            best_name = name
        
        print(f"{name:<25} {spec:>11.0%} {junk:>11.0%} {relevance:>11.2f} {elapsed:>7.1f}s {score:>7.2f}")
    
    print("-" * 80)
    print(f"\n🏆 WINNER: {best_name} (score: {best_score:.2f})")
    
    # Print full keyword lists for comparison
    print("\n" + "=" * 70)
    print("FULL KEYWORD LISTS")
    print("=" * 70)
    for name, data in results.items():
        print(f"\n--- {name} ---")
        for i, kw in enumerate(data.get("keywords", []), 1):
            print(f"  {i:2d}. {kw}")


if __name__ == "__main__":
    asyncio.run(main())
