import pytest
from uuid import uuid4
from pydantic import ValidationError

class TestConfig:
    def test_settings_load(self):
        from styleiq.config import settings
        assert settings.app_name == "STYLEIQ"

    def test_data_directories_exist(self):
        from styleiq.config import settings
        assert settings.data_dir.exists()

    def test_environment_defaults(self):
        from styleiq.config import settings
        from styleiq.config import Environment
        assert settings.env == Environment.DEVELOPMENT

    def test_claude_not_configured_with_placeholder(self):
        from styleiq.config import settings
        result = settings.claude.is_configured
        assert isinstance(result, bool)

    def test_database_url_is_sqlite(self):
        from styleiq.config import settings
        assert settings.database.is_sqlite

    def test_image_retention_default_false(self):
        from styleiq.config import settings
        assert settings.images.retain_uploaded is False

    def test_data_collection_default_disabled(self):
        from styleiq.config import settings
        assert settings.data_collection.enabled is False

class TestEnums:
    def test_modesty_level_ordering(self):
        from styleiq.schemas.enums import ModestyLevel
        assert ModestyLevel.FULL_MODEST > ModestyLevel.MINIMAL

    def test_occasion_university_exists(self):
        from styleiq.schemas.enums import Occasion
        assert Occasion.UNIVERSITY.value == "university"

    def test_all_pakistani_cities_defined(self):
        from styleiq.schemas.enums import PakistaniCity
        cities = {c.value for c in PakistaniCity}
        for expected in ["karachi", "lahore", "islamabad", "rawalpindi", "peshawar"]:
            assert expected in cities

    def test_wedding_occasions_complete(self):
        from styleiq.schemas.enums import Occasion
        occasions = {o.value for o in Occasion}
        for event in ["mehndi", "dholki", "nikkah", "baraat", "walima"]:
            assert event in occasions

    def test_trend_status_lifecycle(self):
        from styleiq.schemas.enums import TrendStatus
        statuses = {s.value for s in TrendStatus}
        assert "emerging" in statuses
        assert "rising" in statuses
        assert "peaking" in statuses
        assert "declining" in statuses

class TestOnboardingProfile:
    def test_valid_profile_creates(self):
        from styleiq.schemas import OnboardingProfile, ModestyLevel, PakistaniCity
        profile = OnboardingProfile(
            age=22, city=PakistaniCity.ISLAMABAD,
            modesty_level=ModestyLevel.MODERATE,
            budget_min=2000, budget_max=8000,
        )
        assert profile.age == 22
        assert profile.budget_max == 8000

    def test_budget_min_cannot_exceed_max(self):
        from styleiq.schemas import OnboardingProfile
        with pytest.raises(ValidationError) as exc_info:
            OnboardingProfile(budget_min=10000, budget_max=5000)
        assert "budget_min cannot exceed budget_max" in str(exc_info.value)

    def test_body_fields_all_optional(self):
        from styleiq.schemas import OnboardingProfile
        profile = OnboardingProfile()
        assert profile.height_cm is None
        assert profile.weight_optional is None
        assert profile.body_notes is None

    def test_body_recommendations_opt_in(self):
        from styleiq.schemas import OnboardingProfile
        profile = OnboardingProfile()
        assert profile.enable_body_based_recommendations is False

    def test_invalid_aesthetic_rejected(self):
        from styleiq.schemas import OnboardingProfile
        with pytest.raises(ValidationError):
            OnboardingProfile(preferred_aesthetics=["totally_made_up_aesthetic"])

    def test_valid_aesthetics_accepted(self):
        from styleiq.schemas import OnboardingProfile
        profile = OnboardingProfile(preferred_aesthetics=["minimal", "feminine", "contemporary"])
        assert len(profile.preferred_aesthetics) == 3

    def test_default_city_islamabad(self):
        from styleiq.schemas import OnboardingProfile
        profile = OnboardingProfile()
        assert profile.city == "islamabad"

