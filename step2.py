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
def format_eggs(eggs):
    if not eggs:
        return "🚫 No eggs"

    rarity_counts = {}
    pending = 0
    hatched = 0

    for egg in eggs:
        r = egg.get("rarity", "Unknown")
        emoji = egg.get("emoji", "🥚")
        key = f"{emoji} {r}"
        rarity_counts[key] = rarity_counts.get(key, 0) + 1
        if egg.get("status") == "pending":
            pending += 1
        else:
            hatched += 1

    lines = []
    for k, count in rarity_counts.items():
        lines.append(f"{k}: {count}")
    lines.append(f"🕒 Pending: {pending} | ✅ Hatched: {hatched}")
    return "\n".join(lines)

def get_element_emoji(element):
    return {
        "Fire": "🔥",
        "Water": "💧",
        "Earth": "🌱",
        "Air": "🌪️",
        "Shadow": "🌑",
        "Light": "🌟",
        "Electric": "⚡",
        "Ice": "❄️",
        "Metal": "⚙️"
    }.get(element, "❓")

def get_leader_position(user_id, all_users, key):
    sorted_users = sorted(all_users.items(), key=lambda x: x[1].get(key, 0), reverse=True)
    for i, (uid, _) in enumerate(sorted_users, start=1):
        if str(uid) == str(user_id):
            return i
    return "N/A"

