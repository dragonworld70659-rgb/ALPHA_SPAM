# Telegram Music Bot + Advanced AI (Heroku Ready)

Ye project ab **Music + AI super bot** hai:
- Group VC music play/queue
- AI QnA, summary, image generation
- Heroku deploy ready setup

## 🚀 Features
### Music
- `/play <name/url>` YouTube stream
- `/skip`, `/pause`, `/resume`, `/end`
- `/queue`, `/ping`, `/help`

### Advanced AI
- `/ai <question>` — smart chatbot answer
- `/summarize` — kisi replied text ka summary (Hinglish style)
- `/imagine <prompt>` — AI image generate

## 🔐 Required Env Vars
Copy example:
```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `API_ID` | ✅ | Telegram API ID |
| `API_HASH` | ✅ | Telegram API HASH |
| `BOT_TOKEN` | ✅ | @BotFather bot token |
| `STRING_SESSION` | ✅ | Assistant account Pyrogram string session |
| `OPENAI_API_KEY` | ⚠️ for AI | OpenAI API key (AI commands ke liye required) |
| `AI_MODEL` | ❌ | default `gpt-4.1-mini` |
| `AI_IMAGE_MODEL` | ❌ | default `gpt-image-1` |
| `SUDO_USERS` | ❌ | Space-separated user IDs |
| `COMMAND_PREFIXES` | ❌ | Default `/ ! .` |


### AI key file me kaise daale
`.env` file me directly ye line set karo:
```env
OPENAI_API_KEY=sk-your_openai_api_key_here
```

## 🧪 Local Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## ☁️ Heroku Deploy
```bash
heroku create your-app-name
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... STRING_SESSION=...
heroku config:set OPENAI_API_KEY=... AI_MODEL=gpt-4.1-mini AI_IMAGE_MODEL=gpt-image-1
git push heroku main
```

## ✅ Important Setup
1. Assistant account (`STRING_SESSION`) group me add karo.
2. Assistant ko VC join permission/admin do.
3. Voice chat start karo.
4. `/play` + `/ai` test karo.

Agar chaho next update me mai add kar dunga:
- Auto-DJ mode (24/7 radio)
- AI song recommendations based on chat mood
- Lyrics explain + translation mode
- Per-group memory + custom AI persona
