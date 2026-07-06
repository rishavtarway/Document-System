from __future__ import annotations

import json
from typing import Optional

import httpx
from openai import OpenAI

from app.core.config import settings


PROVIDER_CONFIGS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_field": "groq_api_key",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "api_key_field": "deepseek_api_key",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_field": "openrouter_api_key",
    },
}


class LLMClient:
    _instance: Optional[OpenAI] = None

    @classmethod
    def get_client(cls) -> OpenAI:
        if cls._instance is None:
            cfg = PROVIDER_CONFIGS.get(settings.llm_provider, PROVIDER_CONFIGS["groq"])
            api_key = getattr(settings, cfg["api_key_field"], "")
            cls._instance = OpenAI(api_key=api_key, base_url=cfg["base_url"])
        return cls._instance

    @classmethod
    def _model_name(cls) -> str:
        if settings.llm_provider == "groq":
            return settings.groq_model
        elif settings.llm_provider == "openrouter":
            return settings.openrouter_model
        return settings.deepseek_model

    @classmethod
    def _vision_model(cls) -> str:
        if settings.llm_provider == "groq":
            return settings.groq_vision_model
        return cls._model_name()

    @classmethod
    async def generate(cls, prompt: str, response_format: str = "json", temperature: float = 0.1) -> str:
        client = cls.get_client()
        kwargs = {
            "model": cls._model_name(),
            "messages": [
                {"role": "system", "content": "You are a document processing assistant. Respond in JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": 4096,
        }
        # Groq doesn't support response_format for all models, so always embed in prompt
        kwargs["response_format"] = {"type": "json_object"}
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")

    @classmethod
    async def generate_with_image(cls, prompt: str, image_data: str, temperature: float = 0.1) -> str:
        client = cls.get_client()
        try:
            response = client.chat.completions.create(
                model=cls._vision_model(),
                messages=[
                    {"role": "system", "content": "You are a document processing assistant."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_data}"},
                            },
                        ],
                    },
                ],
                temperature=temperature,
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"LLM vision call failed: {e}")


class EmbeddingClient:
    @classmethod
    async def embed(cls, text: str) -> list[float]:
        """Generate embedding vector for text.
        Falls back to a simple hash-based vector when no embeddings API is available.
        """
        if settings.llm_provider == "groq":
            return cls._mock_embedding(text)

        cfg = PROVIDER_CONFIGS.get(settings.llm_provider, PROVIDER_CONFIGS["deepseek"])
        api_key = getattr(settings, cfg["api_key_field"], "")
        url = f"{cfg['base_url'].rstrip('/')}/embeddings"

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "text-embedding-3-small", "input": text},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

    @classmethod
    def _mock_embedding(cls, text: str) -> list[float]:
        """Simple deterministic embedding for Groq (no embeddings API).
        Generates a 128-dim vector from text hash for demo purposes.
        """
        import hashlib
        h = hashlib.sha256(text.encode()).hexdigest()
        seed = int(h[:8], 16)
        import random
        rng = random.Random(seed)
        vec = [rng.gauss(0, 1) for _ in range(128)]
        norm = sum(x * x for x in vec) ** 0.5
        return [x / norm for x in vec]
