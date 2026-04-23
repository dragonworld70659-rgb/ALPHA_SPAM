from __future__ import annotations

import random
from dataclasses import dataclass

from pyrogram.types import User

# Some commonly used Telegram custom emoji IDs (may render for premium-compatible clients)
PREMIUM_EMOJI_IDS = {
    "love": "5456359419090473856",
    "fire": "5456359419090474010",
    "spark": "5456359419090473930",
    "heart": "5456359419090473976",
}

GF_LINES = [
    "Good morning babu, pani piya kya? 💖",
    "Main hoon na, tension mat lo 😌",
    "Aaj tum bahut cute lag rahe ho ✨",
    "Tumhare liye playlist ready hai 🎶",
    "Chalo coffee date text pe hi sahi ☕",
]

BF_LINES = [
    "Aaj gym gaya tha... bas tumhare liye 💪",
    "No worries, I got your back 😎",
    "Tum smile karo, baaki sab set hai ❤️",
    "Aaj ka song dedicate kiya tumhe 🎧",
    "Protection mode ON 🛡️",
]

FIGHT_LINES = [
    "Roast level dangerously high 🔥",
    "Mic drop moment 🎤",
    "Savage comeback detected 😵",
    "Chat battlefield activated ⚔️",
    "Public ne whistle maara 😮‍💨",
]


@dataclass
class ModeResult:
    title: str
    meter: int
    line: str


def gf_mode(name: str) -> ModeResult:
    return ModeResult("GF MODE", random.randint(70, 100), random.choice(GF_LINES).replace("tum", name))


def bf_mode(name: str) -> ModeResult:
    return ModeResult("BF MODE", random.randint(70, 100), random.choice(BF_LINES).replace("tum", name))


def couple_pick(users: list[User]) -> tuple[User, User] | None:
    humans = [u for u in users if not u.is_bot]
    if len(humans) < 2:
        return None
    return tuple(random.sample(humans, 2))


def chat_fight_score() -> tuple[int, int, str]:
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    return a, b, random.choice(FIGHT_LINES)


def pemoji(name: str) -> str:
    eid = PREMIUM_EMOJI_IDS[name]
    return f'<emoji id="{eid}">✨</emoji>'
