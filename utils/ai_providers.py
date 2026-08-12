"""
AI Provider abstraction layer for Lovina Bot.
Supports: groq, openai, anthropic, gemini, mistral, ollama
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# Import guards for optional AI provider libraries
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class BaseProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], max_tokens: int = 1024, temperature: float = 0.7) -> str: ...
    @property
    @abstractmethod
    def name(self) -> str: ...


class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        from groq import AsyncGroq
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
    @property
    def name(self) -> str: return f"Groq ({self.model})"
    async def chat(self, messages, max_tokens=1024, temperature=0.7) -> str:
        r = await self.client.chat.completions.create(model=self.model, messages=messages, max_tokens=max_tokens, temperature=temperature)
        return r.choices[0].message.content or ""


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    @property
    def name(self) -> str: return f"OpenAI ({self.model})"
    async def chat(self, messages, max_tokens=1024, temperature=0.7) -> str:
        if openai is None:
            raise ValueError("openai package not installed. Run: pip install openai")
        r = await self.client.chat.completions.create(model=self.model, messages=messages, max_tokens=max_tokens, temperature=temperature)
        return r.choices[0].message.content or ""


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
    @property
    def name(self) -> str: return f"Anthropic ({self.model})"
    async def chat(self, messages, max_tokens=1024, temperature=0.7) -> str:
        if anthropic is None:
            raise ValueError("anthropic package not installed. Run: pip install anthropic")
        system_msg = ""
        filtered = []
        for m in messages:
            if m["role"] == "system": system_msg = m["content"]
            else: filtered.append({"role": m["role"], "content": m["content"]})
        r = await self.client.messages.create(model=self.model, max_tokens=max_tokens, system=system_msg, messages=filtered)
        return r.content[0].text if r.content else ""


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model_name = model
        self._genai = genai
    @property
    def name(self) -> str: return f"Google Gemini ({self.model_name})"
    async def chat(self, messages, max_tokens=1024, temperature=0.7) -> str:
        if genai is None:
            raise ValueError("google-generativeai package not installed. Run: pip install google-generativeai")
        import asyncio
        model = self._genai.GenerativeModel(self.model_name)
        history = []
        system_ctx = ""
        for m in messages:
            if m["role"] == "system": system_ctx = m["content"]
            elif m["role"] == "user":
                content = m["content"]
                if system_ctx and not history: content = f"{system_ctx}\n\n{content}"; system_ctx = ""
                history.append({"role": "user", "parts": [content]})
            elif m["role"] == "assistant": history.append({"role": "model", "parts": [m["content"]]})
        loop = asyncio.get_event_loop()
        r = await loop.run_in_executor(None, lambda: model.generate_content(history, generation_config={"max_output_tokens": max_tokens, "temperature": temperature}))
        return r.text or ""


class MistralProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    @property
    def name(self) -> str: return f"Mistral ({self.model})"
    async def chat(self, messages, max_tokens=1024, temperature=0.7) -> str:
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not set. Add it to your environment variables.")
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post("https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature})
            return r.json()["choices"][0]["message"]["content"] or ""


class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
    @property
    def name(self) -> str: return f"Ollama/{self.model} (local)"
    async def chat(self, messages, max_tokens=1024, temperature=0.7) -> str:
        import httpx
        async with httpx.AsyncClient(timeout=120.0) as c:
            r = await c.post(f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False,
                      "options": {"num_predict": max_tokens, "temperature": temperature}})
            return r.json().get("message", {}).get("content", "")


def build_provider(provider_name: str | None = None) -> BaseProvider:
    from config import (
        AI_PROVIDER,
        GROQ_API_KEY, GROQ_MODEL,
        OPENAI_API_KEY, OPENAI_MODEL,
        ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
        GEMINI_API_KEY, GEMINI_MODEL,
        MISTRAL_API_KEY, MISTRAL_MODEL,
        OLLAMA_BASE_URL, OLLAMA_MODEL,
    )
    name = (provider_name or AI_PROVIDER or "groq").lower().strip()
    if name == "openai":
        if not OPENAI_API_KEY: raise EnvironmentError("OPENAI_API_KEY not set. Add it to Railway env vars.")
        return OpenAIProvider(OPENAI_API_KEY, OPENAI_MODEL)
    if name == "anthropic":
        if not ANTHROPIC_API_KEY: raise EnvironmentError("ANTHROPIC_API_KEY not set. Add it to Railway env vars.")
        return AnthropicProvider(ANTHROPIC_API_KEY, ANTHROPIC_MODEL)
    if name == "gemini":
        if not GEMINI_API_KEY: raise EnvironmentError("GEMINI_API_KEY not set. Add it to Railway env vars.")
        return GeminiProvider(GEMINI_API_KEY, GEMINI_MODEL)
    if name == "mistral":
        if not MISTRAL_API_KEY: raise EnvironmentError("MISTRAL_API_KEY not set. Add it to Railway env vars.")
        return MistralProvider(MISTRAL_API_KEY, MISTRAL_MODEL)
    if name == "ollama":
        return OllamaProvider(OLLAMA_BASE_URL, OLLAMA_MODEL)
    # Default: Groq
    if not GROQ_API_KEY: raise EnvironmentError("GROQ_API_KEY not set. Get a free key at https://console.groq.com")
    return GroqProvider(GROQ_API_KEY, GROQ_MODEL)


def list_available_providers() -> dict[str, bool]:
    from config import GROQ_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY
    return {
        "groq": bool(GROQ_API_KEY),
        "openai": bool(OPENAI_API_KEY),
        "anthropic": bool(ANTHROPIC_API_KEY),
        "gemini": bool(GEMINI_API_KEY),
        "mistral": bool(MISTRAL_API_KEY),
        "ollama": True,
    }
