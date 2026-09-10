"""
STYLEIQ Garment Category Taxonomy
───────────────────────────────────
Complete hierarchy of garment categories understood by STYLEIQ.
Pakistan-first: Eastern and Modest categories are primary.
"""

GARMENT_CATEGORIES = [
    # ── EASTERN ───────────────────────────────────────────────────────────
    dict(key="eastern", label="Eastern", family="eastern", parent_key=None,
         metadata_json={"description": "Traditional Pakistani and South Asian garments"}),

    dict(key="shalwar_kameez", label="Shalwar Kameez", family="eastern", parent_key="eastern",
         season_tags=["summer", "winter", "all_season"],
         occasion_tags=["university", "office_casual", "dawat", "eid", "home"],
         metadata_json={"description": "The national dress of Pakistan — shirt with trousers"}),

    dict(key="kurta_short", label="Short Kurta", family="eastern", parent_key="eastern",
         season_tags=["summer", "all_season"],
         occasion_tags=["university", "casual", "home"],
         metadata_json={"length": "above knee", "styling": "usually paired with jeans or trousers"}),

    dict(key="kurta_midi", label="Midi Kurta", family="eastern", parent_key="eastern",
         season_tags=["summer", "all_season"],
         occasion_tags=["university", "office_casual", "brunch", "dawat"],
         metadata_json={"length": "knee to mid-calf"}),

    dict(key="kurta_long", label="Long Kurta", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         occasion_tags=["dawat", "eid", "office_formal", "formal_event"],
         modesty_min=3,
         metadata_json={"length": "below calf"}),

    dict(key="straight_shirt", label="Straight Shirt", family="eastern", parent_key="eastern",
         season_tags=["summer", "all_season"],
         occasion_tags=["university", "office_casual", "casual"],
         metadata_json={"silhouette": "straight, no waist definition"}),

    dict(key="a_line_shirt", label="A-Line Shirt", family="eastern", parent_key="eastern",
         season_tags=["summer", "all_season"],
         occasion_tags=["university", "brunch", "casual", "dawat"],
         metadata_json={"silhouette": "flares from waist or chest"}),

    dict(key="frock", label="Frock", family="eastern", parent_key="eastern",
         season_tags=["summer", "all_season"],
         occasion_tags=["casual", "dawat", "eid"],
         metadata_json={"description": "Full flared eastern dress"}),

    dict(key="anarkali", label="Anarkali", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         occasion_tags=["dawat", "eid", "formal_event", "nikkah"],
         modesty_min=3,
         metadata_json={"silhouette": "flared floor-length, Mughal-inspired"}),

    dict(key="two_piece", label="2-Piece", family="eastern", parent_key="eastern",
         season_tags=["summer", "all_season"],
         occasion_tags=["university", "casual", "dawat"],
         metadata_json={"components": ["shirt", "shalwar or trouser"]}),

    dict(key="three_piece", label="3-Piece", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         occasion_tags=["dawat", "eid", "formal_event", "nikkah", "walima"],
         modesty_min=3,
         metadata_json={"components": ["shirt", "shalwar", "dupatta"]}),

    dict(key="gharara", label="Gharara", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         occasion_tags=["mehndi", "nikkah", "baraat", "walima", "eid"],
         modesty_min=3,
         metadata_json={"description": "Wide flared divided skirt, traditional bridal/formal"}),

    dict(key="sharara", label="Sharara", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         occasion_tags=["mehndi", "nikkah", "baraat", "walima"],
         modesty_min=3,
         metadata_json={"description": "Flared trousers from knee down"}),

    dict(key="lehenga", label="Lehenga Choli", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         occasion_tags=["baraat", "walima", "mehndi", "formal_event"],
         modesty_min=2,
         metadata_json={"components": ["choli", "lehenga skirt", "dupatta"]}),

    dict(key="saree", label="Saree", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         occasion_tags=["formal_event", "walima", "baraat"],
         modesty_min=2,
         metadata_json={"draping": "6-9 yards of fabric, multiple draping styles"}),

    dict(key="unstitched", label="Unstitched Fabric", family="eastern", parent_key="eastern",
         season_tags=["summer", "winter", "all_season"],
         metadata_json={"description": "Fabric purchased for custom stitching by tailor — unique to Pakistan"}),

    dict(key="dupatta", label="Dupatta / Shawl", family="eastern", parent_key="eastern",
         season_tags=["all_season"],
         metadata_json={"description": "Scarf/veil worn with eastern outfits"}),

    # ── WESTERN ───────────────────────────────────────────────────────────
    dict(key="western", label="Western", family="western", parent_key=None,
         metadata_json={"description": "Western-style garments"}),

    dict(key="tshirt", label="T-Shirt", family="western", parent_key="western",
         season_tags=["summer"],
         occasion_tags=["university", "casual", "home"],
         metadata_json={"variants": ["basic", "graphic", "oversized"]}),

    dict(key="blouse", label="Blouse / Shirt", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["university", "office_casual", "brunch", "cafe"]),

    dict(key="crop_top", label="Crop Top", family="western", parent_key="western",
         season_tags=["summer"],
         occasion_tags=["casual", "brunch"],
         modesty_min=1),

    dict(key="jeans_straight", label="Straight Jeans", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["university", "casual", "brunch", "cafe"]),

    dict(key="jeans_wide_leg", label="Wide-Leg Jeans", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["university", "brunch", "casual"],
         metadata_json={"trend_status": "peaking 2025"}),

    dict(key="cargo_pants", label="Cargo Pants", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["university", "casual"],
         metadata_json={"trend_status": "rising 2025"}),

    dict(key="trousers", label="Trousers", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["office_formal", "office_casual", "formal_event"]),

    dict(key="skirt_midi", label="Midi Skirt", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["university", "brunch", "casual"],
         modesty_min=3),

    dict(key="skirt_maxi", label="Maxi Skirt", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["casual", "brunch", "dawat"],
         modesty_min=4),

    dict(key="dress_midi", label="Midi Dress", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["brunch", "dinner", "cafe", "casual"],
         modesty_min=3),

    dict(key="dress_maxi", label="Maxi Dress", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["casual", "brunch", "dinner", "travel_local"],
         modesty_min=4),

    dict(key="coord_set", label="Co-ord Set", family="western", parent_key="western",
         season_tags=["all_season"],
         occasion_tags=["brunch", "dinner", "cafe", "casual"],
         metadata_json={"description": "Matching top and bottom set"}),

    dict(key="blazer", label="Blazer", family="western", parent_key="western",
         season_tags=["all_season", "winter"],
         occasion_tags=["office_formal", "office_casual", "formal_event", "university"],
         metadata_json={"styling": "can be worn over kurta for fusion look"}),

    dict(key="jacket", label="Jacket", family="western", parent_key="western",
         season_tags=["winter", "transitional"],
         occasion_tags=["casual", "university", "airport"],
         metadata_json={"variants": ["denim", "leather", "bomber"]}),

    dict(key="coat", label="Coat", family="western", parent_key="western",
         season_tags=["winter"],
         occasion_tags=["office_formal", "formal_event", "airport"]),

    dict(key="cardigan", label="Cardigan / Sweater", family="western", parent_key="western",
         season_tags=["winter", "transitional"],
         occasion_tags=["university", "office_casual", "casual", "home"]),

    # ── MODEST ────────────────────────────────────────────────────────────
    dict(key="modest", label="Modest / Abaya", family="modest", parent_key=None,
         modesty_min=4,
         metadata_json={"description": "Full coverage modest garments"}),

    dict(key="abaya_basic", label="Basic Abaya", family="modest", parent_key="modest",
         season_tags=["all_season"],
         occasion_tags=["university", "office_casual", "dawat", "formal_event"],
         modesty_min=5),

    dict(key="abaya_embroidered", label="Embroidered Abaya", family="modest", parent_key="modest",
         season_tags=["all_season"],
         occasion_tags=["dawat", "eid", "formal_event", "nikkah"],
         modesty_min=5),

    dict(key="abaya_open_front", label="Open-Front Abaya", family="modest", parent_key="modest",
         season_tags=["all_season"],
         occasion_tags=["university", "casual", "dawat"],
         modesty_min=4),

    dict(key="longline_shirt", label="Longline Shirt / Tunic", family="modest", parent_key="modest",
         season_tags=["all_season"],
         occasion_tags=["university", "casual", "dawat"],
         modesty_min=4),

    dict(key="oversized_set", label="Oversized Modest Set", family="modest", parent_key="modest",
         season_tags=["all_season"],
         occasion_tags=["university", "casual"],
         modesty_min=4),

    # ── FUSION ────────────────────────────────────────────────────────────
    dict(key="fusion", label="Fusion / Mixed Styling", family="fusion", parent_key=None,
         metadata_json={"description": "Mixed eastern and western styling"}),

    dict(key="kurta_with_jeans", label="Kurta + Jeans", family="fusion", parent_key="fusion",
         season_tags=["all_season"],
         occasion_tags=["university", "casual", "brunch"],
         metadata_json={"components": ["eastern top", "western bottom"]}),

    dict(key="blazer_over_kurta", label="Blazer over Kurta", family="fusion", parent_key="fusion",
         season_tags=["all_season", "winter"],
         occasion_tags=["office_casual", "university", "brunch", "formal_event"],
         metadata_json={"styling": "western layer over eastern base"}),

    dict(key="western_top_eastern_bottom", label="Western Top + Eastern Bottom", family="fusion",
         parent_key="fusion", season_tags=["all_season"],
         occasion_tags=["casual", "university", "brunch"]),

    dict(key="abaya_with_sneakers", label="Abaya + Sneakers", family="fusion", parent_key="fusion",
         season_tags=["all_season"],
         occasion_tags=["university", "casual"],
         modesty_min=4,
         metadata_json={"styling": "modest eastern with casual western footwear"}),
]
