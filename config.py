import os
from dataclasses import dataclass


def _as_list(value: str) -> list[int]:
    if not value.strip():
        return []
    return [int(x) for x in value.replace(',', ' ').split()]


@dataclass(frozen=True)
class Config:
    api_id: int
    api_hash: str
    bot_token: str
    string_session: str
    sudo_users: list[int]
    command_prefixes: list[str]
    openai_api_key: str
    ai_model: str
    ai_image_model: str


config = Config(
    api_id=int(os.getenv("API_ID", "0")),
    api_hash=os.getenv("API_HASH", ""),
    bot_token=os.getenv("BOT_TOKEN", ""),
    string_session=os.getenv("STRING_SESSION", ""),
    sudo_users=_as_list(os.getenv("SUDO_USERS", "")),
    command_prefixes=os.getenv("COMMAND_PREFIXES", "/ ! .").split(),
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    ai_model=os.getenv("AI_MODEL", "gpt-4.1-mini"),
    ai_image_model=os.getenv("AI_IMAGE_MODEL", "gpt-image-1"),
)


if not all([config.api_id, config.api_hash, config.bot_token, config.string_session]):
    raise RuntimeError(
        "Missing required env vars. Set API_ID, API_HASH, BOT_TOKEN, STRING_SESSION."
    )
