"""Statistical trend detection pipeline using TF-IDF n-grams (Hybrid Step 1).

This module provides:
1. `extract_candidates_tfidf(texts)`: Extract frequent n-grams from corpus.
2. `detect_trends(items, keywords)`: Compute trend metrics for given keywords.

Designed to be used with an LLM refiner in `trend_agent.py`.
"""

import logging
import re
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np
import spacy
from keybert import KeyBERT
from scipy import stats
from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger(__name__)

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


# ── Text cleaning ──────────────────────────────────────────────────────

_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_SPECIAL_CHARS_RE = re.compile(r"[^\w\s'-]")  # keep apostrophes & hyphens
_MULTI_SPACE_RE = re.compile(r"\s{2,}")

# Platform boilerplate phrases that pollute TF-IDF
# These are fragments from Reddit bots, YouTube descriptions, Twitter UI, etc.
_BOILERPLATE_PHRASES = [
    # Reddit bot/mod boilerplate
    "subreddit message compose",
    "message compose",
    "performed automatically",
    "contact moderators",
    "action performed",
    "bot action",
    "moderator action",
    "reddit moderator",
    "automoderator",
    "submission statement",
    "removed submission",
    "flair submission",
    "report spam",
    "upvote downvote",
    "crosspost subreddit",
    "original poster",
    "comment thread",
    "reply comment",
    "removed comment",
    "deleted comment",
    "subreddit rules",
    "community guidelines",
    # YouTube boilerplate
    "subscribe channel",
    "like subscribe",
    "click link",
    "link description",
    "check link",
    "description below",
    "comment section",
    "notification bell",
    "watch video",
    "video description",
    # Twitter/X boilerplate
    "retweet like",
    "follow account",
    "twitter thread",
    # Generic web noise
    "click here",
    "read more",
    "learn more",
    "sign up",
    "free trial",
    "limited time",
    "check out",
    "don forget",
    "make sure",
    "let know",
    "feel free",
    "want make",
    "going make",
    "need know",
    "want know",
    "things need",
    "things know",
    "lot people",
    "people think",
    "pretty good",
    "really good",
    "looks like",
]

# Single words that should never appear as standalone trend keywords
# Single words that should never appear as standalone trend keywords
_JUNK_SINGLE_WORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
    "its", "let", "may", "new", "now", "old", "see", "way", "who", "did",
    "got", "just", "like", "make", "use", "using", "used", "best", "good",
    "really", "actually", "basically", "literally", "probably", "definitely",
    "thing", "things", "stuff", "people", "time", "going", "want", "need",
    "look", "looking", "think", "thought", "right", "well", "long", "term",
    "this", "that", "those", "these", "there", "here", "where", "when",
    "what", "why", "how", "with", "from", "into", "onto", "upon", "within",
    "without", "about", "above", "below", "under", "over", "after", "before",
    "since", "until", "while", "during", "through", "across", "along",
    "against", "among", "between", "around", "behind", "beyond", "inside",
    "outside", "near", "next", "down", "left", "right", "front", "back", "top",
    "bottom", "side", "high", "low", "hard", "soft", "easy", "believe",
    "understand", "know", "mean", "say", "said", "says", "told", "tell",
    "ask", "asked", "answer", "question", "problem", "issue", "point",
    "case", "fact", "idea", "part", "place", "area", "room", "world",
    "group", "state", "year", "month", "week", "hour", "minute", "second",
    "today", "yesterday", "tomorrow", "tonight", "morning", "afternoon",
    "evening", "night", "home", "work", "school", "office", "shop", "store",
    "instead", "rather", "quite", "very", "much", "many", "more", "most",
    "less", "least", "few", "fewer", "fewest", "own", "other", "another",
    "each", "every", "either", "neither", "both", "link", "url", "video",
    "channel", "post", "comment", "reply", "share", "subscribe", "follow",
    "retweet", "upvote", "downvote", "vote", "karma", "award", "gold",
    "silver", "platinum", "points", "score", "views", "likes", "dislikes",
    "stats", "analytics", "metrics", "data", "info", "information",
    "details", "description", "title", "subject", "message", "body", "text",
}


