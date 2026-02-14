"""Preprocessing Agent — clean, deduplicate, and embed content."""

import logging
import uuid
from datetime import datetime, timezone

from src.state import PlatformState, CleanedDataRef, PlatformEnum
from src.processing.cleaner import clean_text
from src.processing.dedup import deduplicate_batch
from src.processing.embeddings import generate_embeddings
from src.processing.normalization import (
    normalize_twitter_data,
    normalize_youtube_data,
    normalize_reddit_data,
)
from src.db.mongo import fetch_raw_data
from src.db.neon import async_session, ContentItemModel, log_pipeline_step

logger = logging.getLogger(__name__)


async def preprocessing_agent(state: PlatformState) -> dict:
    """
    Agent 2: Clean, deduplicate, and generate embeddings.

    Reads: ingestion_metadata
    Writes: cleaned_data_refs, total_items_processed, total_embeddings_generated
    """
    logger.info("[Preprocessing Agent] Starting...")
    await log_pipeline_step(state.run_id, "Preprocessing", "running", "Cleaning, deduplicating, and embedding content...")

    cleaned_refs: list[CleanedDataRef] = []
    total_processed = 0
    total_embeddings = 0

    for meta in state.ingestion_metadata:
        if meta.status == "failed" or meta.items_fetched == 0:
            continue

        platform = meta.platform
        batch_id = meta.batch_id
        logger.info(f"[Preprocessing] Processing batch {batch_id} from {platform.value}")
        await log_pipeline_step(state.run_id, "Preprocessing", "info", f"Processing {platform.value} data...")

        try:
            # Step 1: Fetch raw data from MongoDB
            raw_items = []
            if platform == PlatformEnum.TWITTER:
                raw_items = await fetch_raw_data("raw_twitter_tweets", batch_id)
            elif platform == PlatformEnum.YOUTUBE:
                raw_items = await fetch_raw_data("raw_youtube_videos", batch_id)
            elif platform == PlatformEnum.REDDIT:
                raw_items = await fetch_raw_data("raw_reddit_posts", batch_id)

            if not raw_items:
                logger.warning(f"[Preprocessing] No raw items found for batch {batch_id}")
                continue

            # Step 2: Normalize
            normalized = []
            if platform == PlatformEnum.TWITTER:
                normalized = normalize_twitter_data(raw_items)
            elif platform == PlatformEnum.YOUTUBE:
                normalized = normalize_youtube_data(raw_items)
            elif platform == PlatformEnum.REDDIT:
                normalized = normalize_reddit_data(raw_items)

            # Step 3: Clean texts
            for item in normalized:
                text = item.get("text", "") or item.get("title", "") or ""
                cleaned = clean_text(text, strip_urls=True)
                item["cleaned_text"] = cleaned.text
                item["language"] = cleaned.language
                item["extracted_urls"] = cleaned.urls
                item["extracted_hashtags"] = cleaned.hashtags

            # Step 4: Deduplicate
            dedup_result = deduplicate_batch(
                normalized,
                text_field="cleaned_text",
                platform_field="platform",
                id_field="platform_id",
            )
            unique_items = dedup_result.unique_items
            await log_pipeline_step(state.run_id, "Preprocessing", "info", f"{platform.value}: {len(unique_items)} unique items (after dedup)")

            # Step 5: Generate embeddings
            texts_for_embedding = []
            original_indices = []
            
            for idx, item in enumerate(unique_items):
                txt = item.get("cleaned_text", "").strip()
                if txt:
                    texts_for_embedding.append(txt)
                    original_indices.append(idx)

            embeddings_list = []
            if texts_for_embedding:
                embeddings_result = generate_embeddings(texts_for_embedding, batch_size=64)
                embeddings_list = [e.tolist() for e in embeddings_result]
                total_embeddings += len(embeddings_list)

            # Map back to full list (None for empty texts)
            full_embeddings = [None] * len(unique_items)
            for i, original_idx in enumerate(original_indices):
                full_embeddings[original_idx] = embeddings_list[i]

            # Step 6: Write to Neon content_items table
            content_ids = []
            async with async_session() as session:
                for i, item in enumerate(unique_items):
                    emb = full_embeddings[i]
                    
                    try:
                        content_item = ContentItemModel(
                            id=uuid.uuid4(),
                            platform=item["platform"],
                            platform_id=str(item["platform_id"]),
                            content_type=item["content_type"],
                            title=item.get("title"),
                            body=item.get("body"),
                            author=item.get("author"),
                            url=item.get("url"),
                            content_hash=item["content_hash"],
                            language=item.get("language", "en"),
                            upvotes=item.get("upvotes", 0),
                            likes=item.get("likes", 0),
                            views=item.get("views", 0),
                            comments_count=item.get("comments_count", 0),
                            shares=item.get("shares", 0),
                            fetched_at=datetime.now(timezone.utc),
                            processed_at=datetime.now(timezone.utc),
                            batch_id=batch_id,
                            embedding=emb,
                        )
                        session.add(content_item)
                        await session.commit()
                        content_ids.append(str(content_item.id))
                    except Exception as e:
                        await session.rollback()
                        if "unique constraint" in str(e).lower():
                            # Fetch existing ID if duplicate
                            # TODO: handle fetching existing ID to add to content_ids?
                            # For now, just skip adding to this run's processed list
                            pass
                        else:
                            logger.error(f"Failed to insert item {i}: {e}")

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
            logger.error(f"[Preprocessing] {platform.value} batch {batch_id} failed: {e}")
            await log_pipeline_step(state.run_id, "Preprocessing", "error", f"Error processing {platform.value}: {e}")
            import traceback
            traceback.print_exc()

    logger.info(
        f"[Preprocessing Agent] Complete. "
        f"Processed: {total_processed}, Embeddings: {total_embeddings}"
    )
    await log_pipeline_step(state.run_id, "Preprocessing", "completed", f"Preprocessing complete. {total_processed} items ready.")

    return {
        "cleaned_data_refs": cleaned_refs,
        "total_items_processed": total_processed,
        "total_embeddings_generated": total_embeddings,
    }
