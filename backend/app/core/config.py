from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./sermon_extraction.db"
    storage_root: str = "./storage"
    ytdlp_path: str = "yt-dlp"
    ffmpeg_path: str = "ffmpeg"
    ai_provider: str = "fake"
    transcription_provider: str = "fake"
    classification_provider: str = "fake"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

settings = Settings()
