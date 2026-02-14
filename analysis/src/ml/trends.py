"""Statistical trend detection pipeline.

CHANGELOG:
  2026-02-14 v2: Replaced TF-IDF with KeyBERT + spaCy.
    - KeyBERT (BERT embeddings) ranks candidates by semantic relevance.
    - spaCy noun-chunk extraction guarantees only nouns/noun-phrases
      survive — verbs like "use", contractions like "don't", and
      adjectives like "real" are structurally impossible.
    - Text cleaning strips URLs, emails, HTML entities before extraction.
  2026-02-14 v1: Initial rewrite from regex to TF-IDF n-grams.
"""

import logging
import re
from dataclasses import dataclass
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

# ── Lazy-loaded singletons (heavy models loaded once) ──────────────────
_keybert_model = None
_spacy_nlp = None


def _get_keybert():
    """Lazy-load KeyBERT with the lightweight MiniLM model."""
    global _keybert_model
    if _keybert_model is None:
        from keybert import KeyBERT
        _keybert_model = KeyBERT(model="all-MiniLM-L6-v2")
        logger.info("KeyBERT model loaded (all-MiniLM-L6-v2)")
    return _keybert_model


def _get_spacy():
    """Lazy-load spaCy with the small English model."""
    global _spacy_nlp
    if _spacy_nlp is None:
        import spacy
        _spacy_nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
        logger.info("spaCy model loaded (en_core_web_sm)")
    return _spacy_nlp


@dataclass
class TrendResult:
    """Detected trend signal."""
    keyword: str
    direction: str        # 'emerging', 'declining', 'stable', 'viral'
    momentum_7d: float    # 7-day momentum (ratio vs previous period)
    momentum_30d: float   # 30-day momentum (ratio vs previous period)
    volume_current: int   # Current period mention count
    volume_previous: int  # Previous period mention count
    z_score: float        # Statistical significance
    confidence: float     # 0-1 confidence score
    engagement_score: float = 0.0  # Weighted engagement for this trend
    niche_relevance: float = 0.0   # 0-1 how relevant to configured niche


def calculate_ema(values: list[float], span: int) -> list[float]:
    """Calculate Exponential Moving Average."""
    if not values:
        return []

    alpha = 2 / (span + 1)
    ema = [values[0]]
    for v in values[1:]:
        ema.append(alpha * v + (1 - alpha) * ema[-1])
    return ema


