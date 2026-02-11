"""Text cleaning and normalization pipeline."""

import re
import unicodedata
import logging
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CleanedText:
    """Result of text cleaning."""
    text: str
    urls: list[str]
    mentions: list[str]
    hashtags: list[str]
    language: str
    original_length: int
    cleaned_length: int


# Regex patterns
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
MENTION_PATTERN = re.compile(r'@(\w+)')
HASHTAG_PATTERN = re.compile(r'#(\w+)')
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)
WHITESPACE_PATTERN = re.compile(r'\s+')


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    if "<" in text and ">" in text:
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ")
    return text


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters to NFKC form."""
    return unicodedata.normalize("NFKC", text)


def extract_urls(text: str) -> tuple[str, list[str]]:
    """Extract and remove URLs from text."""
    urls = URL_PATTERN.findall(text)
    cleaned = URL_PATTERN.sub(" ", text)
    return cleaned, urls


def extract_mentions(text: str) -> list[str]:
    """Extract @mentions from text."""
    return MENTION_PATTERN.findall(text)


def extract_hashtags(text: str) -> list[str]:
    """Extract #hashtags from text."""
    return HASHTAG_PATTERN.findall(text)


def detect_language(text: str) -> str:
    """Detect language of text. Returns 'unknown' on failure."""
    try:
        if len(text.strip()) < 10:
            return "unknown"
        return detect(text)
    except LangDetectException:
        return "unknown"


def clean_text(
    text: str,
    strip_urls: bool = True,
    strip_mentions: bool = False,
    strip_emojis: bool = False,
    lowercase: bool = False,
) -> CleanedText:
    """
    Full text cleaning pipeline.

    Args:
        text: Raw text input
        strip_urls: Remove URLs from text
        strip_mentions: Remove @mentions from text
        strip_emojis: Remove emoji characters
        lowercase: Convert to lowercase

    Returns:
        CleanedText with cleaned text and extracted metadata
    """
    if not text:
        return CleanedText(
            text="", urls=[], mentions=[], hashtags=[],
            language="unknown", original_length=0, cleaned_length=0,
        )

    original_length = len(text)

    # Step 1: Strip HTML
    cleaned = strip_html(text)

    # Step 2: Unicode normalization
    cleaned = normalize_unicode(cleaned)

    # Step 3: Extract metadata before removal
    mentions = extract_mentions(cleaned)
    hashtags = extract_hashtags(cleaned)

    # Step 4: URL extraction/removal
    urls: list[str] = []
    if strip_urls:
        cleaned, urls = extract_urls(cleaned)
    else:
        _, urls = extract_urls(cleaned)

    # Step 5: Optional mention removal
    if strip_mentions:
        cleaned = MENTION_PATTERN.sub(" ", cleaned)

    # Step 6: Optional emoji removal
    if strip_emojis:
        cleaned = EMOJI_PATTERN.sub(" ", cleaned)

    # Step 7: Collapse whitespace
    cleaned = WHITESPACE_PATTERN.sub(" ", cleaned).strip()

    # Step 8: Optional lowercase
    if lowercase:
        cleaned = cleaned.lower()

    # Step 9: Language detection
    language = detect_language(cleaned)

    return CleanedText(
        text=cleaned,
        urls=urls,
        mentions=mentions,
        hashtags=hashtags,
        language=language,
        original_length=original_length,
        cleaned_length=len(cleaned),
    )


def clean_batch(texts: list[str], **kwargs) -> list[CleanedText]:
    """Clean a batch of texts."""
    return [clean_text(t, **kwargs) for t in texts]