def clean_text(text: str) -> str:
    """Strip URLs, emails, HTML entities, and excess whitespace."""
    text = _URL_RE.sub("", text)
    text = _SPECIAL_CHARS_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    return text.strip().lower()


def _is_junk_phrase(phrase: str) -> bool:
    """Check if a candidate phrase is boilerplate or meaningless."""
    phrase_lower = phrase.lower().strip()
    words = phrase_lower.split()
    
    if not words:
        return True

    # 1. Reject if ALL words in the phrase are generic junk
    if all(w in _JUNK_SINGLE_WORDS for w in words):
        return True

    # 2. Reject if starts or ends with a pure stopword (e.g., "in ai", "ai for")
    # Exception: "ai agent" -> agent is not a stopword, so this passes.
    # Exception: "generative ai" -> generative is not a stopword.
    # Bad: "with ai" -> 'with' is stopword, 'ai' is not. 
    # Logic: If start word is stopword OR end word is stopword, it's usually a fragment.
    # NOTE: Be careful, "best ai tools" starts with 'best' (junk). 
    # Refined: If starts with a preposition/conjunction-like stopword.
    
    start_stops = {
        "the", "a", "an", "and", "or", "but", "if", "so", "because", "as",
        "of", "at", "by", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below",
        "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "can", "will", "just", "don", "should",
        "now", "this", "that", "these", "those", "instead", "hard", "easy",
    }
    
    end_stops = {
         "the", "a", "an", "and", "or", "but", "if", "so", "because", "as",
        "of", "at", "by", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below",
        "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
        "again", "further", "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "can", "will", "just", "don", "should",
        "now", "this", "that", "these", "those", "is", "was", "are", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "believe", "think", "know", "want", "need", "like", "use",
    }

    if words[0] in start_stops or words[-1] in end_stops:
        return True

    # Check against known boilerplate
    for bp in _BOILERPLATE_PHRASES:
        if bp in phrase_lower or phrase_lower in bp:
            return True
    
    # Reject very short phrases (less than 4 chars total)
    if len(phrase_lower.replace(" ", "")) < 4:
        return True
    
    return False


# ── Core TF-IDF Extraction ─────────────────────────────────────────────

# ── Core Semantic Extraction (KeyBERT + SpaCy) ─────────────────────

# Global lazy loaders
_SPACY_NLP = None
_KEYBERT_MODEL = None

def _get_spacy():
    global _SPACY_NLP
    if _SPACY_NLP is None:
        try:
            _SPACY_NLP = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        except OSError:
            logger.warning("Spacy model 'en_core_web_sm' not found. Download it via: python -m spacy download en_core_web_sm. Using blank English model.")
            _SPACY_NLP = spacy.blank("en")
    return _SPACY_NLP

def _get_keybert():
    global _KEYBERT_MODEL
    if _KEYBERT_MODEL is None:
        # Load small efficient model
        _KEYBERT_MODEL = KeyBERT(model="all-MiniLM-L6-v2")
    return _KEYBERT_MODEL


