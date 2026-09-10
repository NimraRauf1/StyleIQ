from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator, model_validator
from styleiq.schemas.enums import (
    Aesthetic, BrandTier, ConfidenceLevel, DataLicenseType,
    Embellishment, Fabric, GarmentFamily, ModestyLevel,
    NecklineStyle, Occasion, Season, Silhouette, SleeveStyle,
    TrendCategory, TrendGeography, TrendStatus,
)

class StyleIQBase(BaseModel):
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "use_enum_values": True,
    }

class ColorEntry(StyleIQBase):
    name: str
    hex_code: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    family: str
    is_neutral: bool = False
    is_traditional_pk: bool = False

class BrandBase(StyleIQBase):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str
    tier: BrandTier
    country: str = "Pakistan"
    website: Optional[str] = None
    instagram_handle: Optional[str] = None

class BrandCreate(BrandBase):
    style_tags: list[str] = Field(default_factory=list)
    typical_price_min: Optional[int] = Field(None, ge=0)
    typical_price_max: Optional[int] = Field(None, ge=0)
    modesty_score: Optional[float] = Field(None, ge=1.0, le=5.0)
    eastern_western_ratio: Optional[float] = Field(None, ge=0.0, le=1.0)
    description: Optional[str] = None
    data_source: str = "manual"
    data_license: DataLicenseType = DataLicenseType.OWNED

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        import re
        v = v.lower().strip()
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v

    @model_validator(mode="after")
    def validate_price_range(self) -> "BrandCreate":
        if self.typical_price_min and self.typical_price_max:
            if self.typical_price_min > self.typical_price_max:
                raise ValueError("typical_price_min cannot exceed typical_price_max")
        return self

class BrandRead(BrandCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = None

class ProductBase(StyleIQBase):
    name: str = Field(..., min_length=1, max_length=200)
    brand_slug: str
    garment_family: GarmentFamily
    category: str
    price: int = Field(..., ge=0)

class ProductCreate(ProductBase):
    original_price: Optional[int] = Field(None, ge=0)
    fabric: Optional[Fabric] = None
    colors: list[str] = Field(default_factory=list)
    silhouette: Optional[Silhouette] = None
    neckline: Optional[NecklineStyle] = None
    sleeve: Optional[SleeveStyle] = None
    embellishment: Optional[Embellishment] = None
    occasion_tags: list[str] = Field(default_factory=list)
    season_tags: list[str] = Field(default_factory=list)
    modesty_level: ModestyLevel = ModestyLevel.MODERATE
    aesthetic_tags: list[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    in_stock: bool = True
    size_range: list[str] = Field(default_factory=list)
    data_source: str = "manual"
    data_license: DataLicenseType = DataLicenseType.OWNED
    commercial_use_ok: bool = True

class ProductRead(ProductCreate):
    id: UUID = Field(default_factory=uuid4)
    scraped_at: Optional[datetime] = None
    last_verified: Optional[datetime] = None

class TrendSignalEntry(StyleIQBase):
    signal_type: str
    signal_value: float
    signal_date: datetime = Field(default_factory=datetime.utcnow)
    source: str
    raw_data: Optional[dict] = None

class TrendScore(StyleIQBase):
    popularity_score: float = Field(..., ge=0.0, le=100.0)
    growth_score: float = Field(..., ge=0.0, le=100.0)
    cross_brand_score: float = Field(..., ge=0.0, le=100.0)
    search_score: float = Field(..., ge=0.0, le=100.0)
    seasonal_score: float = Field(..., ge=0.0, le=100.0)
    total_score: float = Field(..., ge=0.0, le=100.0)
    score_version: str = "v1.0"
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    signal_count: int = 0

class TrendBase(StyleIQBase):
    name: str
    category: TrendCategory
    description: Optional[str] = None
    season: Optional[Season] = None
    year: Optional[int] = Field(None, ge=2020, le=2030)
    status: TrendStatus = TrendStatus.EMERGING
    geographic_scope: TrendGeography = TrendGeography.PAKISTAN_NATIONAL

class TrendCreate(TrendBase):
    signals: list[TrendSignalEntry] = Field(default_factory=list)
    score: Optional[TrendScore] = None

class TrendRead(TrendCreate):
    id: UUID = Field(default_factory=uuid4)
    detected_at: datetime = Field(default_factory=datetime.utcnow)

class TrendForecast(StyleIQBase):
    forecast_name: str
    forecast_type: TrendCategory
    probability: float = Field(..., ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    forecast_horizon: str
    supporting_signals: list[str] = Field(default_factory=list)
    uncertainty_notes: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = "v1.0"

class OutfitComponent(StyleIQBase):
    role: str
    description: str
    product_id: Optional[UUID] = None
    brand_slug: Optional[str] = None
    estimated_price: Optional[int] = Field(None, ge=0)
    where_to_find: Optional[str] = None

class OutfitRecommendation(StyleIQBase):
    id: UUID = Field(default_factory=uuid4)
    occasion: Occasion
    season: Season
    components: list[OutfitComponent] = Field(..., min_length=1)
    total_estimated_price: int = Field(..., ge=0)
    modesty_level: ModestyLevel
    aesthetic_tags: list[str] = Field(default_factory=list)
    why_recommended: str
    style_match_score: float = Field(..., ge=0.0, le=100.0)
    budget_match_score: float = Field(..., ge=0.0, le=100.0)
    modesty_match_score: float = Field(..., ge=0.0, le=100.0)
    trend_relevance_score: float = Field(..., ge=0.0, le=100.0)
    critic_passed: bool = False
    critic_notes: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def overall_score(self) -> float:
        return round(
            (self.style_match_score * 0.4)
            + (self.budget_match_score * 0.25)
            + (self.modesty_match_score * 0.25)
            + (self.trend_relevance_score * 0.10), 1
        )
