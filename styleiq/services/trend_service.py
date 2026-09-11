"""
STYLEIQ Trend Intelligence Service
────────────────────────────────────
Detects, scores, and ranks fashion trends from real signals.

IMPORTANT: Every score is computed by Python math.
Claude is NOT used for scoring — only for reasoning later.

Scoring formula:
    Total = w1*Popularity + w2*Growth + w3*CrossBrand + w4*Seasonal
    Weights sum to 1.0 and are configurable.

Usage:
    from styleiq.services.trend_service import trend_service
    trends = trend_service.get_trending_now(top_n=5)
    report = trend_service.get_trend_report("chocolate-brown")
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from styleiq.database.connection import SessionLocal
from styleiq.database.models import Trend, TrendSignal, TrendScore
from styleiq.logger import get_logger

log = get_logger(__name__)


# ── Score weights (must sum to 1.0) ───────────────────────────────────────
TREND_SCORE_WEIGHTS = {
    "popularity":   0.30,   # raw frequency — how many brands/mentions
    "growth":       0.30,   # growth rate — is it accelerating?
    "cross_brand":  0.25,   # how many brands adopted it (breadth)
    "seasonal":     0.15,   # is it the right season?
}

SCORE_VERSION = "v1.0"

# ── Pakistani seasonal calendar ────────────────────────────────────────────
# Maps calendar month → peak seasons
MONTH_TO_SEASON = {
    1: "winter", 2: "winter",
    3: "spring", 4: "spring",
    5: "summer", 6: "summer", 7: "summer", 8: "summer",
    9: "transitional", 10: "transitional",
    11: "winter", 12: "winter",
}

# Which seasons are relevant for each trend season tag
SEASON_RELEVANCE = {
    "summer":       {"summer": 1.0, "spring": 0.6, "transitional": 0.3, "winter": 0.0},
    "winter":       {"winter": 1.0, "transitional": 0.6, "spring": 0.3, "summer": 0.0},
    "spring":       {"spring": 1.0, "summer": 0.5, "winter": 0.2, "transitional": 0.4},
    "transitional": {"transitional": 1.0, "spring": 0.7, "winter": 0.5, "summer": 0.3},
    "all":          {"summer": 1.0, "winter": 1.0, "spring": 1.0, "transitional": 1.0},
}


# ── Output data classes ────────────────────────────────────────────────────
@dataclass
class TrendScoreResult:
    """Full scored trend result with evidence."""
    trend_id:    str
    trend_name:  str
    category:    str
    status:      str
    season:      Optional[str]

    # Component scores (0–100)
    popularity_score:  float = 0.0
    growth_score:      float = 0.0
    cross_brand_score: float = 0.0
    seasonal_score:    float = 0.0
    total_score:       float = 0.0

    # Evidence
    signal_count:       int = 0
    brand_count:        float = 0.0
    growth_rate_pct:    Optional[float] = None
    supporting_signals: list[str] = field(default_factory=list)

    # Metadata
    score_version: str = SCORE_VERSION
    computed_at:   datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrendReport:
    """Full intelligence report for a single trend."""
    trend_id:    str
    name:        str
    category:    str
    status:      str
    description: Optional[str]
    season:      Optional[str]
    year:        Optional[int]

    # Score
    score:       Optional[TrendScoreResult] = None

    # Evidence summary
    total_signals:    int = 0
    signal_breakdown: dict = field(default_factory=dict)

    # Context
    status_explanation: str = ""
    trend_insight:      str = ""


# ── Scoring functions ──────────────────────────────────────────────────────
def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _compute_popularity_score(signals: list[TrendSignal]) -> tuple[float, str]:
    """
    How popular is this trend based on raw signal values?

    Method:
    - Sum all brand_appearance signal values
    - Apply log scaling so 1 brand ≠ 10 brands linearly
    - Normalize to 0–100
    """
    brand_signals = [s for s in signals if s.signal_type == "brand_appearance"]
    if not brand_signals:
        return 0.0, "No brand appearance data"

    total_brands = sum(s.signal_value for s in brand_signals)

    # Log scale: 1 brand=20, 5 brands=55, 10 brands=75, 15 brands=90, 20+=100
    if total_brands <= 0:
        score = 0.0
    else:
        score = min(100.0, (math.log(total_brands + 1) / math.log(21)) * 100)

    evidence = f"{int(total_brands)} brand appearances detected"
    return _clamp(score), evidence


def _compute_growth_score(signals: list[TrendSignal]) -> tuple[float, Optional[float], str]:
    """
    Is this trend accelerating or declining?

    Method:
    - Look for search_volume_growth signals (% growth rate)
    - Map growth rate to score: 0% = 50, 50% = 85, 100%+ = 100, negative = lower
    """
    growth_signals = [
        s for s in signals
        if s.signal_type in ("search_volume_growth", "growth_rate")
    ]

    if not growth_signals:
        return 50.0, None, "No growth data — neutral score applied"

    avg_growth = sum(s.signal_value for s in growth_signals) / len(growth_signals)

    # Map growth % to score
    # -50% growth → ~10 score
    # 0% growth   → 50 score
    # 30% growth  → 75 score
    # 50% growth  → 85 score
    # 100%+ growth → 100 score
    if avg_growth >= 100:
        score = 100.0
    elif avg_growth >= 0:
        score = 50.0 + (avg_growth / 100.0) * 50.0
    else:
        # Negative growth — declining trend
        score = max(0.0, 50.0 + avg_growth * 0.4)

    evidence = f"Average search growth: {avg_growth:+.1f}%"
    return _clamp(score), avg_growth, evidence


def _compute_cross_brand_score(signals: list[TrendSignal]) -> tuple[float, float, str]:
    """
    How broadly adopted is this trend across brand tiers?

    Method:
    - Count distinct brands from raw_data in brand_appearance signals
    - More brands = broader adoption = higher score
    - Normalize against Pakistani market size (~15 tracked brands)
    """
    brand_signals = [s for s in signals if s.signal_type == "brand_appearance"]
    if not brand_signals:
        return 0.0, 0.0, "No cross-brand data"

    # Extract brand lists from raw_data
    all_brands: set[str] = set()
    for sig in brand_signals:
        if sig.raw_data and "brands" in sig.raw_data:
            all_brands.update(sig.raw_data["brands"])
        else:
            # If no brand list, count signal value as brand count
            all_brands.update([f"brand_{i}" for i in range(int(sig.signal_value))])

    brand_count = len(all_brands)
    total_tracked = 15   # our current tracked brand universe

    # Score: 1 brand=10, 5 brands=45, 10 brands=75, 15 brands=100
    score = min(100.0, (brand_count / total_tracked) * 100.0)
    evidence = f"Adopted by {brand_count} brands"
    return _clamp(score), float(brand_count), evidence


def _compute_seasonal_score(trend: Trend) -> tuple[float, str]:
    """
    Is this trend seasonally relevant right now?

    Method:
    - Get current Pakistani season from month
    - Match against trend's season tag
    - Return relevance score
    """
    current_month = datetime.utcnow().month
    current_season = MONTH_TO_SEASON.get(current_month, "transitional")
    trend_season = (trend.season or "all").lower()

    relevance_map = SEASON_RELEVANCE.get(trend_season, SEASON_RELEVANCE["all"])
    relevance = relevance_map.get(current_season, 0.5)
    score = relevance * 100.0

    evidence = f"Trend season: {trend_season} | Current season: {current_season} | Relevance: {relevance:.0%}"
    return _clamp(score), evidence


# ── Main scoring function ──────────────────────────────────────────────────
def compute_trend_score(trend: Trend, signals: list[TrendSignal]) -> TrendScoreResult:
    """
    Compute a full trend score from all available signals.
    This is the core algorithm — pure Python, no LLM.
    """
    pop_score,    pop_evidence    = _compute_popularity_score(signals)
    grow_score,   growth_rate, grow_evidence  = _compute_growth_score(signals)
    cross_score,  brand_count,   cross_evidence = _compute_cross_brand_score(signals)
    season_score, season_evidence = _compute_seasonal_score(trend)

    # Weighted total
    total = (
        pop_score    * TREND_SCORE_WEIGHTS["popularity"] +
        grow_score   * TREND_SCORE_WEIGHTS["growth"] +
        cross_score  * TREND_SCORE_WEIGHTS["cross_brand"] +
        season_score * TREND_SCORE_WEIGHTS["seasonal"]
    )

    return TrendScoreResult(
        trend_id=trend.id,
        trend_name=trend.name,
        category=trend.category,
        status=trend.status,
        season=trend.season,
        popularity_score=round(pop_score, 1),
        growth_score=round(grow_score, 1),
        cross_brand_score=round(cross_score, 1),
        seasonal_score=round(season_score, 1),
        total_score=round(total, 1),
        signal_count=len(signals),
        brand_count=brand_count,
        growth_rate_pct=round(growth_rate, 1) if growth_rate is not None else None,
        supporting_signals=[pop_evidence, grow_evidence, cross_evidence, season_evidence],
    )


# ── Trend Intelligence Service ─────────────────────────────────────────────
class TrendIntelligenceService:
    """
    Main interface for trend data.
    Agents query this, not the database directly.
    """

    def _get_all_scored_trends(self) -> list[TrendScoreResult]:
        """Load all trends and compute scores."""
        db = SessionLocal()
        try:
            trends = db.query(Trend).all()
            results = []
            for trend in trends:
                signals = db.query(TrendSignal).filter(
                    TrendSignal.trend_id == trend.id
                ).all()
                score = compute_trend_score(trend, signals)
                results.append(score)
            return results
        finally:
            db.close()

    def get_trending_now(self, top_n: int = 5) -> list[TrendScoreResult]:
        """
        Returns the top N trends by total score right now.
        Sorted by score descending.
        """
        all_scores = self._get_all_scored_trends()
        sorted_scores = sorted(all_scores, key=lambda x: x.total_score, reverse=True)
        log.info("Trend scores computed for {n} trends", n=len(sorted_scores))
        return sorted_scores[:top_n]

    def get_emerging_trends(self) -> list[TrendScoreResult]:
        """Returns trends with 'emerging' status sorted by growth score."""
        all_scores = self._get_all_scored_trends()
        emerging = [t for t in all_scores if t.status == "emerging"]
        return sorted(emerging, key=lambda x: x.growth_score, reverse=True)

    def get_trends_by_category(self, category: str) -> list[TrendScoreResult]:
        """Returns all trends for a specific category (color, silhouette, etc.)"""
        all_scores = self._get_all_scored_trends()
        return [t for t in all_scores if t.category == category]

    def get_trend_report(self, trend_name: str) -> Optional[TrendReport]:
        """Full intelligence report for a single trend."""
        db = SessionLocal()
        try:
            trend = db.query(Trend).filter(
                Trend.name.ilike(f"%{trend_name}%")
            ).first()

            if not trend:
                return None

            signals = db.query(TrendSignal).filter(
                TrendSignal.trend_id == trend.id
            ).all()

            score = compute_trend_score(trend, signals)

            # Signal breakdown by type
            breakdown: dict[str, int] = {}
            for sig in signals:
                breakdown[sig.signal_type] = breakdown.get(sig.signal_type, 0) + 1

            # Status explanation
            status_text = {
                "emerging":   "Early stage — just starting to appear across collections",
                "rising":     "Growing adoption — appearing in more brands and searches",
                "peaking":    "At maximum adoption — widely visible across the market",
                "plateauing": "Stable — high adoption but growth has slowed",
                "declining":  "Losing momentum — fewer new appearances",
                "dormant":    "Currently quiet — may return in future seasons",
            }

            # Trend insight
            if score.total_score >= 80:
                insight = f"{trend.name} is a dominant trend right now with strong evidence across multiple signals."
            elif score.total_score >= 60:
                insight = f"{trend.name} is an active trend with solid supporting evidence."
            elif score.total_score >= 40:
                insight = f"{trend.name} is a moderate trend — worth watching but not yet dominant."
            else:
                insight = f"{trend.name} is an early or niche trend with limited signals so far."

            return TrendReport(
                trend_id=trend.id,
                name=trend.name,
                category=trend.category,
                status=trend.status,
                description=trend.description,
                season=trend.season,
                year=trend.year,
                score=score,
                total_signals=len(signals),
                signal_breakdown=breakdown,
                status_explanation=status_text.get(trend.status, ""),
                trend_insight=insight,
            )
        finally:
            db.close()

    def save_scores_to_db(self) -> int:
        """
        Compute and persist trend scores to the database.
        Returns the number of scores saved.
        """
        db = SessionLocal()
        try:
            trends = db.query(Trend).all()
            saved = 0
            for trend in trends:
                signals = db.query(TrendSignal).filter(
                    TrendSignal.trend_id == trend.id
                ).all()
                result = compute_trend_score(trend, signals)
                score_record = TrendScore(
                    trend_id=trend.id,
                    popularity_score=result.popularity_score,
                    growth_score=result.growth_score,
                    cross_brand_score=result.cross_brand_score,
                    search_score=result.growth_score,
                    seasonal_score=result.seasonal_score,
                    total_score=result.total_score,
                    signal_count=result.signal_count,
                    score_version=SCORE_VERSION,
                    computed_at=datetime.utcnow(),
                )
                db.add(score_record)
                saved += 1
            db.commit()
            log.info("Saved {n} trend scores to database", n=saved)
            return saved
        except Exception as e:
            db.rollback()
            log.error("Failed to save trend scores: {e}", e=str(e))
            raise
        finally:
            db.close()


# ── Singleton ──────────────────────────────────────────────────────────────
trend_service = TrendIntelligenceService()
