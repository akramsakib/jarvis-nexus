from __future__ import annotations

from abc import ABC, abstractmethod


class SpeechToText(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str | None = None, text: str | None = None) -> str:
        raise NotImplementedError


class TextToSpeech(ABC):
    @abstractmethod
    def speak(self, text: str, voice: str | None = None, speed: float = 1.0) -> str:
        raise NotImplementedError


class LocalSTT(SpeechToText):
    def transcribe(self, audio_path: str | None = None, text: str | None = None) -> str:
        return text or "Local STT is unavailable."


class LocalTTS(TextToSpeech):
    def speak(self, text: str, voice: str | None = None, speed: float = 1.0) -> str:
        return f"[voice] {text}"
