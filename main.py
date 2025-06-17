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
from step2 import getegg, eggs, eghatch, addmod, mods, rmmod, missions
from clan import createclan, joinclan, myclan, leaveclan, disbandclan, clanchallenge, accept_clanwar
from step2 import gift, send, drackstats
from travelexp import region, show_region_details, region_back, travel, whereami, explore, select_pve_dragon, pve_move_handler, pve_flee, pve_tame
from datetime import date
from telegram.ext import ChatMemberHandler
from telegram.constants import ParseMode
from minigames import minigames, handle_game_choice

# === CONFIG ===
TOKEN = "8040202761:AAF_HEGJxbZjKsgJANNQQRP4ahXftlMsqCQ"
LOG_GROUP_ID = -1002834714399
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
LOG_GROUP_ID = "-1002834714399"
SUPPORT_LINK = "https://t.me/Dragon_Realm"
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

    # Redirect to /help or /explore if passed via deep link
    if args:
        arg = args[0].lower()
        if arg == "help":
            await help_command(update, context)
            return
        elif arg == "explore":
            await explore(update, context)
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

    # Welcome Keyboard
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

    # Welcome Caption
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
        if update.message:
            await update.message.reply_text(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

HELP_IMAGE_URL = "https://graph.org/file/a2b0ac48d16bd00589b8f-2da15263ad3f26ab8e.jpg"  # Replace with your actual image URL

HELP_CATEGORIES = {
    "main": {
        "title": "🚀 *Main Commands*",
        "commands": [
            "🧭 `/start` — Begin your dragon journey",
            "📊 `/status` — Check your current status",
            "👤 `/profile` — View your profile",
            "🎒 `/inventory` — Show your items and dragons",
            "💰 `/balance` — Show Duskar & Gem",
            "🆔 `/id` — Show your Telegram ID",
            "⏳ `/cooldowns` — View active cooldowns",
            "🔮 `/fortune` — Reveal today's luck",
            "🎁 `/daily` — Claim daily Duskar",
            "🥚 `/dailyegg` — Claim daily egg",
            "🏆 `/leaderboard` — View top players",
            "📈 `/userstats` — Win rate and match stats",
            "📢 `/broadcast` — Send message to all users (Admin)"
        ]
    },
    "dragon": {
        "title": "🐉 *Dragon Commands*",
        "commands": [
            "📜 `/dragons` — Show all owned dragons",
            "🍗 `/feed` — Feed your dragons",
            "🏋️ `/train` — Train your dragons",
            "⚰️ `/release` — Release unwanted dragon",
            "🛒 `/market` — View dragon marketplace"
        ]
    },
    "battle": {
        "title": "⚔️ *Battle Commands*",
        "commands": [
            "🎯 `/challenge` — Challenge someone to a battle",
            "❌ `/cancel` — Cancel an ongoing challenge"
        ]
    },
    "egg": {
        "title": "🥚 *Egg Commands*",
        "commands": [
            "🥚 `/getegg` — Earn eggs",
            "📦 `/eggs` — View your eggs",
            "🐣 `/eghatch` — Hatch ready eggs",
            "🔀 `/hatch` — Hatch a dragon from egg"
        ]
    },
    "clan": {
        "title": "🛡️ *Clan Commands*",
        "commands": [
            "🏰 `/createclan` — Start a new clan",
            "👥 `/joinclan` — Join an existing clan",
            "🧙 `/myclan` — Info about your clan",
            "🚪 `/leaveclan` — Leave your clan",
            "💀 `/disband` — Disband your clan",
            "⚔️ `/clanchallenge` — Start clan war",
            "💸 `/sendusks` — Send Duskar to member"
        ]
    },
    "admin": {
        "title": "🧰 *Admin/Mod Commands*",
        "commands": [
            "➕ `/addmod` — Add a mod (reply/username)",
            "🧑‍⚖️ `/mods` — List all current mods",
            "➖ `/rmmod` — Remove a mod",
            "⛏️ `/mine` — Earn Duskar (Work style)",
            "🪓 `/work` — Simple job for Duskar",
            "🏟️ `/rgroup` — Register this group"
        ]
    }
}

# ========== /help ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🚀 Main", callback_data="help_main"),
            InlineKeyboardButton("🐉 Dragon", callback_data="help_dragon"),
            InlineKeyboardButton("⚔️ Battle", callback_data="help_battle")
        ],
        [
            InlineKeyboardButton("🥚 Eggs", callback_data="help_egg"),
            InlineKeyboardButton("🛡️ Clan", callback_data="help_clan"),
            InlineKeyboardButton("🧰 Admin", callback_data="help_admin")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=HELP_IMAGE_URL,
        caption="`🧙‍♂️ Welcome to Dragon Dusk Help Menu!`\n\n*Choose a category below to view commands:*",
        parse_mode="MarkdownV2",
        reply_markup=reply_markup
    )

