"""Anomaly / virality detection using Isolation Forest."""

import logging
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Anomaly detection result for a single content item."""
    is_outlier: bool
    anomaly_score: float     # -1 (most anomalous) to 1 (most normal)
    features: dict[str, float]


def detect_anomalies(
    items: list[dict],
    contamination: float = 0.05,
) -> list[AnomalyResult]:
    """
    Detect viral outliers using Isolation Forest on engagement metrics.

    Args:
        items: List of content dicts with engagement metrics
        contamination: Expected proportion of outliers (default 5%)

    Returns:
        List of AnomalyResult objects (one per input item)
    """
    if not items:
        return []

    logger.info(f"Running anomaly detection on {len(items)} items (contamination={contamination})")

    # Extract feature matrix
    features_list = []
    for item in items:
        features = _extract_features(item)
        features_list.append(features)

    # Build feature matrix
    feature_names = list(features_list[0].keys())
    X = np.array([[f[k] for k in feature_names] for f in features_list])

    # Handle edge case: too few items
    if len(X) < 10:
        logger.warning(f"Too few items ({len(X)}) for reliable anomaly detection")
        return [
            AnomalyResult(is_outlier=False, anomaly_score=0.0, features=f)
            for f in features_list
        ]

    # Fit Isolation Forest
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
    )

    predictions = model.fit_predict(X)
    scores = model.score_samples(X)

    results: list[AnomalyResult] = []
    for i, (pred, score, features) in enumerate(zip(predictions, scores, features_list)):
        results.append(AnomalyResult(
            is_outlier=bool(pred == -1),
            anomaly_score=round(float(score), 4),
            features=features,
        ))

    outlier_count = sum(1 for r in results if r.is_outlier)
    logger.info(f"Detected {outlier_count} outliers out of {len(results)} items")

    return results


def _extract_features(item: dict) -> dict[str, float]:
    """Extract engagement features from a content item."""
    likes = float(item.get("likes", 0) or 0)
    views = float(item.get("views", 0) or 0)
    comments = float(item.get("comments_count", item.get("comments", 0)) or 0)
    shares = float(item.get("shares", item.get("retweets", 0)) or 0)

    # Derived ratios (avoid division by zero)
    engagement_rate = (likes + comments + shares) / max(views, 1)
    like_comment_ratio = likes / max(comments, 1)
    share_rate = shares / max(views, 1)

    return {
        "likes": likes,
        "views": views,
        "comments": comments,
        "shares": shares,
        "engagement_rate": engagement_rate,
        "like_comment_ratio": like_comment_ratio,
        "share_rate": share_rate,
    }


def get_top_outliers(
    items: list[dict],
    results: list[AnomalyResult],
    top_n: int = 10,
) -> list[dict]:
    """Get the top N most anomalous items."""
    outlier_pairs = [
        (item, result) for item, result in zip(items, results)
        if result.is_outlier
    ]

    # Sort by anomaly score (most negative = most anomalous)
    outlier_pairs.sort(key=lambda x: x[1].anomaly_score)

    return [
        {**item, "anomaly_score": result.anomaly_score, "anomaly_features": result.features}
        for item, result in outlier_pairs[:top_n]
    ]
