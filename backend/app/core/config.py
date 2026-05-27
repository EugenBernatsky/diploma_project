from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGODB_URL: str
    MONGODB_DB: str

    ADMIN_EMAIL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    TMDB_API_READ_TOKEN: str
    TMDB_BASE_URL: str
    TMDB_IMAGE_BASE_URL: str
    TMDB_POSTER_SIZE: str
    TMDB_BACKDROP_SIZE: str
    TMDB_REGION: str
    TMDB_LANGUAGE: str

    GOOGLE_BOOKS_API_KEY: str
    GOOGLE_BOOKS_BASE_URL: str
    GOOGLE_BOOKS_COUNTRY: str
    GOOGLE_BOOKS_LANG: str

    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = ""
    BREVO_SENDER_NAME: str = "MediaCompass"

    EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    EMAIL_VERIFICATION_RESEND_SECONDS: int = 60
    EMAIL_VERIFICATION_MAX_ATTEMPTS: int = 5

    USERNAME_CHANGE_COOLDOWN_DAYS: int = 7


settings = Settings()