def extract_candidates_semantic(texts: list[str], top_n: int = 50) -> list[str]:
    """
    Extract meaningful trend candidates using KeyBERT + POS filtering.
    
    1. POS Filtering: Only allow Noun Phrases (Noun+Noun, Adjective+Noun, etc.)
       This eliminates "this is", "instead of", "hard to believe" naturally.
    2. KeyBERT: Rank phrases by semantic similarity to the corpus.
    """
    if not texts:
        return []

    try:
        nlp = _get_spacy()
        kw_model = _get_keybert()
        
        # Combine texts into one large document for extraction context
        full_text = " ".join(texts)
        
        # 1. Custom Candidate Selection (POS Constraints)
        # We only want n-grams that match specific POS patterns
        def candidate_selection(text):
            doc = nlp(text)
            candidates = set()
            
            for token in doc:
                # Bigrams/Trigrams check
                if token.pos_ in ["NOUN", "PROPN", "ADJ"]:
                    # Look ahead for simple Noun Phrases
                    # Example: "artificial intelligence" (ADJ + NOUN)
                    # "machine learning" (NOUN + NOUN)
                    # "new sora model" (ADJ + PROPN + NOUN)
                    pass 
            
            # Use CountVectorizer with a custom vocabulary from SpaCy would be slow.
            # Instead, let KeyBERT generate n-grams but we filter them.
            return [] 

        # Efficient Hybrid Approach:
        # Let KeyBERT generate n-grams (1-2 words), then filter strictly by POS.
        
        vectorizer = CountVectorizer(
            ngram_range=(2, 3), 
            stop_words="english"
        )
        
        # Extract keywords
        keywords = kw_model.extract_keywords(
            full_text, 
            vectorizer=vectorizer,
            keyphrase_ngram_range=(2, 3), 
            stop_words='english', 
            top_n=top_n * 3  # Over-fetch because we will filter
        )
        
        # Filter Semantic Junk using SpaCy POS tags
        # Only accept phrases that start/end with valid content words
        valid_candidates = []
        for phrase, score in keywords:
            doc = nlp(phrase)
            
            # REJECT if it contains a verb, pronoun, or determiner (unless it's a known entity)
            if any(t.pos_ in ["VERB", "PRON", "DET", "CCONJ", "ADP", "ADV"] for t in doc):
                continue
                
            # ACCEPT only if it ends with a Noun/Propn
            if doc[-1].pos_ not in ["NOUN", "PROPN"]:
                continue
            
            if not _is_junk_phrase(phrase):
                valid_candidates.append(phrase)
                
            if len(valid_candidates) >= top_n:
                break
                
        return valid_candidates

    except Exception as e:
        logger.error(f"Semantic extraction failed: {e}", exc_info=True)
        # Fallback to TF-IDF if ML fails
        return extract_candidates_tfidf(texts, top_n)


def extract_candidates_tfidf(texts: list[str], top_n: int = 50) -> list[str]:
    """Deprecated: Legacy TF-IDF extractor. Use extract_candidates_semantic instead."""
    # (Existing implementation kept as fallback)
    if not texts:
        return []

    try:
        custom_stop = list(_JUNK_SINGLE_WORDS)
        vec = CountVectorizer( # Switched to CountVectorizer for simplicity in fallback
            ngram_range=(2, 3),
            max_features=1000,
            stop_words=custom_stop,
            min_df=2,
            token_pattern=r"(?u)\\b[a-zA-Z][a-zA-Z]+\\b",
        )
        X = vec.fit_transform(texts)
        scores = X.sum(axis=0).A1
        feature_names = vec.get_feature_names_out()
        ranked = sorted(zip(feature_names, scores), key=lambda x: -x[1])
        
        filtered = []
        for term, score in ranked:
            if not _is_junk_phrase(term):
                filtered.append(term)
            if len(filtered) >= top_n:
                break
        return filtered
    except Exception:
        return []


