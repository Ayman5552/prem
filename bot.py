import os
import random
import asyncio
from fastapi import FastAPI
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = FastAPI()

TOKEN = os.getenv("BOT_TOKEN")
VIDEO_ORDNER = "videos"  # Ordner relativ im Projektverzeichnis

nachricht = (
    "🎁 *Geschenk zum Launch:*\n"
    "Nur heute bis *0:00 Uhr* – *Premium VIP für 45 € statt 150 €!*\n\n"
    "..."
)

@app.get("/")
async def root():
    return {"status": "Bot läuft"}

async def prem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat = update.effective_chat

    member: ChatMember = await context.bot.get_chat_member(chat.id, user_id)
    if member.status not in ['administrator', 'creator']:
        await context.bot.send_message(chat_id=chat.id, text="⛔️ Nur Gruppen-Admins dürfen diesen Befehl verwenden.")
        return

    await context.bot.send_message(chat_id=chat.id, text=nachricht, parse_mode="Markdown")

    if not os.path.isdir(VIDEO_ORDNER):
        await context.bot.send_message(chat_id=chat.id, text="⚠️ Video-Ordner nicht gefunden.")
        return

    alle_dateien = [f for f in os.listdir(VIDEO_ORDNER) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
    if not alle_dateien:
        await context.bot.send_message(chat_id=chat.id, text="⚠️ Keine Videos im Ordner gefunden.")
        return

    video_dateien = random.sample(alle_dateien, min(2, len(alle_dateien)))

    for datei in video_dateien:
        video_pfad = os.path.join(VIDEO_ORDNER, datei)
        with open(video_pfad, "rb") as video:
            await context.bot.send_video(chat_id=chat.id, video=video)

    await context.bot.send_message(chat_id=chat.id, text="📽️ Vorschau für Düsseldorf bei Nudes.")

async def main():
    # Telegram-Bot Setup
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("prem", prem_command))
    await app_bot.initialize()
    await app_bot.start()
    print("✅ Bot gestartet")

    # Webserver parallel starten
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    server = uvicorn.Server(config)

    # Webserver "blockiert" das Ende – aber Bot läuft im Hintergrund
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
