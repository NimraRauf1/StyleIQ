"""
STYLEIQ Database Models
────────────────────────
All SQLAlchemy ORM models (database tables).

Each class = one database table.
Each class attribute = one column.

Relationships defined here tell SQLAlchemy how tables connect,
so you can do: user.recommendations instead of writing JOIN queries.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON, Boolean, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from styleiq.database.connection import Base


# ── Helper: generate UUID as string ───────────────────────────────────────
def _uuid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.utcnow()


# ── 1. Users ───────────────────────────────────────────────────────────────
class User(Base):
    """
    A STYLEIQ user account.
    One user has one StyleProfile, one StyleDNA,
    and many Interactions and Recommendations.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    # Relationships
    style_profile: Mapped[Optional["StyleProfile"]] = relationship(
        "StyleProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    style_dna_records: Mapped[list["StyleDNA"]] = relationship(
        "StyleDNA", back_populates="user", cascade="all, delete-orphan"
    )
    style_preferences: Mapped[list["StylePreference"]] = relationship(
        "StylePreference", back_populates="user", cascade="all, delete-orphan"
    )
    garments: Mapped[list["Garment"]] = relationship(
        "Garment", back_populates="user", cascade="all, delete-orphan"
    )
    interactions: Mapped[list["Interaction"]] = relationship(
        "Interaction", back_populates="user", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"


# ── 2. StyleProfile ────────────────────────────────────────────────────────
class StyleProfile(Base):
    """
    User's personal context — city, age, budget, occasions.
    One-to-one with User.
    """
    __tablename__ = "style_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False)

    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    lifestyle: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Budget in PKR
    budget_min: Mapped[int] = mapped_column(Integer, default=0)
    budget_max: Mapped[int] = mapped_column(Integer, default=10000)

    # Style preferences
    modesty_level: Mapped[int] = mapped_column(Integer, default=2)
    eastern_western_pref: Mapped[float] = mapped_column(Float, default=0.5)

    # Body (all optional — user must opt in)
    height_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enable_body_recommendations: Mapped[bool] = mapped_column(Boolean, default=False)

    # JSON fields for lists
    preferred_aesthetics: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    preferred_colors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    disliked_colors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    preferred_occasions: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    preferred_brands: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    disliked_brands: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="style_profile")

    def __repr__(self) -> str:
        return f"<StyleProfile user={self.user_id} city={self.city}>"


# ── 3. StyleDNA ────────────────────────────────────────────────────────────
class StyleDNA(Base):
    """
    User's evolving style fingerprint.
    Multiple records per user — versioned over time.
    The latest version is the current DNA.
    """
    __tablename__ = "style_dna"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)

    # Aesthetic dimensions (0.0 - 100.0)
    minimal: Mapped[float] = mapped_column(Float, default=50.0)
    maximalist: Mapped[float] = mapped_column(Float, default=50.0)
    feminine: Mapped[float] = mapped_column(Float, default=50.0)
    androgynous: Mapped[float] = mapped_column(Float, default=50.0)
    traditional: Mapped[float] = mapped_column(Float, default=50.0)
    contemporary: Mapped[float] = mapped_column(Float, default=50.0)
    romantic: Mapped[float] = mapped_column(Float, default=50.0)
    edgy: Mapped[float] = mapped_column(Float, default=50.0)
    streetwear: Mapped[float] = mapped_column(Float, default=50.0)
    classic: Mapped[float] = mapped_column(Float, default=50.0)
    bohemian: Mapped[float] = mapped_column(Float, default=50.0)

    eastern_affinity: Mapped[float] = mapped_column(Float, default=50.0)
    modesty_score: Mapped[float] = mapped_column(Float, default=50.0)
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)

    computed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="style_dna_records")

    def __repr__(self) -> str:
        return f"<StyleDNA user={self.user_id} v{self.version}>"


# ── 4. StylePreference ─────────────────────────────────────────────────────
class StylePreference(Base):
    """
    Individual preference entries that build up Style DNA.
    e.g. liked color 'beige', disliked brand 'xyz'
    """
    __tablename__ = "style_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    pref_type: Mapped[str] = mapped_column(String(50), nullable=False)
    pref_value: Mapped[str] = mapped_column(String(200), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="style_preferences")

    def __repr__(self) -> str:
        return f"<StylePreference {self.pref_type}:{self.pref_value} ({self.sentiment})>"


