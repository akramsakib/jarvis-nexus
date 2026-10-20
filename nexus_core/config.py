from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Settings:
    ai_provider: str = "local"
    ai_model: str = "local-echo"
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    stt_provider: str = "local"
    tts_provider: str = "local"
    database_url: str = "sqlite:///./nexus.db"
    vector_db_url: str = ""
    wake_word_enabled: bool = False
    screen_access_enabled: bool = False
    telemetry_enabled: bool = True
    microphone_enabled: bool = False
    approval_mode: str = "manual"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        import os

        return cls(
            ai_provider=os.getenv("AI_PROVIDER", "local"),
            ai_model=os.getenv("AI_MODEL", "local-echo"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            stt_provider=os.getenv("STT_PROVIDER", "local"),
            tts_provider=os.getenv("TTS_PROVIDER", "local"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./nexus.db"),
            vector_db_url=os.getenv("VECTOR_DB_URL", ""),
            wake_word_enabled=os.getenv("WAKE_WORD_ENABLED", "false").lower() == "true",
            screen_access_enabled=os.getenv("SCREEN_ACCESS_ENABLED", "false").lower() == "true",
            telemetry_enabled=os.getenv("TELEMETRY_ENABLED", "true").lower() == "true",
            microphone_enabled=os.getenv("MICROPHONE_ENABLED", "false").lower() == "true",
            approval_mode=os.getenv("APPROVAL_MODE", "manual"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
        )


settings = Settings.from_env()