# ========== Callback ==========
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category = query.data.replace("help_", "")
    help_data = HELP_CATEGORIES.get(category)

    if help_data:
        text = f"{help_data['title']}\n\n" + "\n".join(help_data["commands"])
        text += "\n\n➤ _Tap a button below to view other sections_"

        keyboard = [
            [
                InlineKeyboardButton("🚀 Main", callback_data="help_main"),
                InlineKeyboardButton("🐉 Dragon", callback_data="help_dragon"),
                InlineKeyboardButton("⚔️ Battle", callback_data="help_battle")
            ],
            [
                InlineKeyboardButton("🥚 Eggs", callback_data="help_egg"),
                InlineKeyboardButton("🛡️ Clan", callback_data="help_clan"),
                InlineKeyboardButton("🧰 Admin", callback_data="help_admin")
            ]
        ]
        await query.edit_message_caption(
            caption=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

from telegram import Update
from telegram.ext import ContextTypes

GUIDE_LINK = "https://t.me/Nexxxxxo_bots/5"  # Replace with your actual message link

async def guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📖 **DragonDusk Beginner’s Guide**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🧭 Step-by-step instructions to dominate the realm!\n\n"
        f"👉 [Click here to open the official guide]({GUIDE_LINK})\n\n"
        f"🔥 _Train. Hatch. Battle. Rule._",
        parse_mode="Markdown", disable_web_page_preview=False
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
    
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

# === CONFIG ===
BOT_OWNER_ID = 6020886539
BOT_VERSION = "1.0.0"
IMAGE_URL = "https://graph.org/file/a2b0ac48d16bd00589b8f-2da15263ad3f26ab8e.jpg"
START_TIME = datetime.utcnow()

# === Utilities ===
def get_uptime():
    now = datetime.utcnow()
    delta = now - START_TIME
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

def load_mods():
    try:
        with open("mod.json", "r") as f:
            return json.load(f)
    except:
        return {}

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def load_group_data():
    try:
        with open("group.json", "r") as f:
            return json.load(f)
    except:
        return {}

def is_admin(user_id):
    user_id = str(user_id)
    return str(user_id) == str(BOT_OWNER_ID) or user_id in load_mods()

# === Command ===
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("🚫 *Access Denied!*\nThis command is for the owner or mods only.", parse_mode="Markdown")
        return

    users = load_users()
    group_data = load_group_data()
    uptime = get_uptime()

    total_users = len(users)
    total_duskar = sum(u.get("duskar", 0) for u in users.values())
    started_users = sum(1 for u in users.values() if u.get("dragons") and len(u["dragons"]) > 0)
    started_chats = len(group_data)

    bot_username = context.bot.username
    group_info = group_data.get(str(update.effective_chat.id))

    group_stats = (
        "\n\n<b>📍 Group Stats</b>\n"
        "🔸 <i>Not Registered</i>\n"
        "📌 Use <code>/rgroup</code> to register."
    ) if not group_info else (
        f"\n\n<b>📍 Group Stats</b>\n"
        f"🏷️ <b>Name:</b> {group_info['title']}\n"
        f"🐣 <b>Hatched Dragons:</b> {group_info['hatched_count']}"
    )

    status_text = (
        f"⚙️ <b>DragonDusk – Bot Status</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Bot:</b> @{bot_username}\n"
        f"🕒 <b>Uptime:</b> {uptime}\n"
        f"🌍 <b>Version:</b> {BOT_VERSION}\n"
        f"👑 <b>Owner:</b> REDEX\n\n"
        f"📊 <b>Global Stats</b>\n"
        f"👥 Users: <b>{total_users}</b>\n"
        f"🐉 Dragons Hatched: <b>{started_users}</b>\n"
        f"💰 Duskar Distributed: <b>{total_duskar}</b>\n"
        f"💬 Registered Groups: <b>{started_chats}</b>"
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
from telegram import InputMediaPhoto

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.get(user_id, {})

    name = user.get("name", update.effective_user.first_name)
    duskar = user.get("duskar", 0)
    gems = user.get("gems", 0)
    wins = user.get("wins", 0)
    losses = user.get("losses", 0)
    xp = user.get("xp", 0)
    level = user.get("level", 1)
    explore_count = user.get("explore_count", 0)
    tamed_dragons = len(user.get("dragons", []))

    total = wins + losses
    win_percent = round((wins / total) * 100, 2) if total > 0 else 0.0

    next_level_xp = level * 1000
    xp_bar = int((xp / next_level_xp) * 10)
    xp_bar_str = "█" * xp_bar + "░" * (10 - xp_bar)

    text = f"""
<b>╭━━━━━━━◆༻👤༺◆━━━━━━━╮
┃   {name}'s Dragon Profile
╰━━━━━━━◆༻💠༺◆━━━━━━━╯</b>

💰 <b>Duskar:</b> {duskar}   💎 <b>Gems:</b> {gems}

🎮 <b>Battle Stats</b>
• ✅ Wins: <b>{wins}</b>  ❌ Losses: <b>{losses}</b>
• 📈 Win Rate: <b>{win_percent}%</b>

🧭 <b>Exploration</b>
• 🌍 Regions Explored: <b>{explore_count}</b>
• 🐉 Dragons Tamed: <b>{tamed_dragons}</b>

🧠 <b>XP:</b> {xp_bar_str} <code>{xp}/{next_level_xp}</code>
🔼 <b>Level:</b> {level}

🌟 <i>Keep battling and exploring to become a legend!</i>
"""

    try:
        photos = await context.bot.get_user_profile_photos(update.effective_user.id, limit=1)
        if photos.total_count > 0:
            await update.message.reply_photo(
                photo=photos.photos[0][-1].file_id,
                caption=text,
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(text, parse_mode="HTML")
    except Exception as e:
        print(f"[PROFILE ERROR] {e}")
        await update.message.reply_text(text, parse_mode="HTML")


async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        user_data = load_users().get(user_id)

        if not user_data:
            await update.message.reply_text("❌ You are not registered yet. Use /start to begin.")
            return

        dragons = user_data.get("dragons", [])
        potions = user_data.get("potions", {})  # Example: { "1": 2, "2": 1 }

        # Dragon List
        if dragons:
            dragon_list = "\n".join(
                [f"{i+1}. 🐉 <b>{dragon['name']}</b>  •  Level <b>{dragon.get('level', 1)}</b>"
                 for i, dragon in enumerate(dragons)]
            )
        else:
            dragon_list = "🐣 You don't own any dragons yet."

        # Potion List
        potion_names = {
            "1": "Small Potion (20 HP)",
            "2": "Medium Potion (50 HP)",
            "3": "Large Potion (100 HP)"
        }

        if potions:
            potion_list = "\n".join(
                [f"🧪 <b>{potion_names.get(pid, 'Unknown')}</b> x{qty}" for pid, qty in potions.items()]
            )
        else:
            potion_list = "🧪 You don't have any potions."

        # Final Caption
        caption = f"""
    ╔═༻📦 Your Dragon Inventory ༺═╗

    🐉 <b>Dragons:</b>
    {dragon_list}

    🧪 <b>Potions:</b>
    {potion_list}

    ✨ May your collection grow ever stronger!
    """

        await update.message.reply_photo(
            photo="AgACAgUAAxkBAAIJeGhONCr1-YxoF8JUP2HQoRhA3BD0AAL-yjEbZEN5VgrrkGSOQuB0AQADAgADeQADNgQ",  # Replace if needed
            caption=caption,
            parse_mode="HTML"
        )



async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        users = load_json("users.json")
        user = users.get(user_id, {})

        duskar = user.get("duskar", 0)
        gems = user.get("gems", 0)

        text = f"""
    ╭━━━💰 <b>Your Balance</b> 💎━━━╮
    ┃ 
    ┃ 🪙 <b>Duskar:</b> {duskar}
    ┃ 💎 <b>Gems:</b> {gems}
    ┃ 
    ╰━━━━━━━━━━━━━━━━━━━━╯
    """
        await update.message.reply_text(text, parse_mode="HTML")

import json

def load_dragons():
    with open("dragons.json", "r") as f:
        return json.load(f)
# assuming this loads your JSONs

async def dragons(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        user_data = load_users().get(user_id)
        if not user_data:
            await update.message.reply_text("❌ You are not registered. Use /start first.")
            return

        dragons_owned = user_data.get("dragons", [])
        if not dragons_owned:
            await update.message.reply_text("🐣 You don't have any dragons yet. Use /hatch to summon one!")
            return

        all_dragons = load_dragons()  # your full dataset
        type_emojis = {
            "Fire": "🔥", "Water": "💧", "Earth": "🌱", "Air": "🌪️", "Ice": "❄️",
            "Electric": "⚡", "Dark": "🌑", "Light": "🌟", "Metal": "⚙️", "Dragon": "🐉",
            "Poison": "☠️", "Shadow": "🕶️"
        }

        msg = "🐲 <b>Your Dragon Collection</b>\n\n"
        for i, dragon_entry in enumerate(dragons_owned, 1):
            # Handle both dicts and string-only entries
            if isinstance(dragon_entry, dict):
                name = dragon_entry.get("name")
                level = dragon_entry.get("level", 1)
                power = dragon_entry.get("power", 0)
            else:
                name = dragon_entry
                level = 1
                power = 0

            data = all_dragons.get(name, {})
            element = data.get("element", "Unknown")
            emoji = type_emojis.get(element, "🐉")

            msg += (
                f"🔹 <b>{i}. {emoji} {name}</b>\n"
                f"   ├ 🧪 <b>Type:</b> {element}\n"
                f"   ├ 🎚️ <b>Level:</b> {level}\n"
                f"   └ ⚔️ <b>Power:</b> {power}\n\n"
            )

        await update.message.reply_text(msg, parse_mode="HTML")



import random
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes

BASE_FEED_COST = 100
BASE_TRAIN_COST = 250

def level_up_dragon(dragon):
        # Increase level
        dragon["level"] = dragon.get("level", 1) + 1

        # Boost moves power and collect descriptions
        attack_boost = []
        for move in dragon.get("moves", []):
            boost = random.randint(2, 5)
            move["power"] = move.get("power", 0) + boost
            attack_boost.append(f"{move['name']} (+{boost})")

        # Increase dragon power (at least keep old power, or add boost)
        old_power = dragon.get("power", 30)
        power_boost = random.randint(5, 15)
        dragon["power"] = old_power + power_boost

        # Increase current HP by 10–20 (initialize if missing)
        old_hp = dragon.get("current_hp", dragon.get("base_hp", 100))
        hp_boost = random.randint(10, 20)
        dragon["current_hp"] = old_hp + hp_boost

        return attack_boost


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

    today_str = date.today().isoformat()

    # Reset or increment feed count
    if user_data.get("last_feed_date") == today_str:
        user_data["feed_count_today"] = user_data.get("feed_count_today", 0) + 1
    else:
        user_data["feed_count_today"] = 1
    user_data["last_feed_date"] = today_str

    feed_count = user_data["feed_count_today"]
    cost = BASE_FEED_COST * feed_count

    if user_data.get("duskar", 0) < cost:
        await update.message.reply_text(f"💸 You need at least {cost} Duskar to feed a dragon now (feed count today: {feed_count}).")
        return

    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(dragons):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid dragon number.")
        return

    dragon = dragons[index]
    added_power = random.randint(1, 5)
    dragon["power"] = dragon.get("power", 0) + added_power

    msg = (
        f"🍖 You fed <b>{dragon['name']}</b>!\n"
        f"⚡ Power increased by <b>{added_power}</b>.\n"
        f"💰 {cost} Duskar spent | 🔋 Power: <b>{dragon['power']}</b>\n"
        f"🛠️ Feed count today: {feed_count}"
    )

    # Check level-up
    if dragon["power"] >= 95:
        attack_boost = level_up_dragon(dragon)
        msg += f"\n\n🔼 <b>{dragon['name']}</b> leveled up to Level {dragon['level']}!"
        msg += "\n⚔️ Attack moves improved:\n• " + "\n• ".join(attack_boost)

    user_data["duskar"] -= cost
    user_data["dragons"] = dragons
    users[user_id] = user_data
    save_users(users)

    await update.message.reply_text(msg, parse_mode="HTML")

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

    today_str = date.today().isoformat()

    # Reset or increment train count
    if user_data.get("last_train_date") == today_str:
        user_data["train_count_today"] = user_data.get("train_count_today", 0) + 1
    else:
        user_data["train_count_today"] = 1
    user_data["last_train_date"] = today_str

    train_count = user_data["train_count_today"]
    cost = BASE_TRAIN_COST * train_count

    if user_data.get("duskar", 0) < cost:
        await update.message.reply_text(f"💸 You need at least {cost} Duskar to train a dragon now (train count today: {train_count}).")
        return

    try:
        index = int(context.args[0]) - 1
        if index < 0 or index >= len(dragons):
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Invalid dragon number.")
        return

    dragon = dragons[index]
    power_gain = random.randint(5, 8)
    dragon["power"] = dragon.get("power", 0) + power_gain

    # Boost attack moves by 1-3 for normal training
    attack_boost = []
    for move in dragon.get("moves", []):
        boost = random.randint(1, 3)
        move["power"] += boost
        attack_boost.append(f"{move['name']} (+{boost})")

    msg = (
        f"🏋️ Training complete for <b>{dragon['name']}</b>!\n"
        f"🔋 Power increased by <b>{power_gain}</b>\n"
        f"⚔️ Attack moves improved:\n• " + "\n• ".join(attack_boost) + "\n"
        f"💰 {cost} Duskar spent\n"
        f"🛠️ Train count today: {train_count}"
    )

    # Check for level up if power >= 95
    if dragon["power"] >= 95:
        level_boost = level_up_dragon(dragon)
        msg += f"\n\n🔼 <b>{dragon['name']}</b> leveled up to Level {dragon['level']}!"
        msg += "\n⚔️ Additional attack moves improved:\n• " + "\n• ".join(level_boost)

    user_data["duskar"] -= cost
    user_data["dragons"] = dragons
    users[user_id] = user_data
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

        # Safe refund calculation
        level = dragon.get("level", 1)
        power = dragon.get("power")
        if power is None:
            power = 100  # So power//10 = 10 duskar if power missing
        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 1
        try:
            power = int(power)
        except (TypeError, ValueError):
            power = 100

        refund = level * 10 + power // 10

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
from datetime import datetime, timedelta


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

    earned = 80  # Fixed Duskar amount
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

        cooldown = timedelta(minutes=90)
        now = datetime.now()

        last_mine_str = user.get("last_mine")
        mine_date = user.get("mine_date")
        mine_count = user.get("mine_count", 0)

        # Reset mine_count if date changed
        today_str = now.date().isoformat()
        if mine_date != today_str:
            mine_count = 0
            user["mine_date"] = today_str
            user["mine_count"] = 0

        # Check if max 3 shifts reached
        if mine_count >= 3:
            await update.message.reply_text("⛏️ You’ve already completed 3 mining shifts today. Try again tomorrow!")
            return

        # Cooldown check
        if last_mine_str:
            last_mine = datetime.fromisoformat(last_mine_str)
            if now - last_mine < cooldown:
                next_time = last_mine + cooldown
                minutes = int((next_time - now).total_seconds() // 60)
                await update.message.reply_text(f"⏳ You’re tired! Try mining again in {minutes} min.")
                return

        # Successful mining
        earned = random.randint(40, 100)
        user["duskar"] = user.get("duskar", 0) + earned
        user["last_mine"] = now.isoformat()
        user["mine_count"] = mine_count + 1
        save_json("users.json", users)

        await update.message.reply_text(
            f"⛏️ You mined some rare crystals and earned <b>{earned} Duskar</b>!\n"
            f"💰 Total Duskar: <b>{user['duskar']}</b>\n"
            f"📦 Mining shifts used today: <b>{user['mine_count']}/3</b>",
            parse_mode="HTML"
        )


from datetime import datetime

from datetime import datetime

CHANNEL_USERNAME = "@Nexxxxxo_bots"  # 🔁 Replace with your actual channel username

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.setdefault(user_id, {})

    # Check channel membership
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ("member", "creator", "administrator"):
            raise ValueError("Not a member")
    except:
        await update.message.reply_text(
            f"🔒 To claim your daily reward, join our official channel: {CHANNEL_USERNAME}\n"
            f"Then try again with /daily.",
            parse_mode="HTML"
        )
        return

    # Check daily cooldown
    last_daily = user.get("last_daily")
    today = datetime.now().date()

    if last_daily and datetime.fromisoformat(last_daily).date() == today:
        await update.message.reply_text("📅 You've already claimed your daily reward today. Come back tomorrow!")
        return

    # Reward
    user["duskar"] = user.get("duskar", 0) + 50
    user["gems"] = user.get("gems", 0) + 2
    user["last_daily"] = datetime.now().isoformat()
    save_json("users.json", users)

    await update.message.reply_text(
        f"🎁 You received your daily reward!\n\n"
        f"💰 <b>+50 Duskar</b>\n💎 <b>+2 Gems</b>\n\n"
        f"Thanks for being part of our community!",
        parse_mode="HTML"
    )

from datetime import datetime

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

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

# === MARKET COMMAND ===
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
╔═══🛒 <b>Dragon Market</b> ═══╗

✨ <i>Welcome, brave tamer! Stock up for your next battle.</i>

🧪 <b>Potions – Restore Dragon HP</b>
━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ <b>Small Potion</b> – 🩸 Heals 20 HP  
💰 <i>Cost:</i> 300 Duskar  |  <code>ID: 1</code>

2️⃣ <b>Medium Potion</b> – 🩸 Heals 50 HP  
💰 <i>Cost:</i> 800 Duskar  |  <code>ID: 2</code>

3️⃣ <b>Large Potion</b> – 🩸 Heals 100 HP  
💰 <i>Cost:</i> 1200 Duskar  |  <code>ID: 3</code>
━━━━━━━━━━━━━━━━━━━━━━━

🛍️ <b>To purchase:</b> <code>/buy &lt;item_id&gt;</code>  
<i>Example:</i> <code>/buy 2</code>

🔮 <i>More magical items arriving soon...</i>
╚═══════════════════════════╝
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1️⃣ Buy Small Potion", callback_data="buy_1"),
            InlineKeyboardButton("2️⃣ Buy Medium Potion", callback_data="buy_2"),
        ],
        [
            InlineKeyboardButton("3️⃣ Buy Large Potion", callback_data="buy_3"),
        ]
    ])

    await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# === CALLBACK HANDLER FOR BUTTONS ===
async def buy_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    item_id = int(query.data.split("_")[1])
    user_id = str(query.from_user.id)

    await query.message.reply_text(
        f"🛒 You selected to buy item ID: <b>{item_id}</b>\n"
        f"💡 Use <code>/buy {item_id}</code> to confirm your purchase.",
        parse_mode="HTML"
    )

ITEMS = {
    1: {"name": "Small Potion", "heal": 20, "price": 300},
    2: {"name": "Medium Potion", "heal": 50, "price": 800},
    3: {"name": "Large Potion", "heal": 100, "price": 1200},
}

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json("users.json")
    user = users.get(user_id)

    if not user:
        await update.message.reply_text("❌ You are not registered yet. Use /start to begin.")
        return

    if len(context.args) != 1 or context.args[0] not in ["1", "2", "3"]:
        await update.message.reply_text("❌ Usage: /buy <item_id>\nAvailable: 1 (Small), 2 (Medium), 3 (Large)")
        return

    item_id = context.args[0]
    prices = {"1": 300, "2": 800, "3": 1200}
    names = {"1": "Small Potion", "2": "Medium Potion", "3": "Large Potion"}
    cost = prices[item_id]

    if user.get("duskar", 0) < cost:
        await update.message.reply_text("❌ Not enough Duskar.")
        return

    user["duskar"] -= cost

    # ✅ Ensure potions field exists
    if "potions" not in user:
        user["potions"] = {"1": 0, "2": 0, "3": 0}

    user["potions"][item_id] += 1
    users[user_id] = user
    save_json("users.json", users)

    await update.message.reply_text(
        f"✅ Purchased <b>{names[item_id]}</b> for {cost} Duskar.",
        parse_mode="HTML"
    )
users = load_json("users.json")

for uid, user in users.items():
    if "potions" not in user:
        user["potions"] = {"1": 0, "2": 0, "3": 0}

save_json("users.json", users)


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

        top_duskar = sorted(users.items(), key=lambda x: x[1].get("duskar", 0), reverse=True)[:3]
        top_gems = sorted(users.items(), key=lambda x: x[1].get("gems", 0), reverse=True)[:3]
        top_wins = sorted(users.items(), key=lambda x: x[1].get("wins", 0), reverse=True)[:3]
        top_tames = sorted(users.items(), key=lambda x: len(x[1].get("dragons", [])), reverse=True)[:3]
        top_explores = sorted(users.items(), key=lambda x: x[1].get("explore_count", 0), reverse=True)[:3]

        def format_list(title, emoji, data, key_fn):
            lines = [f"<b>{emoji} {title}</b>\n"]
            for i, (uid, user) in enumerate(data, 1):
                name = user.get("name", "Unknown")
                value = key_fn(user)
                medal = ["🥇", "🥈", "🥉"][i - 1]
                lines.append(f"{medal} <b>{name}</b> — {value}")
            return "\n".join(lines)

        msg = (
            "<u><b>🏆 DragonDusk Leaderboard</b></u>\n"
            "🔥 Only the strongest make it to the top!\n\n" +

            format_list("Top Duskar Holders", "💰", top_duskar, lambda u: u.get("duskar", 0)) + "\n\n" +
            format_list("Top Gem Collectors", "💎", top_gems, lambda u: u.get("gems", 0)) + "\n\n" +
            format_list("Top Battle Winners", "⚔️", top_wins, lambda u: u.get("wins", 0)) + "\n\n" +
            format_list("Most Dragons Tamed", "🐉", top_tames, lambda u: len(u.get("dragons", []))) + "\n\n" +
            format_list("Most Explores", "🧭", top_explores, lambda u: u.get("explore_count", 0))
        )

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

async def sendgems(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_text("Usage:\n➡️ /sendgems <user_id> <amount>\nOr reply to a user with: `/sendgems <amount>`", parse_mode="Markdown")
            return

        # Parse amount
        try:
            amount = int(context.args[1]) if not update.message.reply_to_message else int(context.args[0])
            if amount <= 0:
                raise ValueError
        except:
            await update.message.reply_text("❌ Invalid Gems amount.", parse_mode="Markdown")
            return

        # Load and update users
        users = load_users()
        if user_id not in users:
            users[user_id] = {"duskar": 0, "gems": 0, "wins": 0, "losses": 0}
        users[user_id]["gems"] += amount
        save_users(users)

        # Aesthetic confirmation
        await update.message.reply_text(
            f"💸 *gems Transfer Successful!*\n\n"
            f"👑 Sent: *{amount} gems*\n"
            f"🎉 To: {mention}",
            parse_mode="Markdown"
        )





from datetime import datetime
import json
from telegram import Update
from telegram.ext import ContextTypes

# === CONFIG ===
LOG_GROUP_ID = -1002834714399  # Your actual log group ID
GROUP_LINK = "https://t.me/Dragon_Realm"
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

async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_id = str(user.id)
    week = datetime.utcnow().strftime("%Y-%U")
    data = load_tasks()
    count = data.get(user_id, {}).get(week, 0)

    await update.message.reply_text(
        f"📊 *Weekly Message Challenge*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Name: `{user.first_name}`\n"
        f"🗓️ Week: `{week}`\n"
        f"💬 Tracked Messages: `{count}/2500`\n"
        f"🏆 Reward on 2500:\n"
        f"  ├ 💰 *500 Duskar*\n"
        f"  ├ 💎 *Gems* (chance)\n"
        f"  └ 🥚 *Rare Egg* (low chance)\n\n"
        f"📝 Only messages in [Log Group]({GROUP_LINK}) are counted!",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != LOG_GROUP_ID:
        return

    user_id = str(update.effective_user.id)
    week = datetime.utcnow().strftime("%Y-%U")
    data = load_tasks()

    if user_id not in data:
        data[user_id] = {}
    if week not in data[user_id]:
        data[user_id][week] = 0

    data[user_id][week] += 1
    save_tasks(data)

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text(f"File ID: {update.message.photo[-1].file_id}")


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


WELCOME_IMAGE = "AgACAgUAAxkBAAIJbGhOMnHkJWB3ON9pycZ49SBnRUDXAAL8yjEbZEN5VrSoxWjQ5f5oAQADAgADeQADNgQ"  # 🔁 Replace with your custom image

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not update.message or not update.message.new_chat_members:
        return

    if chat.id != LOG_GROUP_ID:
        return

    bot_username = (await context.bot.get_me()).username
    guide_url = "https://t.me/Nexxxxxo_bots"

    for member in update.message.new_chat_members:
        if member.is_bot:
            continue

        welcome_msg = f"""
╭━━━━━━━◆༻🐉༺◆━━━━━━━╮
🔥 Welcome, [{member.full_name}](tg://user?id={member.id})! 🔥
╰━━━━━━━◆༻🌑༺◆━━━━━━━╯

🌟 *The world of DragonDusk awaits...*
🛡️ Train mighty dragons  
🥚 Hatch legendary eggs  
⚔️ Battle for glory

💎 Type /start and let your legacy begin  
🔮 May the dusk guide your path...
"""

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌱 Begin Journey", callback_data="help_main")],
            [InlineKeyboardButton("📘 View Guide", url=guide_url)],
            [InlineKeyboardButton("🆘 Support", url="https://t.me/Nexxxxxo_bots")]
        ])

        try:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=WELCOME_IMAGE,
                caption=welcome_msg,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"[WELCOME ERROR] {e}")

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📥 Message received:", update.message.text)
    await update.message.reply_text("✅ Bot received your message.")

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from html import escape

DRAGONS_PER_PAGE = 10
DRAGONS_JSON_PATH = "dragons.json"

def load_json(path):
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def rarity_stars(rarity):
    stars_map = {
        "Common": "★☆☆☆☆",
        "Uncommon": "★★☆☆☆",
        "Rare": "★★★☆☆",
        "Epic": "★★★★☆",
        "Legendary": "★★★★★"
    }
    return stars_map.get(rarity, escape(rarity))

def build_dragons_page(dragons, page):
    start = page * DRAGONS_PER_PAGE
    end = start + DRAGONS_PER_PAGE
    page_dragons = dragons[start:end]

    lines = []
    for i, (name, data) in enumerate(page_dragons, start=start + 1):
        element = escape(data.get("element", "Unknown"))
        rarity = data.get("rarity", "Common")
        stars = rarity_stars(rarity)

        lines.append(
            f"<b>{i}.</b> 🐲 <b>{escape(name)}</b>\n"
            f" • Element: <i>{element}</i>\n"
            f" • Rarity: {stars}\n"
        )

    total_pages = (len(dragons) - 1) // DRAGONS_PER_PAGE + 1
    header = (
        "╔════════════════════════════╗\n"
        f"     🐉 <b>Dragon List — Page {page + 1}/{total_pages}</b> 🐉\n"
        "╚════════════════════════════╝\n\n"
    )

    footer = f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    text = header + "\n".join(lines) + footer

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"dragons_page_{page - 1}"))
    if end < len(dragons):
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"dragons_page_{page + 1}"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
    return text, reply_markup

