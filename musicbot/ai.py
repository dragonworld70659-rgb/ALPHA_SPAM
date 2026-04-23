from __future__ import annotations

import base64
from dataclasses import dataclass

from openai import AsyncOpenAI


@dataclass(frozen=True)
class AISettings:
    api_key: str
    chat_model: str
    image_model: str


class AIAssistant:
    def __init__(self, settings: AISettings) -> None:
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.api_key) if settings.api_key else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    async def ask(self, prompt: str, system_prompt: str | None = None) -> str:
        if not self.client:
            raise RuntimeError("AI feature disabled: OPENAI_API_KEY missing")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.settings.chat_model,
            messages=messages,
            temperature=0.6,
        )
        return response.choices[0].message.content or "No response"

    async def summarize(self, text: str) -> str:
        return await self.ask(
            text,
            system_prompt=(
                "Summarize the user text in Hinglish bullets. "
                "Keep key actions, names, numbers, and a short TL;DR."
            ),
        )

    async def generate_image(self, prompt: str) -> bytes:
        if not self.client:
            raise RuntimeError("AI feature disabled: OPENAI_API_KEY missing")

        result = await self.client.images.generate(
            model=self.settings.image_model,
            prompt=prompt,
            size="1024x1024",
        )

        data = result.data[0]
        if getattr(data, "b64_json", None):
            return base64.b64decode(data.b64_json)

        # fallback in case API returns URL-only response
        if getattr(data, "url", None):
            import httpx

            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.get(data.url)
                r.raise_for_status()
                return r.content

        raise RuntimeError("Image generation failed")
