from __future__ import annotations

import json
from typing import Optional

import httpx
from openai import OpenAI

from app.core.config import settings


class LLMClient:
    _instance: Optional[OpenAI] = None

    @classmethod
    def get_client(cls) -> OpenAI:
        if cls._instance is None:
            if settings.use_openrouter:
                cls._instance = OpenAI(
                    api_key=settings.openrouter_api_key,
                    base_url="https://openrouter.ai/api/v1",
                )
            else:
                cls._instance = OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com",
                )
        return cls._instance

    @classmethod
    async def generate(cls, prompt: str, response_format: str = "json", temperature: float = 0.1) -> str:
        client = cls.get_client()
        try:
            response = client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {"role": "system", "content": "You are a document processing AI. Respond in the requested format."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"} if response_format == "json" else None,
                temperature=temperature,
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")

    @classmethod
    async def generate_with_image(cls, prompt: str, image_data: str, response_format: str = "json") -> str:
        client = cls.get_client()
        try:
            response = client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {"role": "system", "content": "You are a document processing AI."},
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
                response_format={"type": "json_object"} if response_format == "json" else None,
                temperature=temperature,
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"LLM vision call failed: {e}")


class EmbeddingClient:
    @classmethod
    async def embed(cls, text: str) -> list[float]:
        """Generate embedding vector for text"""
        if settings.use_openrouter:
            url = "https://openrouter.ai/api/v1/embeddings"
            headers = {"Authorization": f"Bearer {settings.openrouter_api_key}"}
        else:
            url = "https://api.deepseek.com/v1/embeddings"
            headers = {"Authorization": f"Bearer {settings.deepseek_api_key}"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=headers,
                json={
                    "model": "text-embedding-3-small",
                    "input": text,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