async def dragonslist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dragons = list(load_json(DRAGONS_JSON_PATH).items())
    page = 0  # First page
    text, keyboard = build_dragons_page(dragons, page)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def dragonslist_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("dragons_page_"):
        return

    page = int(data.split("_")[-1])
    dragons = list(load_json(DRAGONS_JSON_PATH).items())
    text, keyboard = build_dragons_page(dragons, page)

    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=keyboard)

async def dragonsinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "❌ Usage: /dragonsinfo <dragon_id>\nGet full stats of a dragon by its ID from the list."
        )
        return

    dragon_id = int(context.args[0]) - 1
    dragons = list(load_json(DRAGONS_JSON_PATH).items())

    if dragon_id < 0 or dragon_id >= len(dragons):
        await update.message.reply_text("❌ Invalid dragon ID.")
        return

    name, data = dragons[dragon_id]

    element = escape(data.get("element", "Unknown"))
    base_hp = data.get("base_hp", "?")
    rarity = data.get("rarity", "Common")
    moves = data.get("moves", [])

    # Build moveset text with styling
    move_lines = []
    for move in moves:
        emoji = "💥" if move["type"] == "physical" else "🌪️"
        move_lines.append(
            f"┊ {emoji} <b>{escape(move['name'])}</b>\n"
            f"┊    🌀 <i>{escape(move['type'].capitalize())}</i> | 🔋 <b>{move['power']}</b>"
        )

    msg = (
        "╔════════════════════╗\n"
        f"    🐲 <b>Dragon #{dragon_id + 1} — Full Stats</b>\n"
        "╚════════════════════╝\n\n"
        f"🏷️ <b>Name:</b> {escape(name)}\n"
        f"🌈 <b>Element:</b> {element}\n"
        f"⭐ <b>Rarity:</b> {rarity_stars(rarity)}\n"
        f"❤️ <b>Base HP:</b> {base_hp}\n\n"
        "📜 <b>Moveset:</b>\n" + "\n".join(move_lines)
    )

    await update.message.reply_text(msg, parse_mode="HTML")