# Main userstats command
async def userstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get target user
        if update.message and update.message.reply_to_message:
            user = update.message.reply_to_message.from_user
        elif context.args:
            username = context.args[0].lstrip('@')
            for u_id, u_data in load_user_data().items():
                if u_data.get("username", "").lower() == username.lower():
                    user = type('User', (), {'id': int(u_id), 'first_name': u_data.get("first_name", username)})
                    break
            else:
                await update.effective_message.reply_text("❌ Username not found.")
                return
        else:
            user = update.effective_user

        # Load user data
        data = get_user_data(user.id)
        if not data:
            await update.effective_message.reply_text("❌ No data found for this user.")
            return

        dragons = data.get("dragons", [])
        eggs = data.get("eggs", [])
        explore_count = data.get("explore_count", 0)
        duskar = data.get("duskar", 0)
        gems = data.get("gems", 0)
        wins = data.get("wins", 0)
        xp = data.get("xp", 0)
        level = data.get("level", 1)

        # XP bar
        next_level_xp = level * 1000
        xp_bar = int((xp / next_level_xp) * 10)
        xp_bar_str = "█" * xp_bar + "░" * (10 - xp_bar)

        # Egg breakdown
        egg_types = {}
        hatched = 0
        for egg in eggs:
            egg_type = egg.get("type", "Unknown")
            egg_types[egg_type] = egg_types.get(egg_type, 0) + 1
            if egg.get("xp", 0) >= 100:
                hatched += 1
        pending = len(eggs) - hatched

        # Rankings
        all_users = load_user_data()
        duskar_rank = get_leader_position(user.id, all_users, "duskar")
        gem_rank = get_leader_position(user.id, all_users, "gems")
        win_rank = get_leader_position(user.id, all_users, "wins")
        explore_rank = get_leader_position(user.id, all_users, "explore_count")

        # Tame rank
        tame_rank = sorted(all_users.items(), key=lambda x: len(x[1].get("dragons", [])), reverse=True)
        tame_rank = next((i + 1 for i, (uid, _) in enumerate(tame_rank) if str(uid) == str(user.id)), "—")

        # Dragon display
        if dragons:
            dragon_info = "\n".join(
                f"• <b>{d.get('name', 'Unnamed')}</b> "
                f"({get_element_emoji(d.get('element'))} {d.get('element', '?')}) – "
                f"🐉 Lv.{d.get('level', 1)} | ⚡ {d.get('power', 0)}"
                for d in dragons
            )
        else:
            dragon_info = "🚫 No dragons yet."

        # Final Message
        msg = f"""
<b>📊 Stats for {user.first_name}</b>
╭━━━━━━━━━━🐉 DRAGONS ━━━━━━━━━━╮
<b>Total:</b> {len(dragons)} owned
{dragon_info}
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━🥚 EGGS ━━━━━━━━━━━━━╮
🔸 <b>Pending:</b> {pending} ✅ <b>Hatched:</b> {hatched}
🔹 {" | ".join(f"{k}: {v}" for k, v in egg_types.items()) if egg_types else "None"}
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━📈 STATS ━━━━━━━━━━━╮
💰 <b>Duskar:</b> {duskar}  🏅 Rank #{duskar_rank}
💎 <b>Gems:</b> {gems}   🏅 Rank #{gem_rank}
⚔️ <b>Wins:</b> {wins}   🏅 Rank #{win_rank}
🧭 <b>Explores:</b> {explore_count} 🏅 Rank #{explore_rank}
🐲 <b>Dragons Tamed:</b> {len(dragons)} 🏅 Rank #{tame_rank}
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━🧠 PROGRESS ━━━━━━━━━╮
⭐ <b>XP:</b> {xp_bar_str} <code>{xp}/{next_level_xp}</code>
🔼 <b>Level:</b> {level}
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""

        await update.effective_message.reply_text(msg, parse_mode="HTML")

    except Exception as e:
        print(f"[userstats ERROR] {e}")
        await update.effective_message.reply_text("⚠️ An error occurred while fetching stats.")


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
import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

USER_FILE = "users.json"

RARITY_POOL = [
        ("Normal", 50, "🥚"),
        ("Rare", 36, "🔷"),
        ("Legendary", 10, "🌟"),
        ("Ultimate", 4, "💠")
    ]

    # === JSON Handling ===
def load_json(file):
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

def save_json(file, data):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # === Rarity Functions ===
def choose_rarity():
        roll = random.randint(1, 100)
        total = 0
        for rarity, chance, emoji in RARITY_POOL:
            total += chance
            if roll <= total:
                return rarity, emoji
        return "Normal", "🥚"  # Fallback

def chance_to_hatch(rarity):
        if rarity == "Normal":
            return random.random() < 0.5
        elif rarity == "Rare":
            return random.random() < 0.75
        return True  # Legendary & Ultimate always hatch

    # === Main Egg Command ===
async def getegg(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        users = load_json(USER_FILE)
        user = users.setdefault(user_id, {})

        today = datetime.now().date()
        last_egg = user.get("last_egg")

        # Check daily limit
        if last_egg:
            try:
                last_egg_date = datetime.fromisoformat(last_egg).date()
                if last_egg_date == today:
                    await update.message.reply_text("🕒 You've already received an egg today. Try again tomorrow!")
                    return
            except Exception as e:
                print(f"Error parsing last_egg date: {e}")

        # Generate egg
        rarity, emoji = choose_rarity()
        will_hatch = chance_to_hatch(rarity)

        egg_data = {
            "rarity": rarity,
            "emoji": emoji,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "will_hatch": will_hatch
        }

        eggs = user.setdefault("eggs", [])
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
        "Normal": ["Drakelet", "Scaleling", "pyron", "Zephira", "Stormscale"],
        "Rare": ["Spectronox", "Aqualing", "Snowpiercer", "Cindersnout"],
        "Legendary": ["Voidhorn", "Nocturnex"],
        "Ultimate": ["Solarion", "Glacira"]
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

async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            sender_id = str(update.effective_user.id)
            reply_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
            if not reply_user:
                await update.message.reply_text("❌ Reply to the user you want to gift a dragon to.")
                return

            receiver_id = str(reply_user.id)
            users = load_user_data()
            sender = users.get(sender_id, {})
            receiver = users.setdefault(receiver_id, {})
            sender_dragons = sender.get("dragons", [])
            receiver_dragons = receiver.setdefault("dragons", [])

            if not sender_dragons:
                await update.message.reply_text("🐉 You don't have any dragons to gift.")
                return

            if not context.args:
                await update.message.reply_text("📦 Usage: /gift <dragon_number>\nUse /inventory to check your dragon numbers.")
                return

            try:
                index = int(context.args[0]) - 1
                if index < 0 or index >= len(sender_dragons):
                    raise ValueError
            except ValueError:
                await update.message.reply_text("❌ Invalid dragon number. Use /inventory to check.")
                return

            dragon = sender_dragons.pop(index)
            receiver_dragons.append(dragon)
            save_user_data(users)

            await update.message.reply_text(
                f"🎁 You gifted <b>{dragon['name']}</b> to {reply_user.first_name}!",
                parse_mode="HTML"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error during gift: {e}")


async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            sender_id = str(update.effective_user.id)
            reply_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
            if not reply_user:
                await update.message.reply_text("❌ Reply to the user you want to send Duskar or Gems to.")
                return

            receiver_id = str(reply_user.id)
            users = load_user_data()
            sender = users.setdefault(sender_id, {})
            receiver = users.setdefault(receiver_id, {})

            if len(context.args) != 2 or context.args[0].lower() not in ("duskar", "gems"):
                await update.message.reply_text("📤 Usage: /send <duskar|gems> <amount>")
                return

            currency = context.args[0].lower()
            try:
                amount = int(context.args[1])
                if amount <= 0:
                    raise ValueError
            except ValueError:
                await update.message.reply_text("❌ Enter a valid positive amount.")
                return

            sender_amount = sender.get(currency, 0)
            if sender_amount < amount:
                await update.message.reply_text(f"💸 You don't have enough {currency.title()} (You have {sender_amount})!")
                return

            sender[currency] = sender_amount - amount
            receiver[currency] = receiver.get(currency, 0) + amount
            save_user_data(users)

            await update.message.reply_text(
                f"✅ You sent <b>{amount} {currency.title()}</b> to {reply_user.first_name}.",
                parse_mode="HTML"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error during send: {e}")


def load_user_data():
    return load_json("users.json")

def save_user_data(data):
    save_json("users.json", data)


from telegram.helpers import escape

from telegram.helpers import escape

async def drackstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.effective_user.id)
        users = load_json("users.json")
        dragon_data = load_json("dragons.json")

        user = users.get(user_id, {})
        user_dragons = user.get("dragons", [])

        if not user_dragons:
            await update.message.reply_text("🐉 You don't have any dragons yet.")
            return

        if not context.args:
            await update.message.reply_text("📘 Usage: /drackstats <dragon_number>\nCheck your dragon number using /dragons.")
            return

        try:
            index = int(context.args[0]) - 1
            if index < 0 or index >= len(user_dragons):
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Invalid dragon number.")
            return

        dragon = user_dragons[index]
        name = escape(dragon["name"])
        level = dragon.get("level", 1)
        power = dragon.get("power", "?")

        # Use dynamic HP from user dragon, fallback to static
        current_hp = dragon.get("current_hp")
        base_hp = dragon.get("base_hp")
        if base_hp is None or current_hp is None:
            static_info = dragon_data.get(dragon["name"], {})
            base_hp = static_info.get("base_hp", "?")
            current_hp = base_hp
        else:
            # Ensure integers
            base_hp = int(base_hp)
            current_hp = int(current_hp)

        # Use dynamic moves if present, else fallback to static
        moves = dragon.get("moves")
        if not moves:
            moves = dragon_data.get(dragon["name"], {}).get("moves", [])

        # Build stylish moveset showing current move powers
        move_lines = []
        for move in moves:
            emoji = "💥" if move["type"] == "physical" else "🌪️"
            move_name = escape(move["name"])
            move_type = escape(move["type"].capitalize())
            move_power = move.get("power", "?")
            move_lines.append(
                f"┊ {emoji} <b>{move_name}</b>\n"
                f"┊    🌀 <i>{move_type}</i> | 🔋 <b>{move_power}</b>"
            )

        msg = (
            f"╔════════════════════╗\n"
            f"    🐲 <b>Dragon #{index + 1} — Stats</b>\n"
            f"╚════════════════════╝\n\n"
            f"🏷️ <b>Name:</b> {name}\n"
            f"🌈 <b>Element:</b> {escape(dragon.get('element', 'Unknown'))}\n"
            f"📶 <b>Level:</b> {level}\n"
            f"⚔️ <b>Power:</b> {power}\n"
            f"❤️ <b>HP:</b> {current_hp} / {base_hp}\n\n"
            f"📜 <b>Moveset:</b>\n" + "\n".join(move_lines)
        )

        await update.message.reply_text(msg, parse_mode="HTML")

    except Exception as e:
        await update.message.reply_text(f"❌ Error in /drackstats: {e}")

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from datetime import datetime

import json, os

USER_FILE = "users.json"

# Load and save helpers
def load_json(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Get current week
from datetime import datetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

USER_FILE = "users.json"

# Utility functions
def load_json(file):
    import json, os
    return json.load(open(file, encoding='utf-8')) if os.path.exists(file) else {}

def save_json(file, data):
    import json
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_current_week():
    return datetime.utcnow().strftime("%Y-W%U")

# Missions
MISSIONS_LIST = [
    {"key": "explore", "target": 10, "label": "🌲 Explore 10 Times"},
    {"key": "pvp_wins", "target": 5, "label": "⚔️ Win 5 Dragon Battles"},
    {"key": "tames", "target": 3, "label": "🐉 Tame 3 Wild Dragons"}
]

REWARDS = {
    "duskar": 2000,
    "gems": 10,
    "egg": {"rarity": "Rare", "emoji": "🔷", "status": "pending", "timestamp": datetime.now().isoformat()}
}

# Format mission display
def format_mission_progress(progress, missions):
    lines = ["📜 <b>Weekly Dragon Missions</b>", "🗓️ Ends: Sunday Night", ""]
    complete = True

    for mission in missions:
        done = progress.get(mission["key"], 0)
        needed = mission["target"]
        emoji = "✅" if done >= needed else "❌"
        lines.append(f"{emoji} {mission['label']} – <b>{min(done, needed)}</b>/{needed}")
        if done < needed:
            complete = False

    return "\n".join(lines), complete

# Handler
async def missions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USER_FILE)
    user = users.setdefault(user_id, {})

    # Ensure fields exist
    user.setdefault("explore_count", 0)
    user.setdefault("wins", 0)
    user.setdefault("tames", 0)
    user.setdefault("duskar", 0)
    user.setdefault("gems", 0)
    user.setdefault("eggs", [])

    # 🗓️ Weekly reset
    current_week = get_current_week()
    if "missions" not in user or user["missions"].get("week") != current_week:
        user["missions"] = {
            "week": current_week,
            "progress": {"explore": 0, "pvp_wins": 0, "tames": 0},
            "completed": False
        }

    # Update progress
    progress = user["missions"]["progress"]
    progress["explore"] = user["explore_count"]
    progress["pvp_wins"] = user["wins"]
    progress["tames"] = user["tames"]

    # Format message
    mission_text, all_done = format_mission_progress(progress, MISSIONS_LIST)
    reward_text = (
        "\n\n🎁 <b>Rewards on Completion:</b>\n"
        f"💰 <b>{REWARDS['duskar']} Duskar</b>\n"
        f"💎 <b>{REWARDS['gems']} Gems</b>\n"
        f"🥚 <b>{REWARDS['egg']['emoji']} {REWARDS['egg']['rarity']} Egg</b>"
    )

    final = mission_text + reward_text

    # Reward claim
    if all_done and not user["missions"]["completed"]:
        user["missions"]["completed"] = True
        user["duskar"] += REWARDS["duskar"]
        user["gems"] += REWARDS["gems"]
        user["eggs"].append(REWARDS["egg"])
        final += "\n\n🏆 <b>Missions Completed!</b>\n🎊 You earned your weekly rewards!"
    elif all_done and user["missions"]["completed"]:
        final += "\n\n✨ <i>You've already completed this week's missions.</i>"

    # Save
    users[user_id] = user
    save_json(USER_FILE, users)

    # Respond
    await update.message.reply_text(final, parse_mode=ParseMode.HTML)


