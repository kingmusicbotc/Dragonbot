from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.helpers import escape_markdown
import json, os, time, random
from telegram.constants import ChatMemberStatus
from telegram.ext import ChatMemberHandler
from step2 import userstats, broadcast
from battle import challenge,  select_dragon_callback, handle_move
from telegram.ext import CallbackQueryHandler
from battle import load_json, cancel_battle
from earn import work, mine, daily
from step2 import getegg, eggs, eghatch, addmod, mods, rmmod
from clan import createclan, joinclan, myclan, leaveclan, disbandclan, clanchallenge, accept_clanwar




# === CONFIG ===
TOKEN = "8040202761:AAF_HEGJxbZjKsgJANNQQRP4ahXftlMsqCQ"
LOG_GROUP_ID = -1002689253330
JSON_FILE = "users.json"
GROUP_FILE = "group.json"
ALLOWED_ADMINS = [6020886539, 7793966371]
BOT_VERSION = "1.0.0"
BOT_OWNER = "𝑥𝑜𝑓𝑎 🔱"
IMAGE_URL = "https://graph.org/file/c3057fdb933a40aac35a8-24eb9a945f2183a64c.jpg"
start_time = time.time()

# === JSON Helpers ===
def load_json(file):
    if not os.path.exists(file):
        return {}
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_users():
    return load_json(JSON_FILE)

def save_users(data):
    save_json(JSON_FILE, data)

def load_group_data():
    return load_json(GROUP_FILE)

def save_group_data(data):
    save_json(GROUP_FILE, data)

def load_group_data():
    if not os.path.exists(GROUP_FILE):
        return {}
    try:
        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_group_data(data):
    with open(GROUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

import json

USER_FILE = "users.json"

def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def migrate_gold_to_duskar():
    users = load_json(USER_FILE)
    migrated = 0

    for user_id, data in users.items():
        if "gold" in data and "duskar" not in data:
            data["duskar"] = data["gold"]
            migrated += 1
        if "gold" in data:
            del data["gold"]  # remove gold completely

    save_json(USER_FILE, users)
    print(f"✅ Migration complete. {migrated} users now have 'duskar' instead of 'gold'.")

# Run it
migrate_gold_to_duskar()


# === Uptime Helper ===
def get_uptime():
    seconds = int(time.time() - start_time)
    hrs, secs = divmod(seconds, 3600)
    mins, secs = divmod(secs, 60)
    return f"{hrs:02}:{mins:02}:{secs:02}"

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden
import json, os

# === Configs ===
LOG_GROUP_ID = "-1002689253330"
SUPPORT_LINK = "https://t.me/+P5lRNelMP2w3N2M1"
OWNER_USERNAME = "meee_offline"
IMAGE_URL = "https://graph.org/file/c3057fdb933a40aac35a8-24eb9a945f2183a64c.jpg"
START_STICKER = "CAACAgEAAxkBAAID4GhLtzh83Y1jf5cWyFj7vwIZnEuvAAIVAwACr0ZxRUcBrjQ033EnNgQ"
USERS_FILE = "users.json"

# === JSON Helpers ===
def load_users():
    if not os.path.exists(USERS_FILE):
        print("[INFO] users.json not found, creating new data store.")
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("[LOAD ERROR]", e)
        return {}

def save_users(data):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print("[SAVE SUCCESS] User data updated.")
    except Exception as e:
        print("[SAVE ERROR]", e)

# === /start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    args = context.args
    print(f"🚀 /start triggered by {user_id} ({user.full_name})")

    # Redirect to /help if argument is "help"
    if args and args[0].lower() == "help":
        await help_command(update, context)
        return

    users = load_users()
    is_new = False

    if user_id not in users:
        is_new = True
        users[user_id] = {
            "name": user.full_name,
            "dragons": [],
            "level": 1,
            "gold": 100,
            "hatched": False,
            "gems": 0,
            "win": 0,
            "loss": 0
        }
        save_users(users)
        print(f"[NEW USER] {user.full_name} ({user_id}) added.")

    # Log to group if new user
    if is_new:
        try:
            username = f"@{user.username}" if user.username else "No username"
            await context.bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=(
                    f"🆕 <b>New Dragon Tamer joined!</b>\n"
                    f"👤 <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
                    f"🔗 Username: {username}\n"
                    f"🆔 ID: <code>{user.id}</code>"
                ),
                parse_mode=ParseMode.HTML
            )
            print("[LOG SENT] New user logged to group.")
        except Exception as e:
            print(f"[LOG ERROR] {e.__class__.__name__}: {e}")

    # Send welcome sticker
    try:
        await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=START_STICKER)
    except Exception as e:
        print("[STICKER ERROR]", e)

    # Prepare keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛠 Support", url=SUPPORT_LINK),
            InlineKeyboardButton("👑 Chat with Owner", url=f"https://t.me/{OWNER_USERNAME}")
        ],
        [
            InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{context.bot.username}?startgroup=true"),
            InlineKeyboardButton("📜 Commands", url=f"https://t.me/{context.bot.username}?start=help")
        ]
    ])

    # Prepare welcome message
    safe_name = user.first_name.replace("<", "").replace(">", "")
    caption = (
        f"🐉 <u><b>Welcome, Dragon Tamer {safe_name}!</b></u>\n\n"
        "🌌 <i>You have entered the mystical realm of</i> <b>⟪ 𝐃𝐑𝐀𝐆𝐎𝐍𝐃𝐔𝐒𝐊 ⟫</b>\n"
        "━━━━━━━━━━━━━━━\n"
        "✨ <b>Your Journey Begins:</b>\n"
        "🥚 <code>/getegg</code> – Discover magical dragon eggs\n"
        "🐣 <code>/eghatch</code> – Hatch them into mighty beasts\n"
        "🐲 <code>/dragons</code> – View & manage your dragon army\n"
        "⚔️ <code>/challenge</code> – Duel other tamers and rise\n"
        "💎 Earn <b>Duskar</b> & <b>Gems</b> to evolve your dragons\n"
        "🛡️ Build. 🐾 Tame. 🔥 Conquer.\n"
        "━━━━━━━━━━━━━━━\n"
        "🪄 <i>Begin your legacy now with</i> <code>/hatch</code> 🐉\n"
        "🌠 <i>Will you become the legend whispered in dragon tales?</i>"
    )

    # Send welcome image
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=IMAGE_URL,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        print("[PHOTO SENT] Welcome image sent.")
    except Exception as e:
        print("[PHOTO ERROR]", e)
        await update.message.reply_text(
            caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )

