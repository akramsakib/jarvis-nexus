from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ProviderResponse:
    text: str
    provider: str
    model: str
    ok: bool = True


class ModelProvider(ABC):
    name: str = "base"
    model: str = "base-model"

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> ProviderResponse:
        raise NotImplementedError


class LocalEchoProvider(ModelProvider):
    name = "local"
    model = "local-echo"

    def generate(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> ProviderResponse:
        base = system_prompt or "You are NEXUS, a calm and precise personal AI assistant."
        response = f"{base}\n\nUser input: {prompt}\n\nIntent: local analysis completed."
        return ProviderResponse(text=response, provider=self.name, model=self.model, ok=True)


class ProviderFactory:
    @staticmethod
    def get(provider_name: str, model: str | None = None) -> ModelProvider:
        provider_name = (provider_name or "local").lower()
        if provider_name in {"local", "offline"}:
            return LocalEchoProvider()
        raise ValueError(f"Unsupported provider: {provider_name}")
