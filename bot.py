import random
import sqlite3
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8822234299:AAE6Ria9P6mv_joakdq4ZfIsF_pQHenFigs"

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    size INTEGER DEFAULT 0,
    last_time TEXT
)
""")
conn.commit()


def get_user(user):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
    row = cur.fetchone()

    if not row:
        cur.execute(
            "INSERT INTO users (user_id, username, size, last_time) VALUES (?, ?, ?, ?)",
            (user.id, user.username or user.first_name, 0, None)
        )
        conn.commit()
        return (user.id, user.username or user.first_name, 0, None)

    return row


async def dick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user(user)

    last_time = data[3]

    if last_time:
        last = datetime.fromisoformat(last_time)
        if datetime.now() - last < timedelta(hours=12):
            wait = timedelta(hours=12) - (datetime.now() - last)
            await update.message.reply_text(f"⏳ Подожди {wait.seconds//3600}ч {(wait.seconds%3600)//60}м")
            return

    size = data[2]

    roll = random.random()

    if roll < 0.01:
        change = 100
        text = f"💥 ДЖЕКПОТ! +100 см\nТеперь: {size + change}"
    elif roll < 0.26:
        change = -random.randint(1, 5)
        text = f"📉 Уменьшение -{abs(change)} см\nТеперь: {max(0, size + change)}"
    else:
        change = random.randint(1, 10)
        text = f"📈 Рост +{change} см\nТеперь: {size + change}"

    new_size = max(0, size + change)

    cur.execute(
        "UPDATE users SET size=?, last_time=?, username=? WHERE user_id=?",
        (new_size, datetime.now().isoformat(), user.username or user.first_name, user.id)
    )
    conn.commit()

    await update.message.reply_text(text)


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("SELECT username, size FROM users ORDER BY size DESC LIMIT 10")
    rows = cur.fetchall()

    text = "🏆 ТОП:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. {r[0]} — {r[1]} см\n"

    await update.message.reply_text(text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команды: /dick /top")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dick", dick))
    app.add_handler(CommandHandler("top", top))

    print("Bot started")
    import asyncio

def main():
    app = Application.builder().token(TOKEN).build()
    print("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()


