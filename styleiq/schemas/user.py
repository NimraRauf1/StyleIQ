from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import Field, field_validator, model_validator
from styleiq.schemas.enums import (
    Aesthetic, InteractionType, ModestyLevel, Occasion,
    PakistaniCity, PreferenceSentiment, PreferenceSource, StylePreferenceType,
)
from styleiq.schemas.fashion import StyleIQBase

class StyleDNA(StyleIQBase):
    user_id: UUID
    minimal: float = Field(default=50.0, ge=0.0, le=100.0)
    maximalist: float = Field(default=50.0, ge=0.0, le=100.0)
    feminine: float = Field(default=50.0, ge=0.0, le=100.0)
    androgynous: float = Field(default=50.0, ge=0.0, le=100.0)
    traditional: float = Field(default=50.0, ge=0.0, le=100.0)
    contemporary: float = Field(default=50.0, ge=0.0, le=100.0)
    romantic: float = Field(default=50.0, ge=0.0, le=100.0)
    edgy: float = Field(default=50.0, ge=0.0, le=100.0)
    streetwear: float = Field(default=50.0, ge=0.0, le=100.0)
    classic: float = Field(default=50.0, ge=0.0, le=100.0)
    bohemian: float = Field(default=50.0, ge=0.0, le=100.0)
    eastern_affinity: float = Field(default=50.0, ge=0.0, le=100.0)
    modesty_score: float = Field(default=50.0, ge=0.0, le=100.0)
    version: int = Field(default=1)
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    interaction_count: int = Field(default=0)

    @property
    def top_aesthetics(self) -> list[tuple[str, float]]:
        dims = {
            "Minimal": self.minimal, "Maximalist": self.maximalist,
            "Feminine": self.feminine, "Androgynous": self.androgynous,
            "Traditional": self.traditional, "Contemporary": self.contemporary,
            "Romantic": self.romantic, "Edgy": self.edgy,
            "Streetwear": self.streetwear, "Classic": self.classic,
            "Bohemian": self.bohemian,
        }
        return sorted(dims.items(), key=lambda x: x[1], reverse=True)[:3]

    @property
    def style_archetype(self) -> str:
        top = self.top_aesthetics
        if not top:
            return "Undefined"
        top_two = [t[0] for t in top[:2]]
        combos = {
            frozenset(["Minimal", "Feminine"]): "Soft Minimalist",
            frozenset(["Minimal", "Classic"]): "Clean Classic",
            frozenset(["Minimal", "Contemporary"]): "Modern Minimalist",
            frozenset(["Feminine", "Romantic"]): "Romantic Feminine",
            frozenset(["Traditional", "Feminine"]): "Elegant Traditional",
            frozenset(["Traditional", "Classic"]): "Heritage Classic",
            frozenset(["Contemporary", "Edgy"]): "Bold Contemporary",
            frozenset(["Streetwear", "Contemporary"]): "Urban Contemporary",
            frozenset(["Bohemian", "Romantic"]): "Free-Spirited Romantic",
            frozenset(["Maximalist", "Feminine"]): "Maximalist Feminine",
        }
        return combos.get(frozenset(top_two), f"{top_two[0]} {top_two[1]}")

    def as_summary_dict(self) -> dict[str, float]:
        return {
            "Minimal": self.minimal, "Feminine": self.feminine,
            "Traditional": self.traditional, "Contemporary": self.contemporary,
            "Romantic": self.romantic, "Classic": self.classic,
            "Streetwear": self.streetwear, "Eastern Affinity": self.eastern_affinity,
            "Modesty": self.modesty_score,
        }

class StylePreference(StyleIQBase):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    pref_type: StylePreferenceType
    pref_value: str
    sentiment: PreferenceSentiment
    source: PreferenceSource
    weight: float = Field(default=1.0, ge=0.1, le=3.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OnboardingProfile(StyleIQBase):
    age: Optional[int] = Field(None, ge=13, le=100)
    city: PakistaniCity = PakistaniCity.ISLAMABAD
    occupation: Optional[str] = None
    lifestyle: Optional[str] = None
    height_cm: Optional[int] = Field(None, ge=140, le=220)
    weight_optional: Optional[int] = None
    body_notes: Optional[str] = None
    enable_body_based_recommendations: bool = False
    modesty_level: ModestyLevel = ModestyLevel.MODERATE
    eastern_western_preference: float = Field(default=0.5, ge=0.0, le=1.0)
    preferred_aesthetics: list[str] = Field(default_factory=list)
    preferred_colors: list[str] = Field(default_factory=list)
    disliked_colors: list[str] = Field(default_factory=list)
    preferred_silhouettes: list[str] = Field(default_factory=list)
    preferred_fabrics: list[str] = Field(default_factory=list)
    preferred_brands: list[str] = Field(default_factory=list)
    disliked_brands: list[str] = Field(default_factory=list)
    budget_min: int = Field(default=0, ge=0)
    budget_max: int = Field(default=10000, ge=0)
    usual_occasions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_budget_range(self) -> "OnboardingProfile":
        if self.budget_min > self.budget_max:
            raise ValueError("budget_min cannot exceed budget_max")
        return self

    @field_validator("preferred_aesthetics", mode="before")
    @classmethod
    def validate_aesthetics(cls, v: list) -> list:
        valid = {a.value for a in Aesthetic}
        for item in v:
            if item not in valid:
                raise ValueError(f"'{item}' is not a valid aesthetic. Choose from: {valid}")
        return v

class UserInteraction(StyleIQBase):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    interaction_type: InteractionType
    target_type: str
    target_id: UUID
    weight: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_positive(self) -> bool:
        return self.interaction_type in (InteractionType.LIKE, InteractionType.SAVE, InteractionType.PURCHASE)

class SystemStatus(StyleIQBase):
    app_name: str
    version: str
    environment: str
    database_connected: bool
    claude_configured: bool
    data_dir_exists: bool
    log_level: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_healthy(self) -> bool:
        return self.database_connected and self.data_dir_exists
