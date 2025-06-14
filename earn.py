import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
import json
import os

USER_FILE = "users.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def can_earn(last_time, cooldown_minutes):
    if not last_time:
        return True
    last = datetime.fromisoformat(last_time)
    return datetime.now() - last >= timedelta(minutes=cooldown_minutes)

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USER_FILE)
    user = users.setdefault(user_id, {})

    last_work = user.get("last_work")
    if not can_earn(last_work, cooldown_minutes=180):  # 3 hour cooldown
        next_time = datetime.fromisoformat(last_work) + timedelta(minutes=180)
        time_left = next_time - datetime.now()
        minutes = int(time_left.total_seconds() // 60)
        await update.message.reply_text(f"🕒 You need to rest before working again. Try in {minutes} min.")
        return

    earned = random.randint(80, 160)
    user["duskar"] = user.get("duskar", 0) + earned
    user["last_work"] = datetime.now().isoformat()

    save_json(USER_FILE, users)

    await update.message.reply_text(
        f"🔨 You worked hard and earned <b>{earned} Duskar</b>!\n"
        f"💰 Your total Duskar: <b>{user['duskar']}</b>",
        parse_mode="HTML"
    )

async def mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.setdefault(user_id, {})

    last_mine = user.get("last_mine")
    cooldown = timedelta(minutes=90)

    if last_mine:
        last_time = datetime.fromisoformat(last_mine)
        if datetime.now() - last_time < cooldown:
            next_time = last_time + cooldown
            minutes = int((next_time - datetime.now()).total_seconds() // 60)
            await update.message.reply_text(f"⛏️ You've already mined recently. Try again in {minutes} min.")
            return

    earned = random.randint(40, 100)
    user["duskar"] = user.get("duskar", 0) + earned
    user["last_mine"] = datetime.now().isoformat()
    save_json("users.json", users)

    await update.message.reply_text(
        f"⛏️ You mined some rare crystals and earned <b>{earned} Duskar</b>!\n"
        f"💰 Total Duskar: <b>{user['duskar']}</b>",
        parse_mode="HTML"
    )

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.setdefault(user_id, {})

    last_daily = user.get("last_daily")
    today = datetime.now().date()

    if last_daily and datetime.fromisoformat(last_daily).date() == today:
        await update.message.reply_text("📅 You've already claimed your daily reward today. Come back tomorrow!")
        return

    earned = 100
    user["duskar"] = user.get("duskar", 0) + earned
    user["last_daily"] = datetime.now().isoformat()
    save_json("users.json", users)

    await update.message.reply_text(
        f"🎁 Daily reward collected: <b>{earned} Duskar</b>!\n"
        f"💰 Total Duskar: <b>{user['duskar']}</b>",
        parse_mode="HTML"
    )