from telegram.ext import MessageHandler, filters

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def get_sticker_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if it's a private chat
    if update.effective_chat.type != "private":
        return  # Ignore if not private

    sticker = update.message.sticker
    if sticker:
        await update.message.reply_text(
            f"🆔 Sticker File ID:\n<code>{sticker.file_id}</code>",
            parse_mode=ParseMode.HTML
        )

# === /registergroup Command ===
async def registergroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat.type.endswith("group"):
        await update.message.reply_text("❌ This command can only be used in a group.")
        return

    group_data = load_group_data()
    group_id = str(chat.id)
    group_data[group_id] = {
        "title": chat.title,
        "username": f"@{chat.username}" if chat.username else "N/A",
        "members": [],
        "hatched_count": 0
    }
    save_group_data(group_data)
    await update.message.reply_text(f"✅ Group '{chat.title}' registered successfully!")
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    group_data = load_group_data()
    uptime = get_uptime()

    total_users = len(users)
    total_coins = sum(u.get("gold", 0) for u in users.values())
    started_users = sum(1 for u in users.values() if u.get("dragons") and len(u["dragons"]) > 0)

    started_chats = len(group_data)  # <- Fixed this

    bot_username = context.bot.username

    group_info = group_data.get(str(update.effective_chat.id))
    group_stats = "\n\n<b>Group Stats</b>\nNot registered. Use /rgroup." if not group_info else (
        f"\n\n<b>Group Stats</b>\n"
        f"📛 Name: {group_info['title']}\n"
        f"🐲 Hatched Dragons: {group_info['hatched_count']}"
    )

    status_text = (
        f"🤖 <b>Bot Status</b> 🤖\n\n"
        f"🆔 <b>Bot Username:</b> @{bot_username}\n"
        f"⏰ <b>Uptime:</b> {uptime}\n"
        f"👥 <b>Total Users:</b> {total_users}\n"
        f"💰 <b>Total Duskar Distributed:</b> {total_coins}\n"
        f"📊 <b>Additional Stats:</b>\n"
        f" ┗ Started Users: {started_users}\n"
        f" ┗ Started Chats: {started_chats}\n"
        f"⚙️ <b>Version:</b> {BOT_VERSION}\n"
        f"👑 <b>Owned by:</b> REDEX "
    ) + group_stats

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=IMAGE_URL,
        caption=status_text,
        parse_mode="HTML"
    )

