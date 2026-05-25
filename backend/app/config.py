"""Configuración de la aplicación."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./tracker.db"
    openfoodfacts_base_url: str = "https://world.openfoodfacts.org"
    openfoodfacts_user_agent: str = "TrackerDinamico/1.0 (taller4@universidad.edu)"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    # En producción (Render) setear CORS_ALLOW_ALL=true para aceptar cualquier origen
    cors_allow_all: bool = False

    # F1 — Autenticación JWT
    jwt_secret: str = "dev-secret-change-in-production-use-env-var"
    jwt_algorithm: str = "HS256"
    access_token_expire_days: int = 60  # sesión persistente 60 días


settings = Settings()
