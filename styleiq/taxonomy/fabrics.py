"""
STYLEIQ Fabric Taxonomy
────────────────────────
All fabric types with season suitability and Pakistani context.
"""

FABRICS = [
    # ── Summer ────────────────────────────────────────────────────────────
    dict(key="lawn", label="Lawn", season_tags=["summer"],
         metadata_json={
             "description": "Lightweight printed cotton — the most popular Pakistani summer fabric",
             "breathability": "very high", "care": "machine wash",
             "pk_context": "Lawn season (Apr-Aug) is Pakistan's biggest fashion commercial event",
             "variants": ["printed lawn", "embroidered lawn", "digital print lawn"]
         }),

    dict(key="cotton", label="Cotton", season_tags=["summer", "all_season"],
         metadata_json={
             "description": "Breathable natural fabric, versatile year-round",
             "breathability": "high", "care": "machine wash",
             "variants": ["plain cotton", "printed cotton", "cotton blend"]
         }),

    dict(key="voile", label="Voile", season_tags=["summer"],
         metadata_json={
             "description": "Sheer lightweight cotton — popular for dupattas and overlays",
             "breathability": "very high", "sheerness": "high"
         }),

    dict(key="chiffon", label="Chiffon", season_tags=["summer", "all_season"],
         metadata_json={
             "description": "Lightweight flowy fabric — popular for dupattas and formal tops",
             "drape": "excellent", "sheerness": "medium",
             "pk_context": "Common for formal eastern and bridal wear"
         }),

    dict(key="linen", label="Linen", season_tags=["summer", "transitional"],
         metadata_json={
             "description": "Natural textured fabric, slightly heavier than lawn",
             "breathability": "high", "texture": "slightly rough",
             "pk_context": "Popular in premium summer and transitional collections"
         }),

    dict(key="georgette", label="Georgette", season_tags=["all_season"],
         metadata_json={
             "description": "Crinkled sheer fabric with good drape",
             "drape": "excellent", "weight": "light to medium"
         }),

    dict(key="organza", label="Organza", season_tags=["all_season"],
         metadata_json={
             "description": "Crisp sheer fabric — popular for formal overlays",
             "stiffness": "high", "sheerness": "high",
             "pk_context": "Used heavily in bridal and formal Pakistani wear"
         }),

    # ── All-season ────────────────────────────────────────────────────────
    dict(key="karandi", label="Karandi", season_tags=["all_season", "winter"],
         metadata_json={
             "description": "Medium-weight Pakistani fabric between summer and winter weight",
             "breathability": "medium", "warmth": "light",
             "pk_context": "Popular transitional fabric — Oct to Mar in most cities"
         }),

    dict(key="jersey", label="Jersey / Knit", season_tags=["all_season"],
         metadata_json={
             "description": "Stretchy knit fabric — comfortable everyday wear",
             "stretch": "high", "care": "machine wash"
         }),

    dict(key="denim", label="Denim", season_tags=["all_season", "winter"],
         metadata_json={
             "description": "Classic woven cotton — primarily western category",
             "durability": "high", "care": "machine wash cold"
         }),

    dict(key="silk", label="Silk", season_tags=["all_season"],
         metadata_json={
             "description": "Luxurious natural fabric — formal and bridal wear",
             "drape": "excellent", "sheen": "high",
             "pk_context": "Common in premium and bridal Pakistani collections"
         }),

    # ── Winter ────────────────────────────────────────────────────────────
    dict(key="khaddar", label="Khaddar", season_tags=["winter", "transitional"],
         metadata_json={
             "description": "Hand-woven coarse cotton — traditional Pakistani winter fabric",
             "warmth": "medium", "texture": "coarse",
             "pk_context": "Distinctly Pakistani — major brand launches Oct-Jan"
         }),

    dict(key="wool", label="Wool / Tweed", season_tags=["winter"],
         metadata_json={
             "description": "Heavy natural fibre — warmth-focused garments",
             "warmth": "high", "care": "dry clean or hand wash"
         }),

    dict(key="velvet", label="Velvet", season_tags=["winter"],
         metadata_json={
             "description": "Luxurious pile fabric — heavily used in Pakistani formal wear",
             "warmth": "medium", "sheen": "high",
             "pk_context": "Peak season Nov-Jan — wedding season and formal events"
         }),

    dict(key="fleece", label="Fleece", season_tags=["winter"],
         metadata_json={
             "description": "Synthetic warm fabric — casual winterwear",
             "warmth": "high", "care": "machine wash"
         }),
]
