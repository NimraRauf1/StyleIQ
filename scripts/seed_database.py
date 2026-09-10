"""
Seed the STYLEIQ database with initial Pakistani fashion data.
Run: python scripts/seed_database.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from styleiq.database.connection import SessionLocal, create_tables, verify_connection
from styleiq.database.models import Brand, Trend, TrendSignal, DataSource
from styleiq.logger import setup_logging, get_logger

setup_logging(level="INFO", log_to_file=False)
log = get_logger(__name__)

BRANDS = [
    dict(name="Khaadi", slug="khaadi", tier="premium_mid", typical_price_min=3000, typical_price_max=18000,
         modesty_score=3.5, eastern_western_ratio=0.6, description="Contemporary Pakistani fashion with bohemian flair.",
         style_tags=["bohemian", "contemporary", "colorful"], instagram_handle="khaadi", website="https://khaadi.com"),
    dict(name="Sapphire", slug="sapphire", tier="premium_mid", typical_price_min=2500, typical_price_max=15000,
         modesty_score=3.0, eastern_western_ratio=0.5, description="Modern Pakistani fashion balancing eastern and western.",
         style_tags=["contemporary", "minimal", "fusion"], instagram_handle="sapphirepk", website="https://sapphire.pk"),
    dict(name="Limelight", slug="limelight", tier="mass_market", typical_price_min=1500, typical_price_max=6000,
         modesty_score=3.5, eastern_western_ratio=0.55, description="Affordable everyday Pakistani fashion.",
         style_tags=["casual", "colorful", "everyday"], instagram_handle="limelightpk", website="https://limelightpk.com"),
    dict(name="Gul Ahmed", slug="gul-ahmed", tier="mass_market", typical_price_min=1800, typical_price_max=8000,
         modesty_score=3.5, eastern_western_ratio=0.7, description="Classic Pakistani lawn and fabric house.",
         style_tags=["traditional", "lawn", "classic"], instagram_handle="gulahmedofficial", website="https://gulahmedshop.com"),
    dict(name="Nishat Linen", slug="nishat", tier="mass_market", typical_price_min=2000, typical_price_max=9000,
         modesty_score=3.5, eastern_western_ratio=0.65, description="Quality Pakistani linen and fabric collections.",
         style_tags=["classic", "quality", "traditional"], instagram_handle="nishatlinen", website="https://nishat.net"),
    dict(name="Sana Safinaz", slug="sana-safinaz", tier="premium_mid", typical_price_min=4000, typical_price_max=25000,
         modesty_score=3.0, eastern_western_ratio=0.45, description="Sophisticated and chic Pakistani fashion.",
         style_tags=["sophisticated", "chic", "contemporary"], instagram_handle="sanasafinaz", website="https://sanasafinaz.com"),
    dict(name="Zellbury", slug="zellbury", tier="mass_market", typical_price_min=1500, typical_price_max=6000,
         modesty_score=3.5, eastern_western_ratio=0.6, description="Affordable family fashion brand.",
         style_tags=["affordable", "casual", "family"], instagram_handle="zellbury", website="https://zellbury.com"),
    dict(name="Beechtree", slug="beechtree", tier="mass_market", typical_price_min=1800, typical_price_max=7000,
         modesty_score=3.5, eastern_western_ratio=0.55, description="Youth-oriented modest Pakistani fashion.",
         style_tags=["youth", "modest", "colorful"], instagram_handle="beechtreepk", website="https://beechtree.pk"),
    dict(name="Generation", slug="generation", tier="premium_mid", typical_price_min=3000, typical_price_max=15000,
         modesty_score=4.0, eastern_western_ratio=0.75, description="Heritage Pakistani brand with strong cultural identity.",
         style_tags=["traditional", "heritage", "cultural"], instagram_handle="generationpk", website="https://generation.com.pk"),
    dict(name="Alkaram Studio", slug="alkaram", tier="mass_market", typical_price_min=1500, typical_price_max=7000,
         modesty_score=3.5, eastern_western_ratio=0.65, description="Popular lawn and fabric collections.",
         style_tags=["lawn", "printed", "colorful"], instagram_handle="alkaramstudio", website="https://alkaramstudio.com"),
    dict(name="Maria B", slug="maria-b", tier="premium", typical_price_min=8000, typical_price_max=80000,
         modesty_score=3.5, eastern_western_ratio=0.8, description="Luxury Pakistani bridal and pret fashion.",
         style_tags=["luxury", "bridal", "embroidered"], instagram_handle="mariabofficial", website="https://mariab.pk"),
    dict(name="Asim Jofa", slug="asim-jofa", tier="premium", typical_price_min=10000, typical_price_max=100000,
         modesty_score=3.5, eastern_western_ratio=0.85, description="Premium luxury Pakistani fashion.",
         style_tags=["luxury", "embroidered", "formal"], instagram_handle="asimjofaofficial"),
    dict(name="Outfitters", slug="outfitters", tier="western_casual", typical_price_min=2000, typical_price_max=10000,
         modesty_score=2.0, eastern_western_ratio=0.15, description="Youth western fashion brand.",
         style_tags=["western", "youth", "streetwear"], instagram_handle="outfitterspk", website="https://outfitters.com.pk"),
    dict(name="Breakout", slug="breakout", tier="western_casual", typical_price_min=2000, typical_price_max=12000,
         modesty_score=2.0, eastern_western_ratio=0.2, description="Contemporary western casual fashion.",
         style_tags=["western", "casual", "contemporary"], instagram_handle="breakoutpk", website="https://breakout.com.pk"),
    dict(name="Ethnic", slug="ethnic", tier="premium_mid", typical_price_min=2500, typical_price_max=12000,
         modesty_score=3.5, eastern_western_ratio=0.7, description="Modern take on traditional Pakistani fashion.",
         style_tags=["ethnic", "traditional", "modern"], instagram_handle="ethnicbyoutfitters"),
]

TRENDS = [
    dict(name="Chocolate Brown", category="color", status="rising", season="winter", year=2025,
         description="Deep warm brown tones appearing across multiple Pakistani collections.",
         signals=[
             dict(signal_type="brand_appearance", signal_value=8.0, source="manual_catalog_review",
                  raw_data={"brands": ["khaadi", "sapphire", "limelight", "nishat", "gul-ahmed", "ethnic", "generation", "beechtree"]}),
             dict(signal_type="search_volume_growth", signal_value=34.0, source="google_trends_pk",
                  raw_data={"keyword": "chocolate brown dress pakistan", "growth_pct": 34}),
         ]),
    dict(name="Wide-Leg Silhouette", category="silhouette", status="peaking", season="all", year=2025,
         description="Wide-leg trousers and palazzos dominating both eastern and western categories.",
         signals=[
             dict(signal_type="brand_appearance", signal_value=10.0, source="manual_catalog_review",
                  raw_data={"brands": ["khaadi", "sapphire", "outfitters", "breakout", "ethnic", "generation", "limelight", "sana-safinaz", "zellbury", "beechtree"]}),
             dict(signal_type="search_volume_growth", signal_value=52.0, source="google_trends_pk",
                  raw_data={"keyword": "wide leg pants pakistan", "growth_pct": 52}),
         ]),
    dict(name="Minimal Embroidery", category="embellishment", status="rising", season="summer", year=2025,
         description="Shift from heavy embroidery to delicate, minimal thread work and motifs.",
         signals=[
             dict(signal_type="brand_appearance", signal_value=6.0, source="manual_catalog_review",
                  raw_data={"brands": ["generation", "sapphire", "ethnic", "maria-b", "sana-safinaz", "khaadi"]}),
         ]),
    dict(name="Sage Green", category="color", status="emerging", season="spring", year=2025,
         description="Muted sage and olive greens appearing in spring lawn collections.",
         signals=[
             dict(signal_type="brand_appearance", signal_value=5.0, source="manual_catalog_review",
                  raw_data={"brands": ["nishat", "gul-ahmed", "alkaram", "limelight", "beechtree"]}),
             dict(signal_type="search_volume_growth", signal_value=28.0, source="google_trends_pk",
                  raw_data={"keyword": "sage green lawn suit pakistan", "growth_pct": 28}),
         ]),
    dict(name="Clean Girl Aesthetic", category="aesthetic", status="rising", season="all", year=2025,
         description="Minimal makeup, sleek hair, neutral tones — clean effortless styling gaining momentum.",
         signals=[
             dict(signal_type="brand_appearance", signal_value=7.0, source="manual_catalog_review",
                  raw_data={"brands": ["sapphire", "khaadi", "limelight", "zellbury", "beechtree", "nishat", "generation"]}),
         ]),
]

DATA_SOURCES = [
    dict(name="Manual Curation", source_type="manual", scraping_permitted=False, commercial_use_ok=True,
         tos_reviewed=True, robots_checked=True, notes="Hand-curated data owned by STYLEIQ."),
    dict(name="Google Trends via pytrends", source_type="api", url="https://trends.google.com",
         scraping_permitted=False, commercial_use_ok=False, api_available=True, requires_auth=False,
         tos_reviewed=True, robots_checked=True,
         notes="Unofficial API. Free for personal/research use. Check ToS before commercial use."),
    dict(name="Open-Meteo Weather", source_type="api", url="https://open-meteo.com",
         scraping_permitted=False, commercial_use_ok=True, api_available=True, requires_auth=False,
         tos_reviewed=True, robots_checked=True, notes="Free, open-source weather API. No key needed."),
]

def seed():
    create_tables()
    if not verify_connection():
        log.error("Cannot connect to database")
        return

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Brand).count() > 0:
            log.info("Database already seeded — skipping")
            return

        log.info("Seeding brands...")
        for b in BRANDS:
            db.add(Brand(**b))
        db.commit()
        log.info("✓ {n} brands added", n=len(BRANDS))

        log.info("Seeding trends...")
        for t in TRENDS:
            signals_data = t.pop("signals", [])
            trend = Trend(**t)
            db.add(trend)
            db.flush()
            for s in signals_data:
                db.add(TrendSignal(trend_id=trend.id, **s))
        db.commit()
        log.info("✓ {n} trends added", n=len(TRENDS))

        log.info("Seeding data sources...")
        for ds in DATA_SOURCES:
            db.add(DataSource(**ds))
        db.commit()
        log.info("✓ {n} data sources added", n=len(DATA_SOURCES))

        log.info("✓ Database seeded successfully")
        log.info("  Brands: {b}", b=db.query(Brand).count())
        log.info("  Trends: {t}", t=db.query(Trend).count())
        log.info("  Signals: {s}", s=db.query(TrendSignal).count())

    except Exception as e:
        db.rollback()
        log.error("Seeding failed: {e}", e=str(e))
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