def detect_trends(
    items: list[dict],
    text_field: str = "text",
    time_field: str = "created_at",
    niche_keywords: list[str] | None = None,
    keywords: list[str] | None = None,
    min_mentions: int | None = None,
) -> list[TrendResult]:
    """
    Detect trending keywords from content items using statistical methods.

    Args:
        items: List of content dicts with text, timestamp, and engagement
        text_field: Key for text content
        time_field: Key for timestamp
        niche_keywords: Keywords from the user's Niche config — used to
                        filter/boost results and measure niche relevance
        keywords: Optional explicit list of keywords to track (skips extraction)
        min_mentions: Minimum mentions to qualify. If None, auto-scales with
                      corpus size (max(5, corpus_size // 20))

    Returns:
        List of TrendResult objects sorted by a composite score of
        momentum + engagement + niche relevance
    """
    if not items:
        return []

    logger.info(f"Detecting trends in {len(items)} items")

    # Dynamic min_mentions: scales with corpus size
    if min_mentions is None:
        min_mentions = max(5, len(items) // 20)
    logger.info(f"Using min_mentions={min_mentions} (corpus size: {len(items)})")

    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    # Extract keyphrases (bigrams/trigrams) if not provided
    if keywords is None:
        keywords = _auto_extract_keywords(
            items, text_field,
            min_count=min_mentions,
            niche_keywords=niche_keywords,
        )

    # Pre-compute engagement scores for each item
    engagement_map: dict[int, float] = {}
    for idx, item in enumerate(items):
        eng = item.get("engagement", 0)
        # Log-scale engagement to prevent a single viral post from dominating
        engagement_map[idx] = np.log1p(eng) if eng > 0 else 0.0

    # Normalize niche keywords for matching
    niche_set: set[str] = set()
    if niche_keywords:
        niche_set = {kw.lower().strip() for kw in niche_keywords}

    results: list[TrendResult] = []

    for keyword in keywords:
        keyword_lower = keyword.lower()

        current_7d = 0
        previous_7d = 0
        current_30d = 0
        previous_30d = 0
        daily_counts: dict[str, int] = defaultdict(int)
        total_engagement = 0.0
        mention_count = 0

        for idx, item in enumerate(items):
            text = (item.get(text_field) or "").lower()
            if keyword_lower not in text:
                continue

            mention_count += 1
            total_engagement += engagement_map.get(idx, 0.0)

            # Parse timestamp
            ts_raw = item.get(time_field)
            if ts_raw is None:
                continue

            if isinstance(ts_raw, str):
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).replace(tzinfo=None)
                except (ValueError, TypeError):
                    continue
            elif isinstance(ts_raw, datetime):
                ts = ts_raw.replace(tzinfo=None)
            else:
                continue

            day_key = ts.strftime("%Y-%m-%d")
            daily_counts[day_key] += 1

            if ts >= week_ago:
                current_7d += 1
            elif ts >= week_ago - timedelta(days=7):
                previous_7d += 1

            if ts >= month_ago:
                current_30d += 1
            elif ts >= two_months_ago:
                previous_30d += 1

        if mention_count < min_mentions:
            continue

        # Momentum: ratio of current vs previous (0 = no change, positive = growth)
        momentum_7d = (current_7d / max(previous_7d, 1)) - 1.0
        momentum_30d = (current_30d / max(previous_30d, 1)) - 1.0

        # Z-score for statistical significance of the trend
        daily_values = list(daily_counts.values())
        if len(daily_values) >= 3:
            z_score = float(stats.zscore(daily_values)[-1]) if len(daily_values) > 1 else 0.0
        else:
            z_score = 0.0

        # Direction classification with higher thresholds
        if z_score > 3.0 and momentum_7d > 2.0:
            direction = "viral"
        elif momentum_7d > 0.8:
            direction = "emerging"
        elif momentum_7d < -0.3:
            direction = "declining"
        else:
            direction = "stable"

        # Engagement score: average log-engagement per mention
        avg_engagement = total_engagement / max(mention_count, 1)

        # Niche relevance: how closely this keyword relates to configured niche
        niche_relevance = _compute_niche_relevance(keyword_lower, niche_set)

        # Confidence: composite of volume, statistical significance,
        #             engagement, and niche relevance
        volume_score = min(current_7d / max(50, min_mentions * 5), 1.0)
        z_score_normalized = min(abs(z_score) / 3.0, 1.0)
        engagement_normalized = min(avg_engagement / 5.0, 1.0)  # log(~150) ≈ 5

        confidence = (
            0.30 * volume_score +
            0.25 * z_score_normalized +
            0.25 * engagement_normalized +
            0.20 * niche_relevance
        )

        results.append(TrendResult(
            keyword=keyword,
            direction=direction,
            momentum_7d=round(momentum_7d, 3),
            momentum_30d=round(momentum_30d, 3),
            volume_current=current_7d,
            volume_previous=previous_7d,
            z_score=round(z_score, 3),
            confidence=round(confidence, 3),
            engagement_score=round(avg_engagement, 3),
            niche_relevance=round(niche_relevance, 3),
        ))

    # Sort by composite score: momentum + engagement + niche relevance
    results.sort(
        key=lambda r: (
            r.confidence * 0.4 +
            min(r.momentum_7d, 5.0) / 5.0 * 0.3 +
            r.niche_relevance * 0.3
        ),
        reverse=True,
    )

    # Filter: Only keep trends that are emerging/viral OR have high niche relevance
    results = [
        r for r in results
        if r.direction in ("emerging", "viral") or r.niche_relevance > 0.5
    ]

    viral = sum(1 for r in results if r.direction == "viral")
    emerging = sum(1 for r in results if r.direction == "emerging")
    declining = sum(1 for r in results if r.direction == "declining")
    logger.info(f"Trends: {viral} viral, {emerging} emerging, {declining} declining, {len(results)} total")

    return results


def _compute_niche_relevance(keyword: str, niche_set: set[str]) -> float:
    """
    Compute how relevant a detected keyword is to the user's niche.

    Returns 1.0 for exact match, 0.7 for partial overlap, 0.3 for weak overlap,
    0.0 for no connection.
    """
    if not niche_set:
        return 0.5  # No niche configured → neutral relevance

    keyword_words = set(keyword.split())

    for niche_kw in niche_set:
        niche_words = set(niche_kw.split())

        # Exact match
        if keyword == niche_kw:
            return 1.0

        # Keyword contains the niche keyword or vice versa
        if niche_kw in keyword or keyword in niche_kw:
            return 0.9

        # Word overlap
        overlap = keyword_words & niche_words
        if overlap:
            overlap_ratio = len(overlap) / max(len(keyword_words), len(niche_words))
            return max(0.5, overlap_ratio)

    return 0.0


# ── Text cleaning ──────────────────────────────────────────────────────

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
_HTML_ENTITY_RE = re.compile(r"&[a-zA-Z]+;|&#\d+;")
_SPECIAL_CHARS_RE = re.compile(r"[^\w\s'-]")  # keep apostrophes & hyphens
_MULTI_SPACE_RE = re.compile(r"\s{2,}")


def _clean_text(text: str) -> str:
    """Strip URLs, emails, HTML entities, and excess whitespace."""
    text = _URL_RE.sub("", text)
    text = _EMAIL_RE.sub("", text)
    text = _HTML_ENTITY_RE.sub("", text)
    text = _SPECIAL_CHARS_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    return text.strip()


