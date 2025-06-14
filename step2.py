# step2.py

import json, os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

BOT_OWNER_ID = 6020886539 # Replace with your Telegram ID
USER_FILE = "users.json"
GROUP_FILE = "group.json"

# Load user data
def load_user_data():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_user_data(user_id):
    users = load_user_data()
    return users.get(str(user_id))

def load_group_ids():
    if os.path.exists(GROUP_FILE):
        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return list(data.keys())  # Group IDs are the keys
    return []

async def userstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = None
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    elif context.args:
        username = context.args[0].lstrip('@')
        for u_id, u_data in load_user_data().items():
            if u_data.get("username", "").lower() == username.lower():
                user = type('User', (), {'id': int(u_id), 'first_name': u_data.get("first_name", username)})
                break
        if not user:
            await update.message.reply_text("❌ Username not found.")
            return
    else:
        user = update.effective_user

    data = get_user_data(user.id)
    if not data:
        await update.message.reply_text("No data found for this user.")
        return

    # Format dragons list
    dragons = data.get("dragons", [])
    if not dragons:
        dragon_info = "🚫 No dragons yet"
    else:
        dragon_info = "\n".join(
            [f"• {d.get('name', 'Unnamed')} ({d.get('element', '?')}) – 🐉 Lv.{d.get('level', 1)} | ⚡ {d.get('power', 0)}" for d in dragons]
        )

    msg = (
        f"📊 Stats for {user.first_name}:\n\n"
        f"🐉 Dragons ({len(dragons)}):\n{dragon_info}\n\n"
        f"🥚 Eggs: {data.get('eggs', 0)}\n"
        f"💰 Duskar: {data.get('coins', 0)}\n"
        f"⭐ XP: {data.get('xp', 0)}\n"
        f"🔼 Level: {data.get('level', 1)}"
    )
    await update.message.reply_text(msg)

from telegram.constants import ParseMode

BOT_OWNER_ID = 6020886539  # your bot owner ID

def load_mods():
    with open("mod.json", "r") as f:
        return json.load(f).get("mods", [])

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != str(BOT_OWNER_ID) and user_id not in load_mods():
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    users = load_user_data()
    groups = load_group_ids()
    success, failed = 0, 0

    # Broadcast a replied message
    if update.message.reply_to_message:
        for uid in users:
            try:
                await context.bot.copy_message(
                    chat_id=int(uid),
                    from_chat_id=update.effective_chat.id,
                    message_id=update.message.reply_to_message.message_id
                )
                success += 1
            except:
                failed += 1

        for gid in groups:
            try:
                await context.bot.copy_message(
                    chat_id=int(gid),
                    from_chat_id=update.effective_chat.id,
                    message_id=update.message.reply_to_message.message_id
                )
                success += 1
            except:
                failed += 1

    else:
        if not context.args:
            await update.message.reply_text("❗ Usage: /broadcast <message> or reply to a message.")
            return

        message = " ".join(context.args)
        for uid in users:
            try:
                await context.bot.send_message(chat_id=int(uid), text=message, parse_mode=ParseMode.HTML)
                success += 1
            except:
                failed += 1

        for gid in groups:
            try:
                await context.bot.send_message(chat_id=int(gid), text=message, parse_mode=ParseMode.HTML)
                success += 1
            except:
                failed += 1

    await update.message.reply_text(
        f"📢 <b>Broadcast Summary</b>\n\n✅ Sent: <b>{success}</b>\n❌ Failed: <b>{failed}</b>",
        parse_mode=ParseMode.HTML
    )


import random
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
import os
import json

USER_FILE = "users.json"

RARITY_POOL = [
    ("Normal", 50, "🥚"),
    ("Rare", 36, "🔷"),
    ("Legendary", 10, "🌟"),
    ("Ultimate", 4, "💠")
]

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def choose_rarity():
    roll = random.randint(1, 100)
    total = 0
    for rarity, chance, emoji in RARITY_POOL:
        total += chance
        if roll <= total:
            return rarity, emoji
    return "Normal", "🥚"

def chance_to_hatch(rarity):
    if rarity == "Normal":
        return random.random() < 0.5
    elif rarity == "Rare":
        return random.random() < 0.75
    return True

async def getegg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USER_FILE)
    user = users.setdefault(user_id, {})

    today = datetime.now().date()
    last_egg = user.get("last_egg")
    if last_egg and datetime.fromisoformat(last_egg).date() == today:
        await update.message.reply_text("🕒 You've already received an egg today. Try again tomorrow!")
        return

    eggs = user.setdefault("eggs", [])
    rarity, emoji = choose_rarity()
    will_hatch = chance_to_hatch(rarity)

    egg_data = {
        "rarity": rarity,
        "emoji": emoji,
        "timestamp": datetime.now().isoformat(),
        "status": "pending",
        "will_hatch": will_hatch
    }

    eggs.append(egg_data)
    user["last_egg"] = datetime.now().isoformat()
    save_json(USER_FILE, users)

    hatch_text = "✅ This egg will hatch into a dragon!" if will_hatch else "❌ This egg might not hatch successfully."

    await update.message.reply_text(
        f"{emoji} You received a <b>{rarity}</b> Egg!\n{hatch_text}",
        parse_mode="HTML"
    )