class TestStyleDNA:
    def _make_dna(self, **kwargs):
        from styleiq.schemas import StyleDNA
        defaults = dict(
            user_id=uuid4(),
            minimal=82.0, feminine=78.0, traditional=65.0,
            contemporary=71.0, romantic=60.0, classic=55.0,
            streetwear=22.0, eastern_affinity=64.0, modesty_score=80.0,
        )
        defaults.update(kwargs)
        return StyleDNA(**defaults)

    def test_top_aesthetics_returns_three(self):
        dna = self._make_dna()
        assert len(dna.top_aesthetics) == 3

    def test_top_aesthetics_sorted_descending(self):
        dna = self._make_dna()
        scores = [score for _, score in dna.top_aesthetics]
        assert scores == sorted(scores, reverse=True)

    def test_style_archetype_soft_minimalist(self):
        dna = self._make_dna(
            minimal=90.0, feminine=85.0, traditional=10.0,
            contemporary=10.0, romantic=10.0, classic=10.0,
            streetwear=10.0, bohemian=10.0
        )
        assert dna.style_archetype == "Soft Minimalist"

    def test_style_archetype_never_crashes(self):
        dna = self._make_dna()
        archetype = dna.style_archetype
        assert isinstance(archetype, str)
        assert len(archetype) > 0

    def test_scores_bounded_0_to_100(self):
        from styleiq.schemas import StyleDNA
        dna = StyleDNA(user_id=uuid4())
        summary = dna.as_summary_dict()
        for name, score in summary.items():
            assert 0.0 <= score <= 100.0

    def test_scores_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            self._make_dna(minimal=150.0)
        with pytest.raises(ValidationError):
            self._make_dna(feminine=-5.0)

class TestBrandSchema:
    def test_valid_brand_creates(self):
        from styleiq.schemas import BrandCreate, BrandTier
        brand = BrandCreate(
            name="Khaadi", slug="khaadi", tier=BrandTier.PREMIUM_MID,
            typical_price_min=3000, typical_price_max=15000, modesty_score=3.5,
        )
        assert brand.name == "Khaadi"

    def test_slug_must_be_lowercase(self):
        from styleiq.schemas import BrandCreate, BrandTier
        with pytest.raises(ValidationError):
            BrandCreate(name="Test", slug="Khaadi Brand", tier=BrandTier.PREMIUM_MID)

    def test_price_range_validation(self):
        from styleiq.schemas import BrandCreate, BrandTier
        with pytest.raises(ValidationError):
            BrandCreate(
                name="Test", slug="test", tier=BrandTier.MASS_MARKET,
                typical_price_min=10000, typical_price_max=5000,
            )

class TestOutfitSchema:
    def test_overall_score_computed_correctly(self):
        from styleiq.schemas import OutfitRecommendation, OutfitComponent, Occasion, Season, ModestyLevel
        outfit = OutfitRecommendation(
            occasion=Occasion.UNIVERSITY, season=Season.SUMMER,
            components=[OutfitComponent(role="top", description="Test shirt", estimated_price=2000)],
            total_estimated_price=2000, modesty_level=ModestyLevel.MODERATE,
            why_recommended="Test reason",
            style_match_score=80.0, budget_match_score=90.0,
            modesty_match_score=100.0, trend_relevance_score=50.0,
        )
        assert outfit.overall_score == 84.5

    def test_outfit_requires_at_least_one_component(self):
        from styleiq.schemas import OutfitRecommendation, Occasion, Season, ModestyLevel
        with pytest.raises(ValidationError):
            OutfitRecommendation(
                occasion=Occasion.UNIVERSITY, season=Season.SUMMER,
                components=[], total_estimated_price=0,
                modesty_level=ModestyLevel.MODERATE,
                why_recommended="No items",
                style_match_score=80.0, budget_match_score=80.0,
                modesty_match_score=80.0, trend_relevance_score=80.0,
            )
