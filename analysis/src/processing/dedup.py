"""Content deduplication via SHA-256 hash fingerprinting."""

import hashlib
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DedupResult:
    """Deduplication result for a batch."""
    unique_items: list[dict]
    duplicate_count: int
    duplicate_hashes: list[str]


def content_hash(text: str, platform: str = "", platform_id: str = "") -> str:
    """
    Generate a SHA-256 content hash for deduplication.

    Uses normalized text + platform + platform_id to create a unique fingerprint.
    This ensures the same content from different platforms is treated separately.
    """
    normalized = text.strip().lower()
    fingerprint = f"{platform}:{platform_id}:{normalized}"
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()


def deduplicate_batch(
    items: list[dict],
    text_field: str = "text",
    platform_field: str = "platform",
    id_field: str = "platform_id",
) -> DedupResult:
    """
    Deduplicate a batch of items using content hashing.

    Args:
        items: List of content dicts
        text_field: Key for the text content
        platform_field: Key for platform name
        id_field: Key for platform-specific ID

    Returns:
        DedupResult with unique items and duplicate stats
    """
    seen_hashes: set[str] = set()
    unique_items: list[dict] = []
    duplicate_hashes: list[str] = []

    for item in items:
        text = item.get(text_field, "")
        platform = item.get(platform_field, "")
        platform_id = item.get(id_field, "")

        if not text:
            continue

        h = content_hash(text, platform, platform_id)
        item["content_hash"] = h

        if h in seen_hashes:
            duplicate_hashes.append(h)
            continue

        seen_hashes.add(h)
        unique_items.append(item)

    duplicate_count = len(items) - len(unique_items)
    if duplicate_count > 0:
        logger.info(f"Dedup: {len(items)} → {len(unique_items)} ({duplicate_count} duplicates)")

    return DedupResult(
        unique_items=unique_items,
        duplicate_count=duplicate_count,
        duplicate_hashes=duplicate_hashes,
    )
