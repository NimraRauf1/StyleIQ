"""
STYLEIQ Brand Intelligence Service
────────────────────────────────────
Computes brand compatibility scores and generates
brand intelligence reports.

Every score is computed from real data — never invented.
The formula is transparent and configurable.

Usage:
    from styleiq.services.brand_service import brand_service
    report = brand_service.get_brand_report("khaadi")
    matches = brand_service.get_compatible_brands(user_profile, top_n=5)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from styleiq.database.connection import SessionLocal
from styleiq.database.models import Brand, BrandProfile
from styleiq.logger import get_logger

log = get_logger(__name__)


# ── Score weights (configurable) ───────────────────────────────────────────
# These control how much each dimension contributes to overall compatibility.
# They must sum to 1.0.
COMPATIBILITY_WEIGHTS = {
    "style_match":    0.35,   # most important — does the brand's aesthetic match yours?
    "budget_match":   0.25,   # can you actually afford it?
    "modesty_match":  0.25,   # does the brand's coverage match your preference?
    "occasion_match": 0.15,   # does the brand serve your usual occasions?
}


# ── Data classes for structured output ────────────────────────────────────
@dataclass
class BrandCompatibilityScore:
    """
    Detailed compatibility score between a user profile and a brand.
    Every dimension is shown — no black box.
    """
    brand_slug: str
    brand_name: str
    brand_tier: str

    # Component scores (0–100)
    style_match:    float = 0.0
    budget_match:   float = 0.0
    modesty_match:  float = 0.0
    occasion_match: float = 0.0
    overall_score:  float = 0.0

    # Explanation
    style_reasons:    list[str] = field(default_factory=list)
    budget_reason:    str = ""
    modesty_reason:   str = ""
    occasion_reasons: list[str] = field(default_factory=list)
    summary:          str = ""

    # Price info
    typical_price_min: Optional[int] = None
    typical_price_max: Optional[int] = None


@dataclass
class BrandReport:
    """Full intelligence report for a single brand."""
    slug:        str
    name:        str
    tier:        str
    description: Optional[str]

    # Style profile
    style_tags:            list[str] = field(default_factory=list)
    modesty_score:         Optional[float] = None
    eastern_western_ratio: Optional[float] = None

    # Price
    typical_price_min: Optional[int] = None
    typical_price_max: Optional[int] = None

    # Computed insights
    price_tier_label:      str = ""
    modesty_label:         str = ""
    eastern_western_label: str = ""
    best_for_occasions:    list[str] = field(default_factory=list)
    best_for_aesthetics:   list[str] = field(default_factory=list)
    not_ideal_for:         list[str] = field(default_factory=list)


# ── Helper functions ───────────────────────────────────────────────────────
def _modesty_label(score: Optional[float]) -> str:
    if score is None:
        return "Unknown"
    if score >= 4.5:
        return "Full Modest"
    elif score >= 3.5:
        return "Modest"
    elif score >= 2.5:
        return "Moderate"
    elif score >= 1.5:
        return "Relaxed"
    return "Minimal Coverage"


def _eastern_western_label(ratio: Optional[float]) -> str:
    if ratio is None:
        return "Unknown"
    if ratio >= 0.8:
        return "Strongly Eastern"
    elif ratio >= 0.6:
        return "Mostly Eastern"
    elif ratio >= 0.4:
        return "Mixed / Fusion"
    elif ratio >= 0.2:
        return "Mostly Western"
    return "Strongly Western"


def _price_tier_label(price_min: Optional[int], price_max: Optional[int]) -> str:
    if price_max is None:
        return "Unknown"
    if price_max <= 5000:
        return "Budget-Friendly (under PKR 5,000)"
    elif price_max <= 12000:
        return "Mid-Range (PKR 5,000–12,000)"
    elif price_max <= 30000:
        return "Premium (PKR 12,000–30,000)"
    return "Luxury (PKR 30,000+)"


def _clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Keep a value within bounds."""
    return max(min_val, min(max_val, value))


# ── Score computation ──────────────────────────────────────────────────────
def _compute_style_match(brand: Brand, style_tags: list[str], aesthetics: list[str]) -> tuple[float, list[str]]:
    """
    How well does this brand's style match the user's preferences?

    Method: count overlapping style tags and aesthetics.
    Each overlap adds to the score.
    """
    reasons = []
    if not brand.style_tags:
        return 50.0, ["No style data available — neutral score"]

    brand_tags = set(t.lower() for t in brand.style_tags)
    user_tags = set(t.lower() for t in (style_tags + aesthetics))

    overlaps = brand_tags & user_tags
    if not overlaps:
        return 30.0, [f"Style tags don't overlap with your preferences ({', '.join(brand_tags)})"]

    # Score: 30 base + up to 70 for overlaps
    overlap_ratio = len(overlaps) / max(len(brand_tags), 1)
    score = 30.0 + (overlap_ratio * 70.0)

    for tag in overlaps:
        reasons.append(f"Shares your '{tag}' aesthetic")

    return _clamp(score), reasons


