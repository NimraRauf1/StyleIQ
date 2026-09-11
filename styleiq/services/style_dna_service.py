"""
STYLEIQ Style DNA Service
──────────────────────────
Computes, stores, and updates a user's Style DNA.

Style DNA is a set of scored aesthetic dimensions (0–100).
It starts from onboarding answers and evolves from interactions.

Every update is versioned — we never overwrite, we create a new version.
This means we can track how a user's style changes over time.

Usage:
    from styleiq.services.style_dna_service import style_dna_service
    dna = style_dna_service.seed_from_onboarding(user_id, profile)
    dna = style_dna_service.get_current_dna(user_id)
    dna = style_dna_service.update_from_interaction(user_id, interaction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from styleiq.database.connection import SessionLocal
from styleiq.database.models import StyleDNA as StyleDNAModel
from styleiq.database.models import StylePreference, Interaction, User, StyleProfile
from styleiq.logger import get_logger
from styleiq.schemas.enums import InteractionType

log = get_logger(__name__)


# ── Interaction weights ────────────────────────────────────────────────────
# How much does each interaction type move the Style DNA?
INTERACTION_WEIGHTS = {
    InteractionType.LIKE:      1.0,   # strong positive signal
    InteractionType.SAVE:      1.2,   # stronger — user wants to keep it
    InteractionType.PURCHASE:  1.5,   # strongest — real money spent
    InteractionType.DISLIKE:  -1.0,   # strong negative signal
    InteractionType.SKIP:     -0.3,   # weak negative — maybe just not now
    InteractionType.SHARE:     0.8,   # positive — user is proud of it
}

# How much each interaction moves the score (in points, 0–100 scale)
MOVE_AMOUNT = 3.0   # each interaction moves dimensions by up to 3 points

# Decay factor — older interactions matter less
# (used in future weighted average implementation)
RECENCY_DECAY = 0.95

# Aesthetic tag → DNA dimension mapping
# When a user likes something tagged "minimal", which DNA dimensions does it affect?
AESTHETIC_TO_DNA = {
    "minimal":       {"minimal": 1.0, "maximalist": -0.5, "contemporary": 0.3},
    "maximalist":    {"maximalist": 1.0, "minimal": -0.5},
    "feminine":      {"feminine": 1.0, "androgynous": -0.3, "romantic": 0.3},
    "androgynous":   {"androgynous": 1.0, "feminine": -0.3},
    "traditional":   {"traditional": 1.0, "eastern_affinity": 0.5, "contemporary": -0.2},
    "contemporary":  {"contemporary": 1.0, "traditional": -0.2},
    "romantic":      {"romantic": 1.0, "feminine": 0.3, "edgy": -0.2},
    "edgy":          {"edgy": 1.0, "romantic": -0.2, "classic": -0.2},
    "streetwear":    {"streetwear": 1.0, "classic": -0.3, "traditional": -0.2},
    "bohemian":      {"bohemian": 1.0, "traditional": 0.2, "contemporary": 0.2},
    "classic":       {"classic": 1.0, "edgy": -0.3, "streetwear": -0.2},
    "clean_girl":    {"minimal": 0.8, "contemporary": 0.5, "feminine": 0.3},
    "soft_girl":     {"feminine": 0.8, "romantic": 0.6, "minimal": 0.2},
    "ethnic":        {"traditional": 0.8, "eastern_affinity": 0.6},
    "lawn":          {"eastern_affinity": 0.4, "traditional": 0.3},
    "colorful":      {"maximalist": 0.4, "minimal": -0.3},
    "modest":        {"modesty_score": 1.0},
}

# Garment family → DNA dimension mapping
FAMILY_TO_DNA = {
    "eastern":  {"eastern_affinity": 0.8, "traditional": 0.3},
    "western":  {"eastern_affinity": -0.6, "contemporary": 0.3},
    "modest":   {"modesty_score": 0.8, "eastern_affinity": 0.3},
    "fusion":   {"eastern_affinity": 0.2, "contemporary": 0.4},
}


# ── DNA delta calculation ──────────────────────────────────────────────────
def _build_delta(tags: list[str], family: Optional[str], sentiment: float) -> dict[str, float]:
    """
    Build a dictionary of dimension → change amount.

    sentiment: +1.0 for positive interactions, -1.0 for negative.
    tags: aesthetic/style tags from the interacted item.
    family: garment family (eastern/western/modest/fusion).
    """
    delta: dict[str, float] = {}

    # Apply aesthetic tag influences
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in AESTHETIC_TO_DNA:
            for dimension, influence in AESTHETIC_TO_DNA[tag_lower].items():
                current = delta.get(dimension, 0.0)
                delta[dimension] = current + (influence * sentiment * MOVE_AMOUNT)

    # Apply garment family influence
    if family and family in FAMILY_TO_DNA:
        for dimension, influence in FAMILY_TO_DNA[family].items():
            current = delta.get(dimension, 0.0)
            delta[dimension] = current + (influence * sentiment * MOVE_AMOUNT * 0.5)

    return delta


def _apply_delta(dna_dict: dict[str, float], delta: dict[str, float]) -> dict[str, float]:
    """
    Apply a delta to a DNA dictionary.
    Clamps all values to 0–100 range.
    """
    result = dict(dna_dict)
    for dimension, change in delta.items():
        if dimension in result:
            new_val = result[dimension] + change
            result[dimension] = max(0.0, min(100.0, new_val))
    return result


def _dna_model_to_dict(dna: StyleDNAModel) -> dict[str, float]:
    """Convert a StyleDNA database record to a plain dict."""
    return {
        "minimal":          dna.minimal,
        "maximalist":       dna.maximalist,
        "feminine":         dna.feminine,
        "androgynous":      dna.androgynous,
        "traditional":      dna.traditional,
        "contemporary":     dna.contemporary,
        "romantic":         dna.romantic,
        "edgy":             dna.edgy,
        "streetwear":       dna.streetwear,
        "classic":          dna.classic,
        "bohemian":         dna.bohemian,
        "eastern_affinity": dna.eastern_affinity,
        "modesty_score":    dna.modesty_score,
    }


# ── Onboarding → initial DNA ───────────────────────────────────────────────
def _seed_dna_from_onboarding(
    age: Optional[int],
    city: Optional[str],
    modesty_level: int,
    eastern_western_pref: float,
    preferred_aesthetics: list[str],
    preferred_silhouettes: list[str],
    preferred_colors: list[str],
    usual_occasions: list[str],
) -> dict[str, float]:
    """
    Build an initial DNA from onboarding answers.
    This is the starting point — interactions refine it over time.
    """
    # Start at 50 (neutral) for all dimensions
    dna = {
        "minimal": 50.0, "maximalist": 50.0,
        "feminine": 50.0, "androgynous": 50.0,
        "traditional": 50.0, "contemporary": 50.0,
        "romantic": 50.0, "edgy": 50.0,
        "streetwear": 50.0, "classic": 50.0,
        "bohemian": 50.0,
        "eastern_affinity": 50.0,
        "modesty_score": 50.0,
    }

    # ── Modesty level → modesty_score ─────────────────────────────────
    # modesty_level is 1–5, we map to 0–100
    dna["modesty_score"] = (modesty_level - 1) * 25.0  # 1→0, 2→25, 3→50, 4→75, 5→100

    # ── Eastern/Western preference → eastern_affinity ─────────────────
    # eastern_western_pref: 0.0=fully eastern, 1.0=fully western
    dna["eastern_affinity"] = (1.0 - eastern_western_pref) * 100.0

    # ── Preferred aesthetics ───────────────────────────────────────────
    for aesthetic in preferred_aesthetics:
        aesthetic_lower = aesthetic.lower()
        if aesthetic_lower in AESTHETIC_TO_DNA:
            for dimension, influence in AESTHETIC_TO_DNA[aesthetic_lower].items():
                if dimension in dna:
                    # Strong signal from explicit preference — move by 15 points
                    dna[dimension] = max(0.0, min(100.0, dna[dimension] + influence * 15.0))

    # ── Occasion context ───────────────────────────────────────────────
    wedding_occasions = {"mehndi", "dholki", "nikkah", "baraat", "walima"}
    casual_occasions = {"university", "cafe", "brunch", "home"}

    occasion_set = set(usual_occasions)
    if occasion_set & wedding_occasions:
        # Wedding occasions → more traditional, eastern
        dna["traditional"] = min(100.0, dna["traditional"] + 10.0)
        dna["eastern_affinity"] = min(100.0, dna["eastern_affinity"] + 8.0)
    if occasion_set & casual_occasions:
        # Casual occasions → more contemporary
        dna["contemporary"] = min(100.0, dna["contemporary"] + 8.0)

    # Clamp all values
    return {k: max(0.0, min(100.0, v)) for k, v in dna.items()}


# ── Main Service ───────────────────────────────────────────────────────────
class StyleDNAService:

    def create_user(self, email: str, username: str) -> str:
        """
        Create a minimal user record.
        Returns the new user's ID.
        In production this would handle proper auth — for now it's simple.
        """
        db = SessionLocal()
        try:
            # Check if user already exists
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                log.info("User already exists: {email}", email=email)
                return existing.id

            user = User(
                id=str(uuid4()),
                email=email,
                username=username,
                hashed_password="placeholder_hash",  # real auth in Milestone 14
                is_active=True,
            )
            db.add(user)
            db.commit()
            log.info("Created user: {username}", username=username)
            return user.id
        finally:
            db.close()

    def seed_from_onboarding(
        self,
        user_id: str,
        age: Optional[int],
        city: Optional[str],
        modesty_level: int,
        eastern_western_pref: float,
        preferred_aesthetics: list[str],
        preferred_silhouettes: list[str],
        preferred_colors: list[str],
        usual_occasions: list[str],
        budget_min: int = 0,
        budget_max: int = 10000,
    ) -> StyleDNAModel:
        """
        Create the user's initial Style DNA from onboarding answers.
        Also creates a StyleProfile record.
        """
        db = SessionLocal()
        try:
            # Build initial DNA values
            dna_values = _seed_dna_from_onboarding(
                age=age,
                city=city,
                modesty_level=modesty_level,
                eastern_western_pref=eastern_western_pref,
                preferred_aesthetics=preferred_aesthetics,
                preferred_silhouettes=preferred_silhouettes,
                preferred_colors=preferred_colors,
                usual_occasions=usual_occasions,
            )

            # Create or update StyleProfile
            profile = db.query(StyleProfile).filter(
                StyleProfile.user_id == user_id
            ).first()

            if not profile:
                profile = StyleProfile(
                    id=str(uuid4()),
                    user_id=user_id,
                    age=age,
                    city=city,
                    modesty_level=modesty_level,
                    eastern_western_pref=eastern_western_pref,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    preferred_aesthetics=preferred_aesthetics,
                    preferred_colors=preferred_colors,
                    preferred_occasions=usual_occasions,
                )
                db.add(profile)

            # Create initial StyleDNA (version 1)
            dna = StyleDNAModel(
                id=str(uuid4()),
                user_id=user_id,
                version=1,
                interaction_count=0,
                computed_at=datetime.utcnow(),
                **dna_values,
            )
            db.add(dna)
            db.commit()
            db.refresh(dna)

            log.info(
                "Style DNA seeded from onboarding | user={uid} | version=1",
                uid=user_id[:8]
            )
            return dna

        finally:
            db.close()

    def get_current_dna(self, user_id: str) -> Optional[StyleDNAModel]:
        """Get the most recent Style DNA for a user."""
        db = SessionLocal()
        try:
            return (
                db.query(StyleDNAModel)
                .filter(StyleDNAModel.user_id == user_id)
                .order_by(StyleDNAModel.version.desc())
                .first()
            )
        finally:
            db.close()

    def update_from_interaction(
        self,
        user_id: str,
        interaction_type: str,
        item_aesthetic_tags: list[str],
        item_garment_family: Optional[str] = None,
        item_modesty_level: Optional[int] = None,
    ) -> Optional[StyleDNAModel]:
        """
        Update Style DNA based on a user interaction.

        Every like/dislike/save/skip creates a new DNA version.
        The old version is kept for history.

        Returns the new DNA record.
        """
        # Get current DNA
        current = self.get_current_dna(user_id)
        if not current:
            log.warning("No DNA found for user {uid}", uid=user_id[:8])
            return None

        # Determine sentiment from interaction type
        try:
            itype = InteractionType(interaction_type)
        except ValueError:
            log.warning("Unknown interaction type: {t}", t=interaction_type)
            return current

        weight = INTERACTION_WEIGHTS.get(itype, 0.0)
        if weight == 0.0:
            return current

        sentiment = 1.0 if weight > 0 else -1.0
        magnitude = abs(weight)

        # Build delta
        delta = _build_delta(
            tags=item_aesthetic_tags,
            family=item_garment_family,
            sentiment=sentiment * magnitude,
        )

        # Apply modesty signal if present
        if item_modesty_level is not None:
            modesty_signal = (item_modesty_level - 1) * 25.0  # 1→0, 5→100
            current_modesty = current.modesty_score
            # Move toward the item's modesty level
            if sentiment > 0:
                delta["modesty_score"] = (modesty_signal - current_modesty) * 0.1
            else:
                delta["modesty_score"] = (current_modesty - modesty_signal) * 0.05

        # Apply delta to current DNA
        current_dict = _dna_model_to_dict(current)
        new_dict = _apply_delta(current_dict, delta)

        # Save as new version
        db = SessionLocal()
        try:
            new_dna = StyleDNAModel(
                id=str(uuid4()),
                user_id=user_id,
                version=current.version + 1,
                interaction_count=current.interaction_count + 1,
                computed_at=datetime.utcnow(),
                **new_dict,
            )
            db.add(new_dna)
            db.commit()
            db.refresh(new_dna)

            log.debug(
                "DNA updated | user={uid} | v{old}→v{new} | {itype}",
                uid=user_id[:8],
                old=current.version,
                new=new_dna.version,
                itype=interaction_type,
            )
            return new_dna

        finally:
            db.close()

    def get_dna_history(self, user_id: str) -> list[StyleDNAModel]:
        """Get all DNA versions for a user (oldest first)."""
        db = SessionLocal()
        try:
            return (
                db.query(StyleDNAModel)
                .filter(StyleDNAModel.user_id == user_id)
                .order_by(StyleDNAModel.version.asc())
                .all()
            )
        finally:
            db.close()

    def get_style_archetype(self, dna: StyleDNAModel) -> str:
        """Compute the user's style archetype from their DNA."""
        dims = {
            "Minimal": dna.minimal, "Maximalist": dna.maximalist,
            "Feminine": dna.feminine, "Androgynous": dna.androgynous,
            "Traditional": dna.traditional, "Contemporary": dna.contemporary,
            "Romantic": dna.romantic, "Edgy": dna.edgy,
            "Streetwear": dna.streetwear, "Classic": dna.classic,
            "Bohemian": dna.bohemian,
        }
        top_two = sorted(dims.items(), key=lambda x: x[1], reverse=True)[:2]
        top_names = frozenset(t[0] for t in top_two)

        combos = {
            frozenset(["Minimal", "Feminine"]):      "Soft Minimalist",
            frozenset(["Minimal", "Classic"]):       "Clean Classic",
            frozenset(["Minimal", "Contemporary"]):  "Modern Minimalist",
            frozenset(["Feminine", "Romantic"]):     "Romantic Feminine",
            frozenset(["Traditional", "Feminine"]):  "Elegant Traditional",
            frozenset(["Traditional", "Classic"]):   "Heritage Classic",
            frozenset(["Contemporary", "Edgy"]):     "Bold Contemporary",
            frozenset(["Streetwear", "Contemporary"]):"Urban Contemporary",
            frozenset(["Bohemian", "Romantic"]):     "Free-Spirited Romantic",
            frozenset(["Maximalist", "Feminine"]):   "Maximalist Feminine",
            frozenset(["Maximalist", "Traditional"]):"Rich Traditional",
        }
        return combos.get(top_names, f"{top_two[0][0]} {top_two[1][0]}")


# ── Singleton ──────────────────────────────────────────────────────────────
style_dna_service = StyleDNAService()