def detect_trends(
    items: list[dict],
    text_field: str = "text",
    time_field: str = "created_at",
    niche_keywords: list[str] | None = None,
    keywords: list[str] | None = None,
    min_mentions: int | None = None,
) -> list[TrendResult]:
    """
    Detect trending keywords using Hybrid TF-IDF + Stats approach.
    
    Args:
        items: List of dictionaries containing text and timestamp
        text_field: Key for text content
        time_field: Key for timestamp
        niche_keywords: User's niche interests (for relevance scoring)
        keywords: Pre-defined keywords to analyze (if None, will extract via TF-IDF)
        min_mentions: Minimum mentions to qualify
    """
    if not items:
        return []

    logger.info(f"Detecting trends in {len(items)} items")

    # 1. Clean texts for processing
    clean_texts = []
    for item in items:
        raw = item.get(text_field) or ""
        if len(raw) > 10:
            clean_texts.append(clean_text(raw))

    # 2. Extract Candidates (if keywords not provided)
    # 2. Extract Candidates (if keywords not provided)
    if keywords is None:
        # Use new Semantic Extraction (KeyBERT + POS)
        candidates = extract_candidates_semantic(clean_texts, top_n=50)
        logger.info(f"Semantic candidates: {candidates[:10]}")
        keywords = candidates

    # B. Always include niche keywords if provided
    current_kws = list(keywords) if keywords else []
    if niche_keywords:
        seen = {k.lower() for k in current_kws}
        for nk in niche_keywords:
            if nk.lower() not in seen:
                current_kws.append(nk)
                seen.add(nk.lower())
    
    keywords = current_kws

    # 3. Compute Metrics (Momentum, Z-Score, Volume)
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)
    
    # Pre-compute engagement map (log-scaled)
    engagement_map = {}
    for idx, item in enumerate(items):
        eng = item.get("engagement", 0)
        engagement_map[idx] = np.log1p(eng) if eng > 0 else 0.0

    results: list[TrendResult] = []
    
    # Analyze each keyword
    for keyword in keywords:
        kw_lower = keyword.lower()
        
        current_7d = 0
        previous_7d = 0
        current_30d = 0
        previous_30d = 0
        daily_counts = defaultdict(int)
        total_engagement = 0.0
        mention_count = 0
        
        # Scan corpus for matches
        for idx, text in enumerate(clean_texts):
            if kw_lower in text:
                mention_count += 1
                total_engagement += engagement_map.get(idx, 0.0)
                
                # Timestamp logic
                item = items[idx]
                ts_raw = item.get(time_field)
                if not ts_raw: 
                    continue
                    
                try:
                    if isinstance(ts_raw, str):
                        ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00")).replace(tzinfo=None)
                    elif isinstance(ts_raw, datetime):
                        ts = ts_raw.replace(tzinfo=None)
                    else:
                        continue
                except Exception:
                    continue

                daily_counts[ts.strftime("%Y-%m-%d")] += 1
                
                if ts >= week_ago:
                    current_7d += 1
                elif ts >= week_ago - timedelta(days=7):
                    previous_7d += 1
                    
                if ts >= month_ago:
                    current_30d += 1
                elif ts >= two_months_ago:
                    previous_30d += 1

        if mention_count < (min_mentions or max(2, len(items) // 500)):
            continue

        # Calculate Stats
        momentum_7d = (current_7d / max(previous_7d, 1)) - 1.0
        momentum_30d = (current_30d / max(previous_30d, 1)) - 1.0
        
        daily_vals = list(daily_counts.values())
        z_score = 0.0
        if len(daily_vals) >= 3:
             z_score = float(stats.zscore(daily_vals)[-1]) if len(daily_vals) > 1 else 0.0

        # Classification
        if momentum_7d > 1.0 and current_7d > 5:
            direction = "viral"
        elif momentum_7d > 0.5:
            direction = "emerging"
        elif momentum_7d < -0.2:
            direction = "declining"
        else:
            direction = "stable"

        # Niche relevance
        niche_rel = 0.0
        if niche_keywords:
            if any(n.lower() in kw_lower for n in niche_keywords):
                niche_rel = 1.0
            elif any(kw_lower in n.lower() for n in niche_keywords):
                niche_rel = 0.8

        # Confidence Score
        avg_eng = total_engagement / max(mention_count, 1)
        confidence = (
            0.4 * min(current_7d / 20.0, 1.0) +
            0.3 * min(avg_eng / 5.0, 1.0) +
            0.3 * niche_rel
        )

        results.append(TrendResult(
            keyword=keyword,
            direction=direction,
            momentum_7d=round(momentum_7d, 2),
            momentum_30d=round(momentum_30d, 2),
            volume_current=current_7d,
            volume_previous=previous_7d,
            z_score=round(z_score, 2),
            confidence=round(confidence, 2),
            engagement_score=round(avg_eng, 2),
            niche_relevance=round(niche_rel, 2)
        ))

    # Sort and return
    results.sort(key=lambda x: x.confidence, reverse=True)
    return results
