"""Preprocessing Agent — clean, deduplicate, and embed content."""

import logging
from datetime import datetime, timezone

from src.state import PlatformState, CleanedDataRef, PlatformEnum
from src.processing.cleaner import clean_text
from src.processing.dedup import deduplicate_batch, content_hash
from src.processing.embeddings import generate_embeddings

logger = logging.getLogger(__name__)


async def preprocessing_agent(state: PlatformState) -> dict:
    """
    Agent 2: Clean, deduplicate, and generate embeddings.

    Reads: ingestion_metadata
    Writes: cleaned_data_refs, total_items_processed, total_embeddings_generated
    """
    logger.info("[Preprocessing Agent] Starting...")

    cleaned_refs: list[CleanedDataRef] = []
    total_processed = 0
    total_embeddings = 0

    for meta in state.ingestion_metadata:
        if meta.status == "failed" or meta.items_fetched == 0:
            continue

        platform = meta.platform
        logger.info(f"[Preprocessing] Processing {meta.items_fetched} items from {platform.value}")

        try:
            # Step 1: Normalize raw items into a common format
            normalized = _normalize_items(platform, meta.batch_id)

            # Step 2: Clean texts
            for item in normalized:
                text = item.get("text", "") or item.get("title", "") or ""
                cleaned = clean_text(text, strip_urls=True)
                item["cleaned_text"] = cleaned.text
                item["language"] = cleaned.language
                item["extracted_urls"] = cleaned.urls
                item["extracted_hashtags"] = cleaned.hashtags

            # Step 3: Deduplicate
            dedup_result = deduplicate_batch(
                normalized,
                text_field="cleaned_text",
                platform_field="platform",
                id_field="platform_id",
            )
            unique_items = dedup_result.unique_items

            # Step 4: Generate embeddings
            texts_for_embedding = [
                item.get("cleaned_text", "") for item in unique_items
                if item.get("cleaned_text", "").strip()
            ]

            embeddings = None
            if texts_for_embedding:
                embeddings = generate_embeddings(texts_for_embedding, batch_size=64)
                total_embeddings += len(embeddings)

            # TODO: Step 5 — Write to Neon content_items table with embeddings

            content_ids = [item.get("content_hash", "") for item in unique_items]

            cleaned_refs.append(CleanedDataRef(
                platform=platform,
                item_count=len(unique_items),
                content_ids=content_ids,
                embedding_count=len(texts_for_embedding),
            ))

            total_processed += len(unique_items)
            logger.info(
                f"[Preprocessing] {platform.value}: "
                f"{meta.items_fetched} fetched → {len(unique_items)} unique → "
                f"{len(texts_for_embedding)} embedded"
            )

        except Exception as e:
            logger.error(f"[Preprocessing] {platform.value} failed: {e}")

    logger.info(
        f"[Preprocessing Agent] Complete. "
        f"Processed: {total_processed}, Embeddings: {total_embeddings}"
    )

    return {
        "cleaned_data_refs": cleaned_refs,
        "total_items_processed": total_processed,
        "total_embeddings_generated": total_embeddings,
    }


def _normalize_items(platform: PlatformEnum, batch_id: str) -> list[dict]:
    """
    Normalize raw platform items into a common format.

    TODO: In production, this reads from MongoDB raw collections.
    For now, returns empty (items flow from ingestion_agent directly).
    """
    # This will be filled when we add the MongoDB → normalize pipeline
    return []