def _compute_budget_match(brand: Brand, budget_min: int, budget_max: int) -> tuple[float, str]:
    """
    How well does this brand's price range fit the user's budget?

    Method: check overlap between brand price range and user budget range.
    """
    b_min = brand.typical_price_min or 0
    b_max = brand.typical_price_max or 999999

    # Perfect overlap
    if b_min <= budget_max and b_max >= budget_min:
        # How much of the brand's range is within budget?
        overlap_low  = max(b_min, budget_min)
        overlap_high = min(b_max, budget_max)
        brand_range  = max(b_max - b_min, 1)
        overlap_pct  = (overlap_high - overlap_low) / brand_range
        score = 50.0 + (overlap_pct * 50.0)
        reason = f"Price range PKR {b_min:,}–{b_max:,} overlaps with your PKR {budget_min:,}–{budget_max:,} budget"
    elif b_min > budget_max:
        # Brand is entirely above budget
        overshoot = b_min - budget_max
        score = max(0.0, 40.0 - (overshoot / 1000))
        reason = f"Starting price PKR {b_min:,} is above your PKR {budget_max:,} budget"
    else:
        # Brand is entirely below budget (still fine — you can spend less)
        score = 75.0
        reason = f"Fully within your budget (max PKR {b_max:,})"

    return _clamp(score), reason


def _compute_modesty_match(brand: Brand, user_modesty: int) -> tuple[float, str]:
    """
    How well does the brand's modesty level match the user's preference?

    Method: compare brand modesty score (1–5) to user's modesty level (1–5).
    """
    if brand.modesty_score is None:
        return 50.0, "No modesty data available — neutral score"

    brand_modesty = brand.modesty_score
    diff = abs(brand_modesty - user_modesty)

    if diff == 0:
        score = 100.0
        reason = f"Perfect modesty match — brand scores {brand_modesty}/5, you prefer {user_modesty}/5"
    elif diff <= 0.5:
        score = 90.0
        reason = f"Near-perfect modesty match ({brand_modesty}/5 vs your {user_modesty}/5)"
    elif diff <= 1.0:
        score = 75.0
        reason = f"Good modesty match ({brand_modesty}/5 vs your {user_modesty}/5)"
    elif diff <= 2.0:
        score = 45.0
        reason = f"Moderate mismatch — brand is {'more modest' if brand_modesty > user_modesty else 'less modest'} than your preference"
    else:
        score = 15.0
        reason = f"Significant modesty mismatch ({brand_modesty}/5 vs your {user_modesty}/5)"

    return _clamp(score), reason


def _compute_occasion_match(brand: Brand, user_occasions: list[str]) -> tuple[float, list[str]]:
    """
    Does this brand serve the user's typical occasions?

    Method: map brand tier and style to occasions, check overlap.
    """
    reasons = []

    # Brand tier → occasions mapping
    tier_occasions = {
        "mass_market":    ["university", "home", "market", "office_casual", "eid"],
        "premium_mid":    ["university", "office_casual", "office_formal", "dawat", "dinner", "eid", "brunch"],
        "premium":        ["dawat", "dinner", "mehndi", "nikkah", "baraat", "walima", "formal_event", "eid"],
        "luxury":         ["baraat", "walima", "nikkah", "formal_event", "mehndi"],
        "western_casual": ["university", "cafe", "brunch", "market", "travel_local"],
    }

    brand_occasions = set(tier_occasions.get(brand.tier, []))

    # Add occasions based on style tags
    if brand.style_tags:
        tags = [t.lower() for t in brand.style_tags]
        if "bridal" in tags or "formal" in tags:
            brand_occasions.update(["baraat", "walima", "nikkah", "mehndi"])
        if "casual" in tags or "everyday" in tags:
            brand_occasions.update(["university", "home", "cafe", "brunch"])
        if "lawn" in tags:
            brand_occasions.update(["university", "home", "eid", "dawat"])

    user_set = set(user_occasions)
    overlaps = brand_occasions & user_set

    if not user_occasions:
        return 50.0, ["No occasion preferences set"]

    overlap_ratio = len(overlaps) / max(len(user_set), 1)
    score = overlap_ratio * 100.0

    for occ in list(overlaps)[:3]:   # show top 3
        reasons.append(f"Suitable for {occ.replace('_', ' ')}")

    if not overlaps:
        reasons.append("Limited overlap with your usual occasions")

    return _clamp(score), reasons