# Add handlers in your bot setup:
# app.add_handler(CommandHandler("dragonslist", dragonslist))
# app.add_handler(CallbackQueryHandler(dragonslist_callback, pattern=r"^dragons_page_\d+$"))
# app.add_handler(CommandHandler("dragonsinfo", dragonsinfo))


import json
from collections import defaultdict
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ChatMemberHandler, ContextTypes, CallbackContext, filters
)
from keep_alive import keep_alive  # For Replit Uptime


SECOND_LOG_GROUP_ID = -1002689253330  # Replace with your log group ID

# === Globals for Tracking ===
COMMAND_USAGE = defaultdict(int)
BOT_START_TIME = datetime.now()

# === Helper: Get Mod IDs ===
def get_mod_ids():
    try:
        with open("mod.json", "r") as f:
            mod_data = json.load(f)
        return [mod["id"] for mod in mod_data]
    except Exception:
        return []

# === Command Logger ===
async def command_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        command = update.message.text.strip().split()[0]
        if command.startswith("/"):
            COMMAND_USAGE[command] += 1

            # Log to group
            user = update.effective_user
            chat_type = update.message.chat.type
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_text = (
                f"📥 <b>Command Used</b>\n"
                f"👤 <b>User:</b> {user.full_name} (ID: <code>{user.id}</code>)\n"
                f"💬 <b>Command:</b> <code>{command}</code>\n"
                f"🗂 <b>Chat Type:</b> {chat_type}\n"
                f"🕒 <b>Time:</b> {timestamp}"
            )
            try:
                await context.bot.send_message(
                    chat_id=SECOND_LOG_GROUP_ID,
                    text=log_text,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Logging failed: {e}")

# === Command Usage Stats ===
async def command_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in get_mod_ids():
        return  # silently ignore if not mod

    now = datetime.now()
    uptime = now - BOT_START_TIME
    total_seconds = uptime.total_seconds()
    total_minutes = total_seconds / 60

    total_commands = sum(COMMAND_USAGE.values())
    per_min = round(total_commands / total_minutes, 2) if total_minutes > 0 else 0
    per_sec = round(total_commands / total_seconds, 2) if total_seconds > 0 else 0

    top_commands = sorted(COMMAND_USAGE.items(), key=lambda x: x[1], reverse=True)[:5]
    top_text = "\n".join([f"🔹 <b>{cmd}</b>: <code>{count}</code>" for cmd, count in top_commands]) or "None used yet."

    msg = (
        "📊 <b>Bot Command Analytics</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ <b>Uptime:</b> <code>{str(uptime).split('.')[0]}</code>\n"
        f"📨 <b>Total Commands:</b> <code>{total_commands}</code>\n"
        f"📈 <b>Rate:</b> <code>{per_min}</code>/min | <code>{per_sec}</code>/sec\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 <b>Top Commands:</b>\n" + top_text
    )

    await update.message.reply_text(msg, parse_mode="HTML")

 # Make sure only you can use it
# Replace with your actual Telegram user ID
OWNER_ID = 6020886539

import json

def load_dragons():
    with open("dragons.json", "r") as f:
        return json.load(f)


async def giftdrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user

    # ✅ Owner check
    if sender.id != OWNER_ID:
        return await update.message.reply_text("❌ You are not authorized to use this command.")

    # ✅ Reply check
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Please reply to the user you want to gift the dragon to.")

    # ✅ Dragon name check
    if len(context.args) == 0:
        return await update.message.reply_text("🐉 Please provide a dragon name.\nUsage: /giftdrack <DragonName>")

    dragon_name = " ".join(context.args).strip()
    receiver = update.message.reply_to_message.from_user
    receiver_id = str(receiver.id)

    # ✅ Load user data
    users = load_users()
    dragons_data = load_dragons()  # This should return your dragons.json content as a dict

    # ✅ Check if dragon exists
    dragon = dragons_data.get(dragon_name)
    if not dragon:
        return await update.message.reply_text(f"❌ Dragon named '{dragon_name}' not found in database.")

    # ✅ Format new dragon object
    new_dragon = {
        "name": dragon_name,
        "element": dragon["element"],
        "level": 1,
        "xp": 0,
        "power": max(move["power"] for move in dragon["moves"]),
        "base_hp": dragon["base_hp"]
    }

    users.setdefault(receiver_id, {}).setdefault("dragons", []).append(new_dragon)
    save_users(users)

    # ✅ Special message if it’s Elementis Infinitum
    if dragon_name.lower() == "elementis infinitum":
        return await update.message.reply_html(
            f"""
🌌✨ <b>𝐋𝐄𝐆𝐄𝐍𝐃 𝐁𝐎𝐑𝐍</b> ✨🌌

⚡ The skies shatter. The cosmos trembles.

🧝‍♂️ <b>{receiver.first_name}</b> now wields the Ultimate Dragon —  
🐉 <b>Elementis Infinitum</b> — The Cosmic Sovereign!

🔥 <b>250 HP</b> • 💥 <b>Over 120 Power</b> • 🌠 <i>Legend Awakened.</i>
"""
        )

    # ✅ Default gift message
    await update.message.reply_html(
        f"""
🎁✨ <b>𝐃𝐑𝐀𝐂𝐎𝐍𝐈𝐂 𝐆𝐈𝐅𝐓 𝐔𝐍𝐋𝐎𝐂𝐊𝐄𝐃!</b> ✨🎁

🌌 <i>A ripple trembles through the skies...</i>

👑 <b>{sender.first_name}</b> has gifted a dragon —  
🐉 <b>{dragon_name}</b>  
to 🧝‍♂️ <b>{receiver.first_name}</b>!

💫 The stars align as destiny unfolds...
"""
    )

from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram import Update

BOT_OWNER_ID = 6020886539  # Replace with your Telegram user ID



async def dragon_master_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = update.chat_member
        user = member.new_chat_member.user

        if user.id != BOT_OWNER_ID:
            return  # Ignore non-owner joins

        chat = update.effective_chat
        caption = f"""
🔥🐉 <b>⟪ DRAGON MASTER HAS ARRIVED ⟫</b> 🐉🔥

🌪️ The skies roar… the flames rise...
⚡ <b>The one who commands dragons has entered the realm.</b>

👑 <b>{user.full_name}</b> has joined this battlefield!
━━━━━━━━━━━━━━━━━━━━━━━
⚔️ <i>Let the legend continue...</i>
"""

        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=photos.photos[0][-1].file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )
        else:
            await context.bot.send_message(
                chat_id=chat.id,
                text=caption,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        print(f"[ERROR] dragon_master_joined: {e}")
        
import asyncio
from telegram.error import NetworkError
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ChatMemberHandler, filters
)
from keep_alive import keep_alive

