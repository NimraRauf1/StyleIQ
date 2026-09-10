from __future__ import annotations
import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

_here = Path(__file__).resolve().parent
_root = _here.parent
load_dotenv(_root / ".env")

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ClaudeSettings(BaseSettings):
    model_config = {"env_prefix": "CLAUDE_", "extra": "ignore"}
    api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-sonnet-4-6")
    max_tokens: int = Field(default=1024)
    temperature: float = Field(default=0.3)

    @field_validator("api_key", mode="before")
    @classmethod
    def resolve_api_key(cls, v: str) -> str:
        return v or os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_anthropic_api_key_here"

class DatabaseSettings(BaseSettings):
    model_config = {"extra": "ignore"}
    url: str = Field(default="sqlite:///./styleiq.db", alias="DATABASE_URL")

    @property
    def is_sqlite(self) -> bool:
        return self.url.startswith("sqlite")

class DataCollectionSettings(BaseSettings):
    model_config = {"extra": "ignore"}
    enabled: bool = Field(default=False, alias="DATA_COLLECTION_ENABLED")
    request_delay_seconds: float = Field(default=2.0, alias="REQUEST_DELAY_SECONDS")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")

class ImageSettings(BaseSettings):
    model_config = {"extra": "ignore"}
    storage_dir: Path = Field(default=Path("./data/images"), alias="IMAGE_STORAGE_DIR")
    max_size_mb: int = Field(default=5, alias="MAX_IMAGE_SIZE_MB")
    retain_uploaded: bool = Field(default=False, alias="RETAIN_UPLOADED_IMAGES")

    @field_validator("storage_dir", mode="before")
    @classmethod
    def make_path(cls, v) -> Path:
        return Path(v)

class CacheSettings(BaseSettings):
    model_config = {"extra": "ignore"}
    dir: Path = Field(default=Path("./data/cache"), alias="CACHE_DIR")
    ttl_hours: int = Field(default=24, alias="CACHE_TTL_HOURS")

    @field_validator("dir", mode="before")
    @classmethod
    def make_path(cls, v) -> Path:
        return Path(v)

class WeatherSettings(BaseSettings):
    model_config = {"extra": "ignore"}
    default_city: str = Field(default="Islamabad", alias="DEFAULT_CITY")
    default_latitude: float = Field(default=33.6844, alias="DEFAULT_LATITUDE")
    default_longitude: float = Field(default=73.0479, alias="DEFAULT_LONGITUDE")

class VectorStoreSettings(BaseSettings):
    model_config = {"extra": "ignore"}
    persist_dir: Path = Field(default=Path("./data/chroma"), alias="CHROMA_PERSIST_DIR")

    @field_validator("persist_dir", mode="before")
    @classmethod
    def make_path(cls, v) -> Path:
        return Path(v)

class Settings(BaseSettings):
    model_config = {"env_prefix": "STYLEIQ_", "extra": "ignore", "case_sensitive": False}
    app_name: str = "STYLEIQ"
    app_version: str = "0.1.0"
    app_description: str = "Pakistan Fashion Intelligence & Personal Stylist Agent"
    env: Environment = Field(default=Environment.DEVELOPMENT, alias="STYLEIQ_ENV")
    debug: bool = Field(default=True, alias="STYLEIQ_DEBUG")
    log_level: LogLevel = Field(default=LogLevel.DEBUG, alias="STYLEIQ_LOG_LEVEL")
    project_root: Path = Field(default=_root)
    data_dir: Path = Field(default=_root / "data")
    taxonomy_dir: Path = Field(default=_root / "data" / "taxonomy")
    curated_data_dir: Path = Field(default=_root / "data" / "curated")
    models_dir: Path = Field(default=_root / "models")
    logs_dir: Path = Field(default=_root / "logs")
    claude: ClaudeSettings = Field(default_factory=ClaudeSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    data_collection: DataCollectionSettings = Field(default_factory=DataCollectionSettings)
    images: ImageSettings = Field(default_factory=ImageSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    weather: WeatherSettings = Field(default_factory=WeatherSettings)
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)

    def ensure_directories(self) -> None:
        dirs = [
            self.data_dir, self.taxonomy_dir,
            self.curated_data_dir / "brands",
            self.curated_data_dir / "products",
            self.curated_data_dir / "trends",
            self.images.storage_dir, self.cache.dir,
            self.vector_store.persist_dir, self.logs_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @property
    def is_development(self) -> bool:
        return self.env == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.env == Environment.PRODUCTION

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    s.ensure_directories()
    return s

settings = get_settings()
