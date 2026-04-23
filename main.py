import asyncio
import logging
from io import BytesIO

from pyrogram import Client, filters
from pyrogram.types import Message

from config import config
from musicbot.ai import AIAssistant, AISettings
from musicbot.player import MusicPlayer
from musicbot.queue import queues


logging.basicConfig(
    format="[%(levelname)s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

bot = Client(
    "music-bot",
    api_id=config.api_id,
    api_hash=config.api_hash,
    bot_token=config.bot_token,
)

assistant = Client(
    "music-assistant",
    api_id=config.api_id,
    api_hash=config.api_hash,
    session_string=config.string_session,
)

player = MusicPlayer(bot, assistant)
ai = AIAssistant(
    AISettings(
        api_key=config.openai_api_key,
        chat_model=config.ai_model,
        image_model=config.ai_image_model,
    )
)


def cmd(name: str):
    return filters.command(name, prefixes=config.command_prefixes)


@bot.on_message(cmd("start") & filters.group)
async def start_cmd(_: Client, msg: Message):
    await msg.reply_text(
        "🎵 **Music Bot Online**\n"
        "Music: /play /skip /pause /resume /end /queue\n"
        "AI: /ai /summarize /imagine"
    )


@bot.on_message(cmd("help") & filters.group)
async def help_cmd(_: Client, msg: Message):
    text = (
        "**Music Commands**\n"
        "• `/play <song name or url>` - song play/queue\n"
        "• `/skip` - next song\n"
        "• `/pause` - pause stream\n"
        "• `/resume` - resume stream\n"
        "• `/end` - stop + clear queue\n"
        "• `/queue` - show queue\n\n"
        "**AI Commands**\n"
        "• `/ai <question>` - AI se answer\n"
        "• `/summarize` (reply to text) - message summary\n"
        "• `/imagine <prompt>` - AI image generate"
    )
    await msg.reply_text(text)


@bot.on_message(cmd("ping"))
async def ping_cmd(_: Client, msg: Message):
    await msg.reply_text("🏓 Pong")


@bot.on_message(cmd("play") & filters.group)
async def play_cmd(_: Client, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply_text("Usage: /play <song name or url>")

    query = " ".join(msg.command[1:])
    status = await msg.reply_text("🔎 Searching...")
    result = await asyncio.to_thread(player.search, query)
    result.requested_by = msg.from_user.mention if msg.from_user else "Unknown"
    position = queues.add(msg.chat.id, result)

    if position == 1:
        from pytgcalls.types import AudioPiped

        try:
            await player.call.join_group_call(msg.chat.id, AudioPiped(result.stream_url))
        except Exception:
            queues.clear(msg.chat.id)
            return await status.edit_text(
                "❌ Voice chat active karo + assistant ko admin do, phir try karo."
            )
        return await status.edit_text(f"▶️ **Playing:** {result.title}")

    await status.edit_text(f"➕ **Queued #{position}:** {result.title}")


@bot.on_message(cmd("skip") & filters.group)
async def skip_cmd(_: Client, msg: Message):
    if not queues.peek(msg.chat.id):
        return await msg.reply_text("Queue empty hai.")
    queues.pop_next(msg.chat.id)
    nxt = queues.peek(msg.chat.id)
    if not nxt:
        await player.call.leave_group_call(msg.chat.id)
        return await msg.reply_text("⏹ Queue finished, VC छोड़ा.")
    from pytgcalls.types import AudioPiped

    await player.call.change_stream(msg.chat.id, AudioPiped(nxt.stream_url))
    await msg.reply_text(f"⏭ **Now playing:** {nxt.title}")


@bot.on_message(cmd("pause") & filters.group)
async def pause_cmd(_: Client, msg: Message):
    await player.call.pause_stream(msg.chat.id)
    await msg.reply_text("⏸ Paused")


@bot.on_message(cmd("resume") & filters.group)
async def resume_cmd(_: Client, msg: Message):
    await player.call.resume_stream(msg.chat.id)
    await msg.reply_text("▶️ Resumed")


@bot.on_message(cmd("end") & filters.group)
async def end_cmd(_: Client, msg: Message):
    queues.clear(msg.chat.id)
    await player.call.leave_group_call(msg.chat.id)
    await msg.reply_text("🛑 Stopped and queue cleared")


@bot.on_message(cmd("queue") & filters.group)
async def queue_cmd(_: Client, msg: Message):
    items = queues.list(msg.chat.id)
    if not items:
        return await msg.reply_text("Queue empty")
    lines = [f"**Queue ({len(items)})**"]
    for i, track in enumerate(items[:15], 1):
        lines.append(f"`{i}.` {track.title}")
    await msg.reply_text("\n".join(lines))


@bot.on_message((cmd("ai") | cmd("ask")) & filters.group)
async def ai_cmd(_: Client, msg: Message):
    if not ai.enabled:
        return await msg.reply_text("⚠️ OPENAI_API_KEY missing. AI feature disabled.")

    if len(msg.command) < 2:
        return await msg.reply_text("Usage: /ai <question>")

    prompt = " ".join(msg.command[1:])
    status = await msg.reply_text("🤖 Thinking...")
    try:
        answer = await ai.ask(prompt)
    except Exception as e:
        return await status.edit_text(f"❌ AI error: {e}")

    await status.edit_text(answer[:4000])


@bot.on_message(cmd("summarize") & filters.group)
async def summarize_cmd(_: Client, msg: Message):
    if not ai.enabled:
        return await msg.reply_text("⚠️ OPENAI_API_KEY missing. AI feature disabled.")

    if not msg.reply_to_message or not msg.reply_to_message.text:
        return await msg.reply_text("Reply to a text message and use /summarize")

    status = await msg.reply_text("🧠 Summarizing...")
    try:
        summary = await ai.summarize(msg.reply_to_message.text)
    except Exception as e:
        return await status.edit_text(f"❌ AI error: {e}")

    await status.edit_text(summary[:4000])


@bot.on_message(cmd("imagine") & filters.group)
async def imagine_cmd(_: Client, msg: Message):
    if not ai.enabled:
        return await msg.reply_text("⚠️ OPENAI_API_KEY missing. AI feature disabled.")

    if len(msg.command) < 2:
        return await msg.reply_text("Usage: /imagine <prompt>")

    prompt = " ".join(msg.command[1:])
    status = await msg.reply_text("🎨 Generating image...")

    try:
        image_bytes = await ai.generate_image(prompt)
    except Exception as e:
        return await status.edit_text(f"❌ AI image error: {e}")

    bio = BytesIO(image_bytes)
    bio.name = "ai-image.png"
    await msg.reply_photo(photo=bio, caption=f"🖼 Prompt: `{prompt}`")
    await status.delete()


async def run() -> None:
    await assistant.start()
    await bot.start()
    await player.start()
    logging.info("Music bot started successfully")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(run())
