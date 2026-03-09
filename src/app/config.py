"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server configuration. All values can be overridden via environment variables."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Auth
    api_key: str = ""
    allowed_origins: str = "*"

    # Cache
    cache_interval_minutes: int = 60

    # Data sources
    noaa_base_url: str = "https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz"
    uw_synopsis_url: str = "https://a.atmos.washington.edu/data/marine_report.html"
    noaa_timeout_seconds: int = 30

    # MCP
    mcp_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def auth_enabled(self) -> bool:
        return bool(self.api_key)

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
