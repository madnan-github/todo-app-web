"""Configuration module for environment variables."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class ValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    # In production, this MUST be set to a Neon PostgreSQL connection string
    database_url: str = "sqlite+aiosqlite:///./todo_app.db"

    # JWT - CRITICAL: No defaults in production
    # These MUST be set via environment variables in production
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 10080  # 7 days

    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    environment: str = "development"

    # CORS - Vercel production domains only
    cors_origins: str = "http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    # Better Auth - CRITICAL: No defaults in production
    # This MUST be set via environment variables in production
    better_auth_secret: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore"
    )

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def validate_production_secrets(self) -> None:
        """
        Validate that all required secrets are externalized.

        In production, this MUST be called at startup to ensure
        no hardcoded secrets are being used.

        Raises:
            ValidationError: If a required secret is missing or has default value
        """
        missing_secrets = []
        default_secrets = []

        # Check JWT secret
        if self.is_production():
            if not self.jwt_secret_key:
                missing_secrets.append("JWT_SECRET_KEY")
            elif self.jwt_secret_key == "dev-secret-key-change-in-production":
                default_secrets.append("JWT_SECRET_KEY")

            # Check Better Auth secret
            if not self.better_auth_secret:
                missing_secrets.append("BETTER_AUTH_SECRET")
            elif self.better_auth_secret == "dev-auth-secret-change-in-production":
                default_secrets.append("BETTER_AUTH_SECRET")

        errors = []

        if missing_secrets:
            errors.append(
                f"Missing required secrets (must be set in environment): {', '.join(missing_secrets)}"
            )

        if default_secrets:
            errors.append(
                f"Secrets still have default values (must be changed in production): {', '.join(default_secrets)}"
            )

        if errors:
            raise ValidationError(
                f"Production configuration error:\n" + "\n".join(errors)
            )

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def validate_settings() -> Settings:
    """
    Validate settings for the current environment.

    In production, this validates that all secrets are externalized.
    """
    settings = get_settings()

    if settings.is_production():
        settings.validate_production_secrets()

    return settings


# Global settings instance - validate on import in production
try:
    settings = validate_settings()
except ValidationError as e:
    # In production, we want to fail fast
    import sys
    print(f"FATAL: {e}", file=sys.stderr)
    sys.exit(1)