# ── Main Service ───────────────────────────────────────────────────────────
class BrandIntelligenceService:
    """
    Main brand intelligence engine.
    All public methods use real data from the database.
    """

    def get_all_brands(self) -> list[Brand]:
        db = SessionLocal()
        try:
            return db.query(Brand).filter(Brand.commercial_use_ok == True).all()
        finally:
            db.close()

    def get_brand(self, slug: str) -> Optional[Brand]:
        db = SessionLocal()
        try:
            return db.query(Brand).filter(Brand.slug == slug).first()
        finally:
            db.close()

    def get_brand_report(self, slug: str) -> Optional[BrandReport]:
        """
        Generate a full intelligence report for a brand.
        """
        brand = self.get_brand(slug)
        if not brand:
            log.warning("Brand not found: {slug}", slug=slug)
            return None

        # Determine best occasions from tier
        tier_occasions = {
            "mass_market":    ["University", "Everyday", "Eid", "Home"],
            "premium_mid":    ["Office", "Dawat", "Eid", "Brunch", "Dinner"],
            "premium":        ["Dawat", "Mehndi", "Walima", "Formal Events"],
            "luxury":         ["Baraat", "Walima", "Nikkah", "Formal Events"],
            "western_casual": ["University", "Cafe", "Brunch", "Travel"],
        }

        # Not ideal for — inverse of best occasions
        not_ideal = {
            "mass_market":    ["Baraat", "Walima", "Luxury Events"],
            "premium_mid":    ["Home Wear", "Very Casual"],
            "premium":        ["Everyday Casual", "University"],
            "luxury":         ["Everyday", "University", "Casual Outings"],
            "western_casual": ["Formal Events", "Wedding Functions"],
        }

        return BrandReport(
            slug=brand.slug,
            name=brand.name,
            tier=brand.tier,
            description=brand.description,
            style_tags=brand.style_tags or [],
            modesty_score=brand.modesty_score,
            eastern_western_ratio=brand.eastern_western_ratio,
            typical_price_min=brand.typical_price_min,
            typical_price_max=brand.typical_price_max,
            price_tier_label=_price_tier_label(brand.typical_price_min, brand.typical_price_max),
            modesty_label=_modesty_label(brand.modesty_score),
            eastern_western_label=_eastern_western_label(brand.eastern_western_ratio),
            best_for_occasions=tier_occasions.get(brand.tier, []),
            best_for_aesthetics=brand.style_tags or [],
            not_ideal_for=not_ideal.get(brand.tier, []),
        )

    def score_brand_for_user(
        self,
        brand: Brand,
        user_budget_min: int,
        user_budget_max: int,
        user_modesty_level: int,
        user_style_tags: list[str],
        user_aesthetics: list[str],
        user_occasions: list[str],
    ) -> BrandCompatibilityScore:
        """
        Compute a full compatibility score between a brand and a user profile.
        Every number is computed from real data.
        """
        style_score, style_reasons = _compute_style_match(brand, user_style_tags, user_aesthetics)
        budget_score, budget_reason = _compute_budget_match(brand, user_budget_min, user_budget_max)
        modesty_score, modesty_reason = _compute_modesty_match(brand, user_modesty_level)
        occasion_score, occasion_reasons = _compute_occasion_match(brand, user_occasions)

        # Weighted overall score
        overall = (
            style_score   * COMPATIBILITY_WEIGHTS["style_match"] +
            budget_score  * COMPATIBILITY_WEIGHTS["budget_match"] +
            modesty_score * COMPATIBILITY_WEIGHTS["modesty_match"] +
            occasion_score * COMPATIBILITY_WEIGHTS["occasion_match"]
        )

        # Generate summary
        if overall >= 85:
            summary = f"Excellent match — {brand.name} aligns strongly with your style, budget and preferences"
        elif overall >= 70:
            summary = f"Good match — {brand.name} suits most of your preferences"
        elif overall >= 55:
            summary = f"Moderate match — {brand.name} works for some of your needs"
        else:
            summary = f"Limited match — {brand.name} may not align well with your current preferences"

        return BrandCompatibilityScore(
            brand_slug=brand.slug,
            brand_name=brand.name,
            brand_tier=brand.tier,
            style_match=round(style_score, 1),
            budget_match=round(budget_score, 1),
            modesty_match=round(modesty_score, 1),
            occasion_match=round(occasion_score, 1),
            overall_score=round(overall, 1),
            style_reasons=style_reasons,
            budget_reason=budget_reason,
            modesty_reason=modesty_reason,
            occasion_reasons=occasion_reasons,
            summary=summary,
            typical_price_min=brand.typical_price_min,
            typical_price_max=brand.typical_price_max,
        )

    def get_compatible_brands(
        self,
        user_budget_min: int,
        user_budget_max: int,
        user_modesty_level: int,
        user_style_tags: list[str],
        user_aesthetics: list[str],
        user_occasions: list[str],
        top_n: int = 5,
    ) -> list[BrandCompatibilityScore]:
        """
        Score all brands against a user profile and return the top N.
        This is the "best brands for YOU" feature.
        """
        brands = self.get_all_brands()
        scores = []

        for brand in brands:
            score = self.score_brand_for_user(
                brand=brand,
                user_budget_min=user_budget_min,
                user_budget_max=user_budget_max,
                user_modesty_level=user_modesty_level,
                user_style_tags=user_style_tags,
                user_aesthetics=user_aesthetics,
                user_occasions=user_occasions,
            )
            scores.append(score)

        # Sort by overall score descending
        scores.sort(key=lambda s: s.overall_score, reverse=True)
        log.info("Brand compatibility computed for {n} brands", n=len(scores))
        return scores[:top_n]


# ── Singleton ──────────────────────────────────────────────────────────────
brand_service = BrandIntelligenceService()
