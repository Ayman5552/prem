import os
import random
import asyncio
from fastapi import FastAPI
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Token aus ENV lesen (z.B. bei Render als ENV Variable setzen)
TOKEN = os.getenv("TOKEN") or "DEIN_TELEGRAM_BOT_TOKEN_HIER"

VIDEO_ORDNER = r"C:\Users\night\Desktop\PREM"

nachricht = (
    "🎁 *Geschenk zum Launch:*\n"
    "Nur heute bis *0:00 Uhr* – *Premium VIP für 45 € statt 150 €!*\n\n"
    "🤖 *Wofür ist der Bot da?*\n"
    "👉 Der Bot dient *nur dazu*, dir zu zeigen, *wie viele Weiber aktuell online* in der Premium VIP Gruppe sind.\n"
    "So kannst du dir vorher ein Bild machen – *damit du nicht blind irgendwas kaufst*.\n\n"
    "✅ Transparent & fair – keine Überraschungen.\n\n"
    "*So funktioniert's:*\n"
    "1️⃣ Starte den Bot\n"
    "2️⃣ Wähle: 🇩🇪 *Deutschland* → dein *Bundesland* → deine *Stadt* (z. B. Köln)\n"
    "3️⃣ Entweder bleibst du in der Stadt oder gehst weiter zu *Stadtteilen*\n"
    "4️⃣ Dann kannst du auswählen zwischen:\n"
    "   📸 *Nudes*  |  🤝 *Treffen*  |  👻 *Snaps*\n"
    "   Alles sauber sortiert.\n\n"
    "💳 *Zahlung möglich mit:*\n"
    "PayPal, Bank, Crypto, PaySafeCard\n\n"
    "Nach Verifizierung erhältst du mehrere Backup-Links zur Gruppe – falls mal eine gesperrt wird (was fast nie passiert).\n\n"
    "📲 *Privat starten mit* `/start`\n\n"
    "🔜 [@PremiumXVIP_bot](https://t.me/PremiumXVIP_bot) 🔙"
)

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot läuft"}

async def prem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat = update.effective_chat

    member: ChatMember = await context.bot.get_chat_member(chat.id, user_id)
    if member.status not in ['administrator', 'creator']:
        await context.bot.send_message(
            chat_id=chat.id,
            text="⛔️ Nur Gruppen-Admins dürfen diesen Befehl verwenden."
        )
        return

    await context.bot.send_message(
        chat_id=chat.id,
        text=nachricht,
        parse_mode="Markdown"
    )

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

    await context.bot.send_message(
        chat_id=chat.id,
        text="📽️ Das ist eine Vorschau, was z.B. in Düsseldorf bei Nudes zu sehen ist."
    )

async def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("prem", prem_command))
    await application.initialize()
    await application.start()
    return application

async def main():
    # Telegram-Bot starten
    application = await start_bot()
    
    # Uvicorn Webserver für FastAPI starten
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)

    # Webserver und Bot laufen parallel
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