# === /hatch Command ===
dragon_names = ["Pyron", "Aetherwing", "Blazetail", "Frostclaw", "Venomscale"]
dragon_elements = {
    "Fire": {"image": "https://graph.org/file/aaa708b476d9fcf94805e-fe7bd32d2f0e0cde4a.jpg"},
    "Water": {"image": "https://graph.org/file/d2a54e29e6690ce8d2f08-c692c3146bf2893ab4.jpg"},
    "Earth": {"image": "https://graph.org/file/3cfef90871915ad76b157-21176a4771834b6bfb.jpg"},
    "Air": {"image": "https://graph.org/file/0189adaf01f60a9a86607-176420f07183947b31.jpg"},
    "Shadow": {"image": "https://graph.org/file/ee2af282e44c32e5a2c93-54be7dacd78a1d30fd.jpg"}
}

async def hatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = str(user.id)
    users = load_users()

    if user_id not in users:
        await update.message.reply_text("❗ Please use /start before hatching your dragon.")
        return

    if users[user_id].get("hatched", False):
        await update.message.reply_text("❌ You've already hatched your first dragon!")
        return

    name = random.choice(dragon_names)
    element = random.choice(list(dragon_elements.keys()))
    power = random.randint(20, 45)
    level = 1
    dragon_img_url = dragon_elements[element]["image"]

    # Save dragon
    users[user_id]["dragons"].append({
        "name": name,
        "element": element,
        "power": power,
        "level": level
    })
    users[user_id]["hatched"] = True
    save_users(users)

    # Update group hatch count
    group_data = load_group_data()
    group_id = str(chat_id)
    if group_id in group_data:
        group_data[group_id]["hatched_count"] += 1
        save_group_data(group_data)

    dragon_text = (
        f"🎉 <b>Dragon Hatched!</b> 🐉\n\n"
        f"<b>👤 Tamer:</b> {user.full_name}\n"
        f"<b>📛 Name:</b> <code>{name}</code>\n"
        f"<b>🌪 Element:</b> <code>{element}</code>\n"
        f"<b>⚔️ Power:</b> <code>{power}</code>\n"
        f"<b>⭐ Level:</b> <code>{level}</code>\n\n"
        f"Train your dragon with more commands soon!"
    )

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=dragon_img_url,
        caption=dragon_text,
        parse_mode="HTML"
    )

    from telegram import InputFile

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.get(user_id, {})

    name = user.get("name", update.effective_user.first_name)
    duskar = user.get("duskar", 0)
    gems = user.get("gems", 0)
    wins = user.get("wins", 0)
    losses = user.get("losses", 0)
    total = wins + losses
    win_percent = round((wins / total) * 100, 2) if total > 0 else 0.0

    text = f"""
👤 <b>{name}'s Profile</b>

💰 Duskar: <b>{duskar}</b>
💎 Gems: <b>{gems}</b>

📊 Battle Stats:
✅ Wins: <b>{wins}</b>
❌ Losses: <b>{losses}</b>
📈 Win Rate: <b>{win_percent}%</b>
    """

    await update.message.reply_text(text, parse_mode="HTML")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_users().get(user_id)

    if not user_data:
        await update.message.reply_text("❌ You are not registered yet. Use /start to begin.")
        return

    dragons = user_data.get("dragons", [])

    if not dragons:
        await update.message.reply_text("🐣 You don't own any dragons yet. Use /hatch to get one!")
        return

    # Build dragon list text
    dragon_list = "\n".join(
        [f"{i+1}. 🐉 {dragon['name']} – Level {dragon.get('level', 1)}" for i, dragon in enumerate(dragons)]
    )

    await update.message.reply_text(
        f"📦 <b>Your Dragon Inventory:</b>\n\n{dragon_list}",
        parse_mode="HTML"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        users = load_json("users.json")
        user = users.get(user_id, {})

        duskar = user.get("duskar", 0)
        gems = user.get("gems", 0)

        await update.message.reply_text(
            f"💰 Duskar: <b>{duskar}</b>\n💎 Gems: <b>{gems}</b>",
            parse_mode="HTML"
        )

async def dragons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_users().get(user_id)

    if not user_data:
        await update.message.reply_text("❌ You are not registered. Use /start first.")
        return

    dragons = user_data.get("dragons", [])
    if not dragons:
        await update.message.reply_text("🐣 You don't have any dragons yet. Use /hatch to summon one!")
        return

    type_emojis = {
        "Fire": "🔥",
        "Water": "💧",
        "Earth": "🌱",
        "Air": "🌪️",
        "Ice": "❄️",
        "Electric": "⚡",
        "Dark": "🌑",
        "Light": "🌟",
        "Metal": "⚙️",
        "Dragon": "🐉"
    }

    msg = "🐉 <b>Your Dragons</b>\n\n"
    for i, d in enumerate(dragons, 1):
        emoji = type_emojis.get(d.get("type", ""), "🐉")
        name = d.get("name", "Unknown")
        level = d.get("level", 1)
        power = d.get("power", 0)
        msg += (
            f"{i}. {emoji} <b>{name}</b>\n"
            f"   • Type: {d.get('type', 'Unknown')}\n"
            f"   • Level: {level}\n"
            f"   • Power: {power} ⚡\n\n"
        )

    await update.message.reply_text(msg, parse_mode="HTML")

import datetime

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    user_data = users.get(user_id)

    if not user_data:
        await update.message.reply_text("❌ You are not registered. Use /start first.")
        return

    dragons = user_data.get("dragons", [])
    if not dragons:
        await update.message.reply_text("🐣 You don't have any dragons yet. Use /hatch to summon one!")
        return

    if not context.args:
        await update.message.reply_text("🍖 Usage: /feed <dragon_number>")
        return

    # Check Duskar
    if user_data.get("gold", 0) < 100:
        await update.message.reply_text("💸 You need at least 100 coins to feed a dragon.")
        return

    # Daily check
    today_str = datetime.date.today().isoformat()
    last_feed = user_data.get("last_feed")
    if last_feed == today_str:
        await update.message.reply_text("⏳ You can only feed once per day. Come back tomorrow!")
        return

    # Validate index
    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(dragons):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid dragon number.")
        return

    # Feed dragon
    dragon = dragons[index]
    added_power = random.randint(10, 25)
    dragon["power"] = dragon.get("power", 0) + added_power

    # Deduct coins and update feed time
    user_data["gold"] -= 100
    user_data["dragons"] = dragons
    user_data["last_feed"] = today_str
    users[user_id] = user_data
    save_users(users)

    await update.message.reply_text(
        f"🍖 You fed <b>{dragon['name']}</b>!\n"
        f"⚡ Power increased by <b>{added_power}</b>.\n"
        f"💰 100 Duskar spent | 🔋 Power: <b>{dragon['power']}</b>",
        parse_mode="HTML"
    )
import datetime

async def train(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    user_data = users.get(user_id)

    if not user_data:
        await update.message.reply_text("❌ You are not registered. Use /start first.")
        return

    dragons = user_data.get("dragons", [])
    if not dragons:
        await update.message.reply_text("🐣 You don't have any dragons yet.")
        return

    if not context.args:
        await update.message.reply_text("🏋️ Usage: /train <dragon_number>")
        return

    # Check if user has enough Duskar
    if user_data.get("gold", 0) < 150:
        await update.message.reply_text("💸 You need at least 150 coins to train a dragon.")
        return

    # Check 2-day cooldown
    last_train_str = user_data.get("last_train")
    today = datetime.date.today()

    if last_train_str:
        last_train = datetime.date.fromisoformat(last_train_str)
        days_since = (today - last_train).days
        if days_since < 2:
            await update.message.reply_text("⏳ You can train a dragon only once every 2 days.")
            return

    # Validate dragon number
    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(dragons):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid dragon number.")
        return

    dragon = dragons[index]
    power = dragon.get("power", 0)
    level = dragon.get("level", 1)
    required_power = level * 50

    if power < required_power:
        await update.message.reply_text(
            f"⚠️ <b>{dragon['name']}</b> needs at least {required_power} power to train!\n"
            f"Current Power: {power}",
            parse_mode="HTML"
        )
        return

    # Deduct Duskar
    user_data["gold"] -= 150
    user_data["last_train"] = today.isoformat()

    # 80% success chance
    success = random.random() < 0.8
    if success:
        dragon["level"] += 1
        dragon["power"] -= required_power
        msg = (
            f"🏆 Training successful!\n"
            f"🐉 <b>{dragon['name']}</b> leveled up to <b>Level {dragon['level']}</b>!\n"
            f"💰 150 Duskar spent | ⚡ Power left: {dragon['power']}"
        )
    else:
        msg = (
            f"😓 <b>{dragon['name']}</b> failed to level up.\n"
            f"💰 150 Duskar spent — no progress made."
        )

    users[user_id]["dragons"] = dragons
    users[user_id]["gold"] = user_data["gold"]
    users[user_id]["last_train"] = user_data["last_train"]
    save_users(users)

    await update.message.reply_text(msg, parse_mode="HTML")


async def release(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    user_data = users.get(user_id)

    if not user_data:
        await update.message.reply_text("❌ You are not registered. Use /start first.")
        return

    dragons = user_data.get("dragons", [])
    if not dragons:
        await update.message.reply_text("🐣 You don't have any dragons yet.")
        return

    if not context.args:
        await update.message.reply_text("🗑️ Usage: /release <dragon_number>")
        return

    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(dragons):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid dragon number.")
        return

    dragon = dragons.pop(index)
    refund = dragon["level"] * 10 + dragon["power"] // 10
    user_data["gold"] = user_data.get("gold", 0) + refund
    users[user_id]["dragons"] = dragons
    users[user_id]["gold"] = user_data["gold"]
    save_users(users)

    await update.message.reply_text(
        f"🗑️ You released <b>{dragon['name']}</b>.\n"
        f"💰 You earned <b>{refund} coins</b>.",
        parse_mode="HTML"
    )

    import datetime


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

HELP_IMAGE = "https://graph.org/file/c3057fdb933a40aac35a8-24eb9a945f2183a64c.jpg"

# /help command
HELP_IMAGE = "https://graph.org/file/c3057fdb933a40aac35a8-24eb9a945f2183a64c.jpg"  # same image as welcome

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest


import datetime
import random

def check_cooldown(last_time_str, hours):
        try:
            if not last_time_str:
                return True, 0
            last_time = datetime.datetime.fromisoformat(last_time_str)
            now = datetime.datetime.now()
            elapsed = (now - last_time).total_seconds()
            if elapsed >= hours * 3600:
                return True, 0
            else:
                remaining = int((hours * 3600 - elapsed) // 60)
                return False, remaining  # not ready, minutes left
        except:
            return True, 0  # If invalid format, allow use

import json
import random
import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

USER_FILE = "users.json"

# === File I/O ===
def load_users():
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Cooldown check ===
def check_cooldown(last_time: str, cooldown_minutes: int):
    if not last_time:
        return True, 0
    try:
        last = datetime.datetime.fromisoformat(last_time)
    except ValueError:
        return True, 0

    now = datetime.datetime.now()
    minutes_passed = (now - last).total_seconds() / 60
    if minutes_passed >= cooldown_minutes:
        return True, 0
    return False, int(cooldown_minutes - minutes_passed)


async def dailyegg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    user_data = users.get(user_id)

    if not user_data:
        await update.message.reply_text("❌ You are not registered. Use /start first.")
        return

    ready, minutes = check_cooldown(user_data.get("last_egg"), 12)
    if not ready:
        await update.message.reply_text(f"🥚 You've already searched for an egg.\nTry again in {minutes} min.", parse_mode="HTML")
        return

    found = random.random() < 0.2
    user_data["last_egg"] = datetime.datetime.now().isoformat()
    save_users(users)

    if found:
        await update.message.reply_text("🎉 You found a hidden egg! Something rare may hatch soon.")
    else:
        await update.message.reply_text("😔 No egg found... check again later.")

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 <b>Dragon Market</b>\n\n"
        "🚧 Market is under construction!\nSoon you’ll be able to:\n"
        "• Buy rare eggs\n"
        "• Purchase boosts\n"
        "• Trade dragon gear\n\n"
        "Stay tuned 👀",
        parse_mode="HTML"
    )

async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    user_data = users.get(user_id)

    if not user_data or not user_data.get("dragons"):
        await update.message.reply_text("❌ No dragons to rename.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /rename <dragon_number> <new_name>")
        return

    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(user_data["dragons"]):
            raise ValueError
        new_name = " ".join(context.args[1:])
    except ValueError:
        await update.message.reply_text("❌ Invalid dragon number.")
        return

    old_name = user_data["dragons"][index]["name"]
    user_data["dragons"][index]["name"] = new_name
    users[user_id] = user_data
    save_users(users)

    await update.message.reply_text(
        f"✍️ Renamed <b>{old_name}</b> to <b>{new_name}</b>!",
        parse_mode="HTML"
    )

async def cooldowns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    user_data = users.get(user_id, {})
    today = datetime.date.today()
    now = datetime.datetime.now()

    def days_ago(iso):
        if not iso: return "✅ Ready"
        dt = datetime.date.fromisoformat(iso)
        diff = (today - dt).days
        return f"⏳ {1 - diff}d left" if diff < 1 else "✅ Ready"

    def hours_ago(iso):
        if not iso: return "✅ Ready"
        try:
            dt = datetime.datetime.fromisoformat(iso)
            delta = (now - dt).total_seconds()
            return f"⏳ {int((3600 - delta) // 60)}m left" if delta < 3600 else "✅ Ready"
        except:
            return "✅ Ready"

    await update.message.reply_text(
        "<b>⏱️ Cooldown Status</b>\n\n"
        f"🍖 Feed: {days_ago(user_data.get('last_feed'))}\n"
        f"🏋️ Train: {days_ago(user_data.get('last_train'))}\n"
        f"🧬 Evolve: {days_ago(user_data.get('last_evolve'))}\n"
        f"💰 Earn: {days_ago(user_data.get('last_earn'))}",
        parse_mode="HTML"
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 Your Info:\n• ID: <code>{user.id}</code>\n• Name: <b>{user.full_name}</b>",
        parse_mode="HTML"
    )

async def fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fortunes = [
        "🐉 A mighty dragon will bless your path today.",
        "🔥 Great power lies ahead. Be ready.",
        "🌪️ The winds of change are coming for your dragons.",
        "🌑 Beware the shadows, tamer.",
        "✨ A hidden egg will soon reveal itself.",
        "💰 Riches await those who train well."
    ]
    await update.message.reply_text(f"🔮 <i>{random.choice(fortunes)}</i>", parse_mode="HTML")

from flask import Flask
from threading import Thread

app_web = Flask('')

@app_web.route('/')
def home():
    return "✅ Bot is alive!"

def run():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

async def bot_added_or_promoted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    new_member = update.my_chat_member.new_chat_member
    old_status = update.my_chat_member.old_chat_member.status
    new_status = new_member.status

    # Only act if bot was added or promoted
    if chat.type in ("group", "supergroup") and old_status in ["left", "kicked"] and new_status in ["member", "administrator"]:
        group_name = chat.title or "N/A"
        group_id = chat.id
        group_type = chat.type
        group_link = f"https://t.me/{chat.username}" if chat.username else "❌ Not Public"

        # Send log to LOG_GROUP
        try:
            await context.bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=(
                    f"📥 <b>#BOT_ADDED_TO_GROUP</b>\n\n"
                    f"📛 <b>Group:</b> {group_name}\n"
                    f"🆔 <b>ID:</b> <code>{group_id}</code>\n"
                    f"👥 <b>Type:</b> {group_type}\n"
                    f"🔗 <b>Link:</b> {group_link}"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            print("[LOG ERROR]", e)

        # Send welcome message to the group
        try:
            await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"🐉 <b>Thanks for adding <i>DragonDusk</i>!</b>\n\n"
                    f"⚠️ To unlock full features:\n"
                    f"• <b>Make me Admin</b>\n"
                    f"• Use <b>/rgroup</b> to register this group\n\n"
                    f"✨ Let the dragon legends begin! 🌌"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            print("[GROUP MESSAGE ERROR]", e)


from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import json

def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json("users.json")

    top_duskar = sorted(users.items(), key=lambda x: x[1].get("duskar", 0), reverse=True)[:5]
    top_gems = sorted(users.items(), key=lambda x: x[1].get("gems", 0), reverse=True)[:5]
    top_wins = sorted(users.items(), key=lambda x: x[1].get("wins", 0), reverse=True)[:5]

    def format_list(title, emoji, data, key):
        lines = [f"<b>{emoji} {title}</b>"]
        for i, (uid, user) in enumerate(data, 1):
            name = user.get("name", "Unknown")
            value = user.get(key, 0)
            lines.append(f"{i}. {name} — <b>{value}</b>")
        return "\n".join(lines)

    msg = "\n\n".join([
        format_list("Top Duskar Holders", "💰", top_duskar, "duskar"),
        format_list("Top Gem Collectors", "💎", top_gems, "gems"),
        format_list("Top Battle Winners", "⚔️", top_wins, "wins")
    ])

    await update.message.reply_text(msg, parse_mode="HTML")

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import json

# Replace with your actual owner ID
BOT_OWNER_ID = 6020886539

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

async def sendduskar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    if sender_id != BOT_OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    # Check if command is reply-based
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        user_id = str(target_user.id)
        mention = f"[{target_user.first_name}](tg://user?id={user_id})"
    elif len(context.args) >= 2:
        user_id = str(context.args[0])
        amount_text = context.args[1]
        mention = f"`{user_id}`"  # fallback if no username
    else:
        await update.message.reply_text("Usage:\n➡️ /sendduskar <user_id> <amount>\nOr reply to a user with: `/sendduskar <amount>`", parse_mode="Markdown")
        return

    # Parse amount
    try:
        amount = int(context.args[1]) if not update.message.reply_to_message else int(context.args[0])
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text("❌ Invalid Duskar amount.", parse_mode="Markdown")
        return

    # Load and update users
    users = load_users()
    if user_id not in users:
        users[user_id] = {"duskar": 0, "gems": 0, "wins": 0, "losses": 0}
    users[user_id]["duskar"] += amount
    save_users(users)

    # Aesthetic confirmation
    await update.message.reply_text(
        f"💸 *Duskar Transfer Successful!*\n\n"
        f"👑 Sent: *{amount} Duskar*\n"
        f"🎉 To: {mention}",
        parse_mode="Markdown"
    )

# === Run Bot ===
if __name__ == "__main__":
    keep_alive()  # 👈 Keep your Replit or host alive
    app = ApplicationBuilder().token(TOKEN).build()

    # 🌟 Main Commands
    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("inventory", inventory))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("hatch", hatch))
    app.add_handler(CommandHandler("id", myid))
    app.add_handler(CommandHandler("cooldowns", cooldowns))
    app.add_handler(CommandHandler("fortune", fortune))
    app.add_handler(CommandHandler("dailyegg", dailyegg))
    app.add_handler(CommandHandler("userstats", userstats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("challenge", challenge))
    app.add_handler(CommandHandler("work", work))
    app.add_handler(CommandHandler("mine", mine))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    # 🐉 Dragon Commands
    app.add_handler(CommandHandler("dragons", dragons))
    app.add_handler(CommandHandler("feed", feed))
    app.add_handler(CommandHandler("train", train))
    app.add_handler(CommandHandler("release", release))
    app.add_handler(CommandHandler("market", market))

    # 🥚 Egg Commands
    app.add_handler(CommandHandler("getegg", getegg))
    app.add_handler(CommandHandler("eggs", eggs))
    app.add_handler(CommandHandler("eghatch", eghatch))

    # 🧠 Inline Button Handlers
    app.add_handler(CallbackQueryHandler(select_dragon_callback, pattern="^selectdragon_"))
    app.add_handler(CallbackQueryHandler(handle_move, pattern="^move_"))
    app.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer(), pattern="^ignore$"))
    app.add_handler(MessageHandler(filters.Sticker.ALL, get_sticker_id))

    # 📖 Help Menu Callback


    # 📌 Group registration
    app.add_handler(CommandHandler("rgroup", registergroup))
    app.add_handler(CommandHandler("addmod", addmod))
    app.add_handler(CommandHandler("mods", mods))
    app.add_handler(CommandHandler("rmmod", rmmod))
    app.add_handler(CommandHandler("cancel", cancel_battle))

    # 🛡️ Clan Commands
    app.add_handler(CommandHandler("createclan", createclan))
    app.add_handler(CommandHandler("joinclan", joinclan))
    app.add_handler(CommandHandler("myclan", myclan))
    app.add_handler(CommandHandler("leaveclan", leaveclan))
    app.add_handler(CommandHandler("disband", disbandclan))
    app.add_handler(CommandHandler("clanchallenge", clanchallenge))
    app.add_handler(CallbackQueryHandler(accept_clanwar, pattern=r"^accept_clanwar\|"))
    app.add_handler(CommandHandler("sendusks", sendduskar))


    # 🤖 Bot Management
    app.add_handler(ChatMemberHandler(bot_added_or_promoted, ChatMemberHandler.MY_CHAT_MEMBER))

    print("🐉 Dragon is Cominggg...")
    app.run_polling()