# ── Noun-phrase candidate extraction via spaCy ─────────────────────────

def _extract_noun_candidates(texts: list[str]) -> list[str]:
    """
    Use spaCy to pull noun chunks and proper nouns from a corpus.

    This is the key quality gate: verbs ("use", "make"), auxiliaries
    ("don", "isn"), and adjectives ("real") are structurally impossible
    because we only keep NOUN and PROPN chunks.
    """
    nlp = _get_spacy()

    # Process in batches for efficiency
    candidates = Counter()
    for doc in nlp.pipe(texts, batch_size=64, n_process=1):
        # Noun chunks: "machine learning", "code review", "AI agents"
        for chunk in doc.noun_chunks:
            # Strip determiners and pronouns from the start
            span_text = chunk.text.lower().strip()
            # Remove leading articles/determiners
            words = span_text.split()
            while words and words[0] in {"a", "an", "the", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their", "some", "any", "no", "every"}:
                words = words[1:]
            cleaned = " ".join(words)
            if cleaned and len(cleaned) >= 3 and len(cleaned.split()) <= 4:
                candidates[cleaned] += 1

        # Also capture standalone proper nouns not in chunks
        for token in doc:
            if token.pos_ == "PROPN" and len(token.text) >= 2:
                candidates[token.text.lower()] += 1

    return candidates


# ── Main keyword extraction (KeyBERT + spaCy) ─────────────────────────

def _auto_extract_keywords(
    items: list[dict],
    text_field: str,
    min_count: int = 5,
    max_keywords: int = 80,
    niche_keywords: list[str] | None = None,
) -> list[str]:
    """
    Extract meaningful keyphrases using KeyBERT + spaCy noun-chunk filtering.

    Pipeline:
      1. Clean text (strip URLs, HTML entities, special chars)
      2. spaCy noun-chunk extraction → candidate phrases (nouns only)
      3. Frequency filter → keep candidates with >= min_count mentions
      4. KeyBERT semantic ranking → rank by relevance to the full corpus
      5. Niche keyword seeding → always include configured niche terms

    This guarantees verbs, adjectives, and junk tokens are structurally
    eliminated rather than relying on brittle blocklists.
    """
    # 1. Collect and clean texts
    texts = []
    for item in items:
        text = (item.get(text_field) or "").strip()
        if text and len(text) > 20:
            texts.append(_clean_text(text))

    if not texts:
        logger.warning("No texts available for keyword extraction")
        return list(niche_keywords) if niche_keywords else []

    logger.info(f"Extracting keywords from {len(texts)} cleaned texts")

    # 2. spaCy: extract noun-phrase candidates with frequency counts
    noun_counts = _extract_noun_candidates(texts)

    if not noun_counts:
        logger.warning("spaCy found no noun phrases")
        return list(niche_keywords) if niche_keywords else []

    # 3. Frequency filter: only keep phrases that appear enough
    min_freq = max(2, min_count // 2)  # half of min_mentions, at least 2
    frequent_nouns = [
        phrase for phrase, count in noun_counts.most_common(300)
        if count >= min_freq
    ]

    if not frequent_nouns:
        # Fall back to top-N by frequency without threshold
        frequent_nouns = [phrase for phrase, _ in noun_counts.most_common(50)]

    logger.info(f"spaCy found {len(noun_counts)} unique noun phrases, {len(frequent_nouns)} pass frequency filter (min_freq={min_freq})")

    # 4. KeyBERT: rank candidates by semantic relevance to the corpus
    try:
        kw_model = _get_keybert()

        # Combine all texts into one document for KeyBERT
        # (KeyBERT works best with a single document representing the "topic")
        combined = " ".join(texts[:200])  # cap at 200 texts to avoid memory issues

        # Use KeyBERT with our pre-filtered noun candidates as the vocabulary
        keybert_results = kw_model.extract_keywords(
            combined,
            candidates=frequent_nouns,
            top_n=max_keywords,
            use_mmr=True,       # Maximal Marginal Relevance for diversity
            diversity=0.5,      # Balance between relevance and diversity
        )

        keywords = [kw for kw, score in keybert_results if score > 0.05]
        logger.info(f"KeyBERT selected {len(keywords)} keywords (from {len(frequent_nouns)} candidates)")

    except Exception as e:
        logger.error(f"KeyBERT extraction failed, falling back to frequency: {e}")
        # Fallback: just use the most frequent noun phrases
        keywords = frequent_nouns[:max_keywords]

    # 5. Always include niche keywords as seeds
    if niche_keywords:
        existing_lower = {k.lower() for k in keywords}
        for nk in niche_keywords:
            if nk.lower() not in existing_lower:
                keywords.append(nk)

    logger.info(
        f"Final keyword list: {len(keywords)} keywords "
        f"(+{len(niche_keywords or [])} niche seeds)"
    )
    return keywords
