from __future__ import annotations

from yt_dlp import YoutubeDL
from pyrogram import Client
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall

from musicbot.queue import Track, queues


YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "extract_flat": False,
    "default_search": "ytsearch",
}


class MusicPlayer:
    def __init__(self, bot: Client, user: Client) -> None:
        self.bot = bot
        self.user = user
        self.call = PyTgCalls(user)

    async def start(self) -> None:
        await self.call.start()

    def search(self, query: str) -> Track:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            return Track(
                title=info.get("title", "Unknown"),
                url=info.get("webpage_url") or query,
                stream_url=info["url"],
                duration=info.get("duration"),
            )

    async def _play_track(self, chat_id: int, track: Track) -> None:
        await self.call.join_group_call(chat_id, AudioPiped(track.stream_url))

    async def enqueue_and_maybe_play(self, msg: Message, query: str) -> str:
        track = self.search(query)
        track.requested_by = msg.from_user.mention if msg.from_user else "Unknown"
        position = queues.add(msg.chat.id, track)
        if position == 1:
            try:
                await self._play_track(msg.chat.id, track)
                return f"▶️ **Playing:** {track.title}"
            except NoActiveGroupCall:
                queues.clear(msg.chat.id)
                return "❌ Group voice chat active nahi hai. Pehle group call start karo."
        return f"➕ **Queued #{position}:** {track.title}"

    async def skip(self, chat_id: int) -> str:
        queues.pop_next(chat_id)
        nxt = queues.peek(chat_id)
        if not nxt:
            await self.call.leave_group_call(chat_id)
            return "⏹ Queue khatam. VC छोड़ दिया."
        await self._play_track(chat_id, nxt)
        return f"⏭ **Now playing:** {nxt.title}"


player: MusicPlayer | None = None