async def eggs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from datetime import datetime, timedelta

    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.get(user_id, {})
    egg_list = user.get("eggs", [])

    if not egg_list:
        await update.message.reply_text("🥚 You have no eggs.")
        return

    HATCH_TIMES = { "Normal": 1, "Rare": 2, "Legendary": 4, "Ultimate": 6 }

    lines = []
    for egg in egg_list:
        if egg["status"] != "pending":
            continue
        laid_time = datetime.fromisoformat(egg["timestamp"])
        hatch_time = laid_time + timedelta(hours=HATCH_TIMES.get(egg["rarity"], 1))
        time_left = hatch_time - datetime.now()

        if time_left.total_seconds() > 0:
            status = f"⏳ {int(time_left.total_seconds() // 60)} min left"
        else:
            status = "✅ Ready to hatch"

        lines.append(f"{egg['emoji']} <b>{egg['rarity']}</b> Egg — {status}")

    await update.message.reply_text(
        "<b>Your Eggs:</b>\n" + "\n".join(lines),
        parse_mode="HTML"
    )

async def eghatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from datetime import datetime, timedelta

    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.setdefault(user_id, {})
    eggs = user.setdefault("eggs", [])
    dragons = user.setdefault("dragons", [])

    HATCH_TIMES = { "Normal": 1, "Rare": 2, "Legendary": 4, "Ultimate": 6 }
    RARITY_DRAGONS = {
        "Normal": ["Drakelet", "Scaleling"],
        "Rare": ["Fireclaw", "Aqualing"],
        "Legendary": ["Stormfang", "Voidhorn"],
        "Ultimate": ["Solarion", "Duskmaw"]
    }

    hatched = []
    for egg in eggs:
        if egg["status"] != "pending":
            continue
        laid_time = datetime.fromisoformat(egg["timestamp"])
        hatch_time = laid_time + timedelta(hours=HATCH_TIMES.get(egg["rarity"], 1))
        if datetime.now() < hatch_time:
            continue
        egg["status"] = "hatched"
        if egg.get("will_hatch", True):
            name = random.choice(RARITY_DRAGONS.get(egg["rarity"], ["Mystic"]))
            dragon = {
                "name": name,
                "element": "Unknown",
                "power": random.randint(25, 60),
                "level": 1
            }
            dragons.append(dragon)
            hatched.append(f"{egg['emoji']} <b>{egg['rarity']}</b> Egg → 🐉 <b>{name}</b>")

    save_json("users.json", users)

    if not hatched:
        await update.message.reply_text("⏳ No eggs are ready to hatch yet.")
    else:
        await update.message.reply_text(
            "🐣 <b>Hatched Dragons:</b>\n" + "\n".join(hatched),
            parse_mode="HTML"
        )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json, os

MODS_FILE = "mod.json"
OWNER_ID = 6020886539  # Replace with your Telegram user ID

def load_mods():
    if os.path.exists(MODS_FILE):
        with open(MODS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_mods(mods):
    with open(MODS_FILE, "w", encoding="utf-8") as f:
        json.dump(mods, f, indent=2)

async def addmod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(
            "🚫 Only the <b>DragonDusk Owner</b> can use this command.", parse_mode="HTML")
        return

    user = update.message.reply_to_message.from_user if update.message.reply_to_message else (context.args and await context.bot.get_chat(context.args[0].lstrip("@")))
    if not user:
        await update.message.reply_text("⚠️ Please reply to a user or provide a valid @username.")
        return

    mods = load_mods()
    if any(mod['id'] == user.id for mod in mods):
        await update.message.reply_text("ℹ️ This user is already a moderator.")
        return

    mods.append({
        "id": user.id,
        "name": user.full_name,
        "username": user.username or "None"
    })
    save_mods(mods)

    await update.message.reply_text(
        text=(
            "🆕 <b>Moderator Appointed!</b>\n\n"
            f"👤 Name: <b>{user.full_name}</b>\n"
            f"🔗 Username: <code>@{user.username or 'None'}</code>\n"
            "🛡️ Role: <b>DragonDusk Moderator</b>\n\n"
            "🎖️ This tamer has joined the Council of Flame."
        ),
        parse_mode="HTML"
    )

async def mods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mods = load_mods()
    if not mods:
        await update.message.reply_text("⚠️ No moderators have been assigned yet.")
        return

    mods_text = "\n".join([f"🛡️ <b>{mod['name']}</b> — <code>@{mod['username']}</code>" for mod in mods])
    await update.message.reply_text(
        text=f"📋 <b>Current Moderators of DragonDusk</b>:\n\n{mods_text}",
        parse_mode="HTML"
    )

async def rmmod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(
            "🚫 You do not have the authority to remove moderators.", parse_mode="HTML")
        return

    user = update.message.reply_to_message.from_user if update.message.reply_to_message else (context.args and await context.bot.get_chat(context.args[0].lstrip("@")))
    if not user:
        await update.message.reply_text("⚠️ Please reply to a user or provide a valid @username.")
        return

    mods = load_mods()
    if not any(mod['id'] == user.id for mod in mods):
        await update.message.reply_text("⚠️ This user is not a moderator.")
        return

    mods = [mod for mod in mods if mod['id'] != user.id]
    save_mods(mods)

    await update.message.reply_text(
        text=(
            "❌ <b>Moderator Removed!</b>\n\n"
            f"👤 <b>{user.full_name}</b> (<code>@{user.username or 'None'}</code>) is no longer part of the council.\n"
            "🪓 Power revoked successfully."
        ),
        parse_mode="HTML"
    )


#Clansss