# ── 5. Brand ───────────────────────────────────────────────────────────────
class Brand(Base):
    """
    A Pakistani (or international) fashion brand.
    Central entity — products and brand profiles belong to brands.
    """
    __tablename__ = "brands"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(50), default="Pakistan")
    tier: Mapped[str] = mapped_column(String(30), nullable=False)

    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    instagram_handle: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Style characteristics
    style_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    typical_price_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    typical_price_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    modesty_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    eastern_western_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Target audience
    target_age_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_age_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Data provenance
    data_source: Mapped[str] = mapped_column(String(50), default="manual")
    data_license: Mapped[str] = mapped_column(String(50), default="owned")
    commercial_use_ok: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="brand", cascade="all, delete-orphan"
    )
    brand_profiles: Mapped[list["BrandProfile"]] = relationship(
        "BrandProfile", back_populates="brand", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Brand {self.name} ({self.tier})>"


# ── 6. BrandProfile ────────────────────────────────────────────────────────
class BrandProfile(Base):
    """
    Computed seasonal profile for a brand.
    Auto-updated when new product data is collected.
    """
    __tablename__ = "brand_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id"), nullable=False)

    season: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    common_colors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    common_silhouettes: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    common_fabrics: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    common_occasions: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    trend_alignment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    computed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="brand_profiles")

    def __repr__(self) -> str:
        return f"<BrandProfile {self.brand_id} {self.season}/{self.year}>"


# ── 7. Product ─────────────────────────────────────────────────────────────
class Product(Base):
    """
    A single fashion item from a brand.
    The core catalog entity — what gets recommended.
    """
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    brand_id: Mapped[str] = mapped_column(String(36), ForeignKey("brands.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Classification
    garment_family: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Pricing
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    original_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Style attributes
    fabric: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    colors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    silhouette: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    neckline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sleeve: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    embellishment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    modesty_level: Mapped[int] = mapped_column(Integer, default=2)

    # Tags
    occasion_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    season_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    aesthetic_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    size_range: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # URLs
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    product_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)

    # Data provenance
    data_source: Mapped[str] = mapped_column(String(50), default="manual")
    data_license: Mapped[str] = mapped_column(String(50), default="owned")
    commercial_use_ok: Mapped[bool] = mapped_column(Boolean, default=True)

    scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_verified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    price_history: Mapped[list["PriceHistory"]] = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product {self.name} PKR {self.price}>"


# ── 8. Garment (user wardrobe) ─────────────────────────────────────────────
class Garment(Base):
    """
    A clothing item in the user's wardrobe or uploaded for analysis.
    Analyzed by the Image Analyzer Agent.
    """
    __tablename__ = "garments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    colors: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    fabric: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    silhouette: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Image
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Vision analysis results
    vision_attributes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    aesthetic_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    modesty_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    source: Mapped[str] = mapped_column(String(30), default="uploaded")
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="garments")

    def __repr__(self) -> str:
        return f"<Garment {self.category} user={self.user_id}>"


# ── 9. Trend ───────────────────────────────────────────────────────────────
class Trend(Base):
    """
    A detected fashion trend.
    Has signals (evidence) and scores (computed from signals).
    """
    __tablename__ = "trends"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    season: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="emerging")
    geographic_scope: Mapped[str] = mapped_column(String(30), default="pk_national")

    detected_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    signals: Mapped[list["TrendSignal"]] = relationship(
        "TrendSignal", back_populates="trend", cascade="all, delete-orphan"
    )
    scores: Mapped[list["TrendScore"]] = relationship(
        "TrendScore", back_populates="trend", cascade="all, delete-orphan"
    )
    forecasts: Mapped[list["Forecast"]] = relationship(
        "Forecast", back_populates="trend", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Trend {self.name} ({self.status})>"


# ── 10. TrendSignal ────────────────────────────────────────────────────────
class TrendSignal(Base):
    """
    A single measurable data point for a trend.
    e.g. 'brand_appearance: 8 brands feature chocolate brown'
    """
    __tablename__ = "trend_signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trend_id: Mapped[str] = mapped_column(String(36), ForeignKey("trends.id"), nullable=False)

    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_value: Mapped[float] = mapped_column(Float, nullable=False)
    signal_date: Mapped[datetime] = mapped_column(DateTime, default=_now)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    trend: Mapped["Trend"] = relationship("Trend", back_populates="signals")

    def __repr__(self) -> str:
        return f"<TrendSignal {self.signal_type}={self.signal_value}>"


# ── 11. TrendScore ─────────────────────────────────────────────────────────
class TrendScore(Base):
    """
    Computed score for a trend at a point in time.
    Every number here is computed by Python, not by Claude.
    """
    __tablename__ = "trend_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trend_id: Mapped[str] = mapped_column(String(36), ForeignKey("trends.id"), nullable=False)

    popularity_score: Mapped[float] = mapped_column(Float, default=0.0)
    growth_score: Mapped[float] = mapped_column(Float, default=0.0)
    cross_brand_score: Mapped[float] = mapped_column(Float, default=0.0)
    search_score: Mapped[float] = mapped_column(Float, default=0.0)
    seasonal_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    signal_count: Mapped[int] = mapped_column(Integer, default=0)
    score_version: Mapped[str] = mapped_column(String(10), default="v1.0")

    computed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    trend: Mapped["Trend"] = relationship("Trend", back_populates="scores")

    def __repr__(self) -> str:
        return f"<TrendScore total={self.total_score} v={self.score_version}>"


# ── 12. Forecast ───────────────────────────────────────────────────────────
class Forecast(Base):
    """
    A trend prediction with transparent uncertainty.
    Generated by the Trend Forecasting Agent.
    """
    __tablename__ = "forecasts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    trend_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("trends.id"), nullable=True)

    forecast_name: Mapped[str] = mapped_column(String(200), nullable=False)
    forecast_type: Mapped[str] = mapped_column(String(50), nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(10), nullable=False)
    forecast_horizon: Mapped[str] = mapped_column(String(30), nullable=False)
    supporting_signals: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    uncertainty_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_version: Mapped[str] = mapped_column(String(10), default="v1.0")

    generated_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    trend: Mapped[Optional["Trend"]] = relationship("Trend", back_populates="forecasts")

    def __repr__(self) -> str:
        return f"<Forecast {self.forecast_name} p={self.probability}>"


# ── 13. Outfit ─────────────────────────────────────────────────────────────
class Outfit(Base):
    """
    A complete recommended outfit.
    Components stored as JSON (top, bottom, layer, shoes, accessories).
    """
    __tablename__ = "outfits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)

    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    occasion: Mapped[str] = mapped_column(String(50), nullable=False)
    season: Mapped[str] = mapped_column(String(20), nullable=False)

    components: Mapped[list] = mapped_column(JSON, default=list)
    total_price: Mapped[int] = mapped_column(Integer, default=0)
    modesty_level: Mapped[int] = mapped_column(Integer, default=2)
    aesthetic_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation", back_populates="outfit"
    )

    def __repr__(self) -> str:
        return f"<Outfit {self.occasion} PKR {self.total_price}>"


