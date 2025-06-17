import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
import json
import os
from main import LOG_GROUP_ID

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

import json
from datetime import datetime

TASK_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_tasks(data):
    with open(TASK_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != LOG_GROUP_ID:
        return
    user_id = str(update.effective_user.id)
    data = load_tasks()
    week = datetime.utcnow().strftime("%Y-%U")

    if user_id not in data:
        data[user_id] = {}
    if week not in data[user_id]:
        data[user_id][week] = 0

    data[user_id][week] += 1
    save_tasks(data)

async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_tasks()
    week = datetime.utcnow().strftime("%Y-%U")
    count = data.get(user_id, {}).get(week, 0)
    in_log_group = update.effective_chat.id == LOG_GROUP_ID

    def generate_progress_bar(count, total=2500, parts=10):
        filled = int((count / total) * parts)
        return "✅ " * parts if filled >= parts else "🔸" * filled + "⚪" * (parts - filled)

    bar = generate_progress_bar(count)

    base = (
        f"🎯 *Weekly Task Challenge*\n\n"
        f"👤 User: `{update.effective_user.first_name}`\n"
        f"💬 Messages Sent: *{count}/2500*\n"
        f"📈 Progress:\n{bar}\n"
    )

    if in_log_group:
        extra = (
            f"\n🏆 *Complete your task to earn:*\n"
            f"  • 💰 300 Duskar\n"
            f"  • 💎 Bonus Gems (Chance)\n"
            f"  • 🥚 Rare Egg (Low Chance)\n\n"
            f"🔁 Keep chatting in this group to progress!"
        )
    else:
        extra = (
            f"\n⚠️ *Progress is only tracked in the official log group.*\n"
            f"🛑 You currently have no progress.\n\n"
            f"👉 [Join the Dragons Realm Log Group](https://t.me/YourLogGroupLink) to begin your journey!"
        )

    await update.message.reply_text(base + extra, parse_mode="Markdown", disable_web_page_preview=True)