# === Bot Token ===
TOKEN = "8040202761:AAF_HEGJxbZjKsgJANNQQRP4ahXftlMsqCQ"

# === Keep Alive for Render Ping (optional) ===
keep_alive()

# === Bot Entry Function ===
async def main():
    print("🐉 DragonDusk is starting...")

    app = ApplicationBuilder().token(TOKEN).build()

    # === Register Handlers ===

    app.add_handler(MessageHandler(filters.COMMAND, command_logger), group=1)

    # 📜 Core Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("inventory", inventory))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("hatch", hatch))
    app.add_handler(CommandHandler("id", myid))
    app.add_handler(CommandHandler("gift", gift))
    app.add_handler(CommandHandler("send", send))
    app.add_handler(CommandHandler("debug", debug))
    app.add_handler(CommandHandler("drackstats", drackstats))
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
    app.add_handler(CommandHandler("region", region))
    app.add_handler(CommandHandler("travel", travel))
    app.add_handler(CommandHandler("dracklist", dragonslist))
    app.add_handler(CallbackQueryHandler(dragonslist_callback, pattern=r"^dragons_page_\d+$")) 
    app.add_handler(CommandHandler("drackinfo", dragonsinfo))

    # 🗺️ Region UI
    app.add_handler(CallbackQueryHandler(show_region_details, pattern=r"^region_"))
    app.add_handler(CallbackQueryHandler(region_back, pattern="^region_back$"))

    # 🐉 Dragon System
    app.add_handler(CommandHandler("dragons", dragons))
    app.add_handler(CommandHandler("feed", feed))
    app.add_handler(CommandHandler("train", train))
    app.add_handler(CommandHandler("release", release))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("Wheremi", whereami))

    # 🥚 Egg System
    app.add_handler(CommandHandler("getegg", getegg))
    app.add_handler(CommandHandler("eggs", eggs))
    app.add_handler(CommandHandler("eghatch", eghatch))

    # 📚 Guides
    app.add_handler(CommandHandler("guide", guide))
    app.add_handler(CommandHandler("stats", command_stats))
    app.add_handler(CommandHandler("giftdrack", giftdrack))

    # 🔘 Inline Button Handlers
    app.add_handler(CallbackQueryHandler(select_dragon_callback, pattern=r"^selectdragon_"))
    app.add_handler(CallbackQueryHandler(handle_move, pattern=r"^move_"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern=r"^help_"))
    app.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer(), pattern=r"^ignore$"))
    app.add_handler(CallbackQueryHandler(buy_button_handler, pattern=r"^buy_\d+$"))
    app.add_handler(ChatMemberHandler(dragon_master_joined, ChatMemberHandler.CHAT_MEMBER))

    # 👥 Group Features
    app.add_handler(CommandHandler("rgroup", registergroup))
    app.add_handler(CommandHandler("addmod", addmod))
    app.add_handler(CommandHandler("mods", mods))
    app.add_handler(CommandHandler("rmmod", rmmod))
    app.add_handler(CommandHandler("cancel", cancel_battle))
    app.add_handler(CommandHandler("task", task))
    app.add_handler(CommandHandler("missions", missions))

    # 🛡️ Clan System
    app.add_handler(CommandHandler("createclan", createclan))
    app.add_handler(CommandHandler("joinclan", joinclan))
    app.add_handler(CommandHandler("myclan", myclan))
    app.add_handler(CommandHandler("leaveclan", leaveclan))
    app.add_handler(CommandHandler("disband", disbandclan))
    app.add_handler(CommandHandler("clanchallenge", clanchallenge))
    app.add_handler(CallbackQueryHandler(accept_clanwar, pattern=r"^accept_clanwar\|"))
    app.add_handler(CallbackQueryHandler(select_pve_dragon, pattern=r"^select_pve_dragon\|"))
    app.add_handler(CallbackQueryHandler(pve_move_handler, pattern=r"^pve_move\|"))
    app.add_handler(CallbackQueryHandler(pve_flee, pattern="^pve_flee$"))
    app.add_handler(CallbackQueryHandler(pve_tame, pattern="^pve_tame$"))
    app.add_handler(CommandHandler("minigames", minigames))
    app.add_handler(CallbackQueryHandler(handle_game_choice))

    # 💰 Currency Transfers
    app.add_handler(CommandHandler("sendusks", sendduskar))
    app.add_handler(CommandHandler("sendgems", sendgems))

    # 🆘 Help
    app.add_handler(CommandHandler("help", help_command))

    # 🛠 Background Tasks
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, track_messages))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.PHOTO, get_file_id))

    # 🔄 Bot Lifecycle Events
    app.add_handler(ChatMemberHandler(bot_added_or_promoted, ChatMemberHandler.MY_CHAT_MEMBER))

    try:
        await app.run_polling()
    except NetworkError:
        print("⚠️ Network error. Retrying in 10 seconds...")
        await asyncio.sleep(10)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        await asyncio.sleep(10)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print("⛔ Bot stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