# ── 14. Recommendation ─────────────────────────────────────────────────────
class Recommendation(Base):
    """
    A recommendation delivered to a user.
    Stores match scores and the critic's verdict.
    """
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    outfit_id: Mapped[str] = mapped_column(String(36), ForeignKey("outfits.id"), nullable=False)

    occasion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Match scores
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    style_match: Mapped[float] = mapped_column(Float, default=0.0)
    budget_match: Mapped[float] = mapped_column(Float, default=0.0)
    modesty_match: Mapped[float] = mapped_column(Float, default=0.0)
    trend_match: Mapped[float] = mapped_column(Float, default=0.0)

    # Critic verdict
    critic_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    critic_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    generated_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recommendations")
    outfit: Mapped["Outfit"] = relationship("Outfit", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<Recommendation user={self.user_id} score={self.match_score}>"


# ── 15. Interaction ────────────────────────────────────────────────────────
class Interaction(Base):
    """
    Records every user action — like, dislike, save, skip.
    These drive Style DNA updates.
    """
    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    interaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="interactions")

    def __repr__(self) -> str:
        return f"<Interaction {self.interaction_type} on {self.target_type}>"


# ── 16. PriceHistory ───────────────────────────────────────────────────────
class PriceHistory(Base):
    """
    Tracks price changes for a product over time.
    Used for discount detection and price alerts.
    """
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="price_history")

    def __repr__(self) -> str:
        return f"<PriceHistory PKR {self.price} at {self.recorded_at}>"


# ── 17. DataSource ─────────────────────────────────────────────────────────
class DataSource(Base):
    """
    Registry of every data source used by STYLEIQ.
    Tracks legal status — critical for commercialization.
    """
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Legal status
    robots_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    tos_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    scraping_permitted: Mapped[bool] = mapped_column(Boolean, default=False)
    commercial_use_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    api_available: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=False)
    rate_limit: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    attribution_required: Mapped[bool] = mapped_column(Boolean, default=False)
    attribution_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    def __repr__(self) -> str:
        return f"<DataSource {self.name} ({self.source_type})>"


# ── 18. TaxonomyEntry ──────────────────────────────────────────────────────
class TaxonomyEntry(Base):
    """
    A single entry in the fashion taxonomy.
    Stores garment categories, fabrics, occasions, silhouettes etc.
    as structured database records so agents can query them.
    """
    __tablename__ = "taxonomy_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    taxonomy_type: Mapped[str] = mapped_column(String(30), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    family: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    season_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    occasion_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    modesty_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    formality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    __table_args__ = (
        UniqueConstraint("taxonomy_type", "key", name="uq_taxonomy_type_key"),
    )

    def __repr__(self) -> str:
        return f"<TaxonomyEntry {self.taxonomy_type}:{self.key}>"


# ── 19. ColorPalette ───────────────────────────────────────────────────────
class ColorPalette(Base):
    """
    STYLEIQ's structured color system.
    Every color has a family, hex code, and Pakistani context flag.
    """
    __tablename__ = "color_palette"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hex_code: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    family: Mapped[str] = mapped_column(String(30), nullable=False)
    is_neutral: Mapped[bool] = mapped_column(Boolean, default=False)
    is_traditional_pk: Mapped[bool] = mapped_column(Boolean, default=False)
    season_affinity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<ColorPalette {self.name} ({self.family})>"
