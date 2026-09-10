"""
STYLEIQ Taxonomy Service
─────────────────────────
Loads the Pakistani fashion taxonomy from JSON
and provides a clean query interface for agents.

Usage:
    from styleiq.taxonomy.service import taxonomy
    fabrics = taxonomy.get_fabrics_for_season("summer")
    occasions = taxonomy.get_occasions_by_formality("formal")
    city_info = taxonomy.get_city_climate("islamabad")
"""

from __future__ import annotations
import json
from pathlib import Path
from functools import lru_cache
from styleiq.logger import get_logger

log = get_logger(__name__)

TAXONOMY_PATH = Path(__file__).parent.parent.parent / "data" / "taxonomy" / "pk_fashion_taxonomy.json"


class TaxonomyService:
    """
    Single access point for all fashion taxonomy data.
    Loaded once from JSON, cached in memory.
    """

    def __init__(self):
        self._data = self._load()
        log.info("Taxonomy loaded | version={v}", v=self._data.get("version"))

    def _load(self) -> dict:
        if not TAXONOMY_PATH.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {TAXONOMY_PATH}")
        with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── Garments ──────────────────────────────────────────────────────
    def get_all_families(self) -> list[dict]:
        """Returns all garment families (eastern, western, modest, fusion)."""
        return self._data["garment_families"]

    def get_family(self, family_id: str) -> dict | None:
        """Get a specific garment family by ID."""
        for family in self._data["garment_families"]:
            if family["id"] == family_id:
                return family
        return None

    def get_categories_for_family(self, family_id: str) -> list[dict]:
        """Get all garment categories for a family."""
        family = self.get_family(family_id)
        return family["categories"] if family else []

    def get_all_categories(self) -> list[dict]:
        """Get every garment category across all families."""
        all_cats = []
        for family in self._data["garment_families"]:
            for cat in family["categories"]:
                cat_with_family = dict(cat)
                cat_with_family["family_id"] = family["id"]
                all_cats.append(cat_with_family)
        return all_cats

    def get_categories_for_occasion(self, occasion_id: str) -> list[dict]:
        """Get garment categories appropriate for a given occasion."""
        result = []
        for cat in self.get_all_categories():
            occasions = cat.get("occasions", [])
            if occasion_id in occasions or "any" in occasions:
                result.append(cat)
        return result

    def get_categories_for_modesty(self, min_modesty: int) -> list[dict]:
        """Get categories that meet a minimum modesty level."""
        return [
            cat for cat in self.get_all_categories()
            if cat.get("modesty_min", 1) >= min_modesty
        ]

    # ── Fabrics ───────────────────────────────────────────────────────
    def get_all_fabrics(self) -> list[dict]:
        return self._data["fabrics"]

    def get_fabrics_for_season(self, season: str) -> list[dict]:
        """Get fabrics appropriate for a season."""
        return [
            f for f in self._data["fabrics"]
            if f["season"] == season or f["season"] == "all_season"
        ]

    def get_fabrics_for_city(self, city: str, season: str) -> list[dict]:
        """Get fabrics suitable for a specific city and season."""
        city_info = self.get_city_climate(city)
        if not city_info:
            return self.get_fabrics_for_season(season)
        key = f"recommended_{season}_fabrics"
        recommended_ids = city_info.get(key, [])
        return [f for f in self._data["fabrics"] if f["id"] in recommended_ids]

    def get_fabric(self, fabric_id: str) -> dict | None:
        for f in self._data["fabrics"]:
            if f["id"] == fabric_id:
                return f
        return None

    # ── Occasions ─────────────────────────────────────────────────────
    def get_all_occasions(self) -> list[dict]:
        return self._data["occasions"]

    def get_occasion(self, occasion_id: str) -> dict | None:
        for o in self._data["occasions"]:
            if o["id"] == occasion_id:
                return o
        return None

    def get_occasions_by_formality(self, formality: str) -> list[dict]:
        return [
            o for o in self._data["occasions"]
            if formality in o["formality"]
        ]

    def get_wedding_occasions(self) -> list[dict]:
        """Returns all Pakistani wedding-related occasions."""
        wedding_ids = {"mehndi", "dholki", "nikkah", "baraat", "walima", "mayun", "baat_pakki"}
        return [o for o in self._data["occasions"] if o["id"] in wedding_ids]

    # ── Colors ────────────────────────────────────────────────────────
    def get_all_colors(self) -> list[dict]:
        all_colors = []
        for family, colors in self._data["colors"].items():
            for color in colors:
                color_with_family = dict(color)
                color_with_family["family"] = family
                all_colors.append(color_with_family)
        return all_colors

    def get_colors_by_family(self, family: str) -> list[dict]:
        return self._data["colors"].get(family, [])

    def get_traditional_pk_colors(self) -> list[dict]:
        return self._data["colors"].get("traditional_pk", [])

    def get_colors_for_occasion(self, occasion_id: str) -> list[dict]:
        """Get culturally appropriate colors for an occasion."""
        occasion = self.get_occasion(occasion_id)
        if not occasion:
            return self.get_all_colors()
        color_guides = {
            "mehndi": ["traditional_pk", "earth_tones"],
            "baraat": ["traditional_pk", "jewel_tones"],
            "nikkah": ["neutrals", "pastels"],
            "walima": ["pastels", "neutrals", "jewel_tones"],
            "eid": ["pastels", "jewel_tones", "traditional_pk"],
            "university": ["neutrals", "earth_tones", "pastels"],
            "office_formal": ["neutrals", "jewel_tones"],
        }
        families = color_guides.get(occasion_id, list(self._data["colors"].keys()))
        result = []
        for family in families:
            result.extend(self.get_colors_by_family(family))
        return result

    # ── Silhouettes ───────────────────────────────────────────────────
    def get_all_silhouettes(self) -> list[dict]:
        return self._data["silhouettes"]

    def get_modest_silhouettes(self) -> list[dict]:
        """Get silhouettes that naturally support modest dressing."""
        return [
            s for s in self._data["silhouettes"]
            if s.get("modesty_impact") in ("higher", "neutral")
        ]

    # ── City Climate ──────────────────────────────────────────────────
    def get_city_climate(self, city: str) -> dict | None:
        return self._data["city_climate"].get(city.lower())

    def get_all_cities(self) -> list[str]:
        return list(self._data["city_climate"].keys())

    # ── Combined queries ──────────────────────────────────────────────
    def get_outfit_context(self, occasion_id: str, city: str, season: str, modesty_level: int) -> dict:
        """
        Master query used by the Recommendation Agent.
        Returns everything needed to build an outfit recommendation.
        """
        return {
            "occasion": self.get_occasion(occasion_id),
            "suitable_categories": self.get_categories_for_occasion(occasion_id),
            "suitable_fabrics": self.get_fabrics_for_city(city, season),
            "suitable_colors": self.get_colors_for_occasion(occasion_id),
            "modest_categories": self.get_categories_for_modesty(modesty_level),
            "city_climate": self.get_city_climate(city),
            "modest_silhouettes": self.get_modest_silhouettes() if modesty_level >= 3 else [],
        }

    def summary(self) -> dict:
        """Returns a summary of the taxonomy for display."""
        return {
            "version": self._data["version"],
            "garment_families": len(self._data["garment_families"]),
            "total_categories": len(self.get_all_categories()),
            "fabrics": len(self._data["fabrics"]),
            "occasions": len(self._data["occasions"]),
            "total_colors": len(self.get_all_colors()),
            "silhouettes": len(self._data["silhouettes"]),
            "cities": len(self._data["city_climate"]),
        }


# ── Singleton ──────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_taxonomy() -> TaxonomyService:
    return TaxonomyService()

taxonomy = get_taxonomy()
