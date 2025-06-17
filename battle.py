ort os
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

BATTLE_FILE = "battle.json"
USER_FILE = "users.json"
DRAGON_STATS_FILE = "dragons.json"

ELEMENT_ADVANTAGE = {
    "Fire": {"strong": "Earth", "weak": "Water"},
    "Water": {"strong": "Fire", "weak": "Air"},
    "Air": {"strong": "Water", "weak": "Earth"},
    "Earth": {"strong": "Air", "weak": "Fire"},
    "Poison": {"strong": "Air", "weak": "Earth"},
    "Ice": {"strong": "Air", "weak": "Fire"},
    "Shadow": {"strong": None, "weak": None},
    "Cosmic": {"strong": None, "weak": None},  # Add if needed
    "Light": {"strong": "Shadow", "weak": "Poison"},
    "Dark": {"strong": "Light", "weak": "None"},
}

ELEMENT_EMOJI = {
    "Fire": "🔥", "Water": "💧", "Air": "🌪️",
    "Earth": "🪨", "Shadow": "☠️", "Poison": "🧪",
    "Ice": "❄️", "Cosmic": "🌌", "Light": "🌟", "Dark": "🌑"
}

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def make_battle_id(user1, user2):
    return f"battle_{min(user1, user2)}_{max(user1, user2)}"

def hp_bar(hp, max_hp, length=10):
    filled = int(hp / max_hp * length)
    return "█" * filled + "░" * (length - filled)

# ✅ FIXED DAMAGE CALCULATION
def calculate_damage(move, attacker, defender):
    move_power = move.get("power", 30)  # fallback if move data incomplete
    multiplier = 1.0

    attacker_element = attacker.get("element")
    defender_element = defender.get("element")

    advantage = ELEMENT_ADVANTAGE.get(attacker_element, {})

    if move["type"] == "elemental":
        if advantage.get("strong") == defender_element:
            multiplier = 1.3
        elif advantage.get("weak") == defender_element:
            multiplier = 0.7

    damage = int(move_power * multiplier)
    return damage, multiplier

def get_effect_line(mult):
    if mult > 1:
        return "🔥 It’s super effective!"
    elif mult < 1:
        return "💧 It’s not very effective..."
    return "💥 It's a solid hit!"

def get_dragon_by_name(name: str, data: dict):
    for real_name in data:
        if real_name.lower() == name.lower():
            return data[real_name]
    return None

# === Challenge Command ===
async def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opponent = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not opponent:
        await update.message.reply_text("❌ Reply to someone to challenge them.")
        return

    user_id = str(update.effective_user.id)
    opponent_id = str(opponent.id)

    if user_id == opponent_id:
        await update.message.reply_text("🌀 You can't challenge yourself.")
        return

    battle_id = make_battle_id(user_id, opponent_id)
    battles = load_json(BATTLE_FILE)

    battles[battle_id] = {
        "challenger_id": user_id,
        "opponent_id": opponent_id,
        "player1": user_id,
        "player2": opponent_id,
        "status": "pending",
        "dragons": {},
        "group_id": update.effective_chat.id
    }
    save_json(BATTLE_FILE, battles)

    # Ask dragon from both users in DM
    try:
        await ask_dragon_selection(user_id, context, battle_id)
    except Exception:
        await update.message.reply_text("❌ Challenger must start the bot in private chat first.")

    try:
        await ask_dragon_selection(opponent_id, context, battle_id)
    except Exception:
        await update.message.reply_text(f"❌ {opponent.first_name} must start the bot in private chat first.")

    await update.message.reply_text("🐉 Challenge sent! Both players must choose their dragons.")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import telegram  # Needed for catching BadRequest

# Dragon selection prompt
async def ask_dragon_selection(user_id: str, context, battle_id: str):
    users = load_json(USER_FILE)
    user = users.get(user_id)

    if not user or not user.get("dragons"):
        await context.bot.send_message(chat_id=int(user_id), text="❌ You don’t have any dragons.")
        return

    keyboard = []
    for d in user["dragons"]:
        name = d["name"]
        emoji = ELEMENT_EMOJI.get(d["element"], "🐉")
        keyboard.append([InlineKeyboardButton(f"{emoji} {name}", callback_data=f"selectdragon_{name}_{battle_id}")])

    await context.bot.send_message(
        chat_id=int(user_id),
        text="🐲 Choose your dragon:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Callback when dragon is selected
from telegram.constants import ParseMode
import telegram.error

async def select_dragon_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    try:
        _, dragon_name, battle_id = query.data.split("_", 2)
    except ValueError:
        await query.edit_message_text("❌ Invalid selection.")
        return

    battles = load_json(BATTLE_FILE)
    users = load_json(USER_FILE)
    battle = battles.get(battle_id)

    if not battle or user_id not in [battle["challenger_id"], battle["opponent_id"]]:
        await query.edit_message_text("❌ You are not part of this battle.")
        return

    # Prevent double selection
    if user_id in battle["dragons"]:
        await query.edit_message_text("⚠️ You've already selected your dragon.")
        return

    # Save selected dragon
    battle["dragons"][user_id] = dragon_name
    save_json(BATTLE_FILE, battles)

    # Add XP key to user's dragon if missing
    if user_id in users:
        user_dragons = users[user_id].get("dragons", [])
        for d in user_dragons:
            if d.get("name") == dragon_name:
                xp_key = f"xp_{dragon_name.lower()}"
                if xp_key not in d:
                    d[xp_key] = 0
                break
        save_json(USER_FILE, users)

    # Confirm selection in DM
    try:
        await query.edit_message_text(f"✅ You selected <b>{dragon_name}</b>!", parse_mode=ParseMode.HTML)
    except telegram.error.BadRequest as e:
        if "Message is not modified" not in str(e):
            raise

    # Start battle if both dragons selected
    if battle["dragons"].get(battle["challenger_id"]) and battle["dragons"].get(battle["opponent_id"]):
        battle["status"] = "active"
        battle["turn"] = battle["challenger_id"]

        group_id = battle.get("group_id")
        if group_id:
            try:
                msg = await context.bot.send_message(
                    chat_id=group_id,
                    text="🔥 Both dragons are ready!\n⚔️ Let the battle begin!"
                )
                battle["message_id"] = msg.message_id
            except Exception as e:
                print("❌ Error starting battle:", e)

        save_json(BATTLE_FILE, battles)
        await send_attack_prompt(context, battle_id)

                # === INSIDE your file, not inside callback ===
from telegram.constants import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_attack_prompt(context, battle_id):
    battles = load_json(BATTLE_FILE)
    users = load_json(USER_FILE)
    dragons = load_json(DRAGON_STATS_FILE)
    battle = battles.get(battle_id)

    if not battle:
        return

    turn_id = battle.get("turn")
    player1 = battle.get("challenger_id")
    player2 = battle.get("opponent_id")
    opponent_id = player2 if turn_id == player1 else player1

    if not turn_id or not player1 or not player2:
        return

    attacker_name = battle["dragons"].get(turn_id)
    opponent_name = battle["dragons"].get(opponent_id)

    attacker = get_dragon_by_name(attacker_name, dragons)
    opponent = get_dragon_by_name(opponent_name, dragons)

    if not attacker or not opponent:
        await context.bot.send_message(battle["group_id"], "❌ One or both dragons not found.")
        return

    # Initialize HP if missing
    if "hp" not in battle:
        battle["hp"] = {}
    if turn_id not in battle["hp"]:
        battle["hp"][turn_id] = attacker.get("base_hp", 100)
    if opponent_id not in battle["hp"]:
        battle["hp"][opponent_id] = opponent.get("base_hp", 100)

    hp1 = battle["hp"][turn_id]
    hp2 = battle["hp"][opponent_id]
    max_hp1 = attacker.get("base_hp", 100)
    max_hp2 = opponent.get("base_hp", 100)

    # Get usernames (fallbacks)
    atk_user = await context.bot.get_chat(turn_id)
    def_user = await context.bot.get_chat(opponent_id)
    atk_name = atk_user.first_name or "Attacker"
    def_name = def_user.first_name or "Defender"

    def hp_bar(current, total):
        percent = max(0, min(current / total, 1)) if total else 0
        filled = round(percent * 10)
        return "█" * filled + "░" * (10 - filled)

    hp_bar1 = hp_bar(hp1, max_hp1)
    hp_bar2 = hp_bar(hp2, max_hp2)

    last_action = battle.get("last_action_text", "")

    text = f"""
╔══════🔥 Battle Turn 🔥══════╗

👤 <b>{atk_name}</b> 🆚 <b>{def_name}</b>

{ELEMENT_EMOJI.get(attacker['element'], '🐉')} <b>{attacker_name}</b> — {attacker['element']}  
❤️ {hp_bar1} {hp1}/{max_hp1}

🆚

{ELEMENT_EMOJI.get(opponent['element'], '🐉')} <b>{opponent_name}</b> — {opponent['element']}  
🛡️ {hp_bar2} {hp2}/{max_hp2}

🎯 Your turn, <b>{atk_name}</b>!  
Choose your skill below.

{last_action}

╚════════════════════════════╝
""".strip()

    # Skill Buttons only, NO Potion button
    keyboard = []
    row = []
    for i, move in enumerate(attacker.get("moves", [])):
        emoji = "🔥" if move["type"] == "elemental" else "💪"
        row.append(InlineKeyboardButton(f"{emoji} {move['name']}", callback_data=f"move_{battle_id}_{i}_{turn_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if "message_id" in battle:
            await context.bot.edit_message_text(
                chat_id=battle["group_id"],
                message_id=battle["message_id"],
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            msg = await context.bot.send_message(
                chat_id=battle["group_id"],
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
            battle["message_id"] = msg.message_id
    except Exception as e:
        print("❌ Error sending attack prompt:", e)

    save_json(BATTLE_FILE, battles)


async def handle_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    try:
        _, rest = query.data.split("move_", 1)
        parts = rest.split("_")
        battle_id = "_".join(parts[:-2])
        move_idx = int(parts[-2])
        attacker_id = parts[-1]
    except Exception:
        await query.answer("❌ Invalid move format.", show_alert=True)
        return

    battles = load_json(BATTLE_FILE)
    dragons = load_json(DRAGON_STATS_FILE)
    users = load_json(USER_FILE)
    battle = battles.get(battle_id)

    if not battle or battle.get("status") != "active":
        return

    if user_id != battle.get("turn"):
        await query.answer("❌ It's not your turn.", show_alert=True)
        return

    defender_id = battle["challenger_id"] if user_id == battle["opponent_id"] else battle["opponent_id"]

    # Load dragons
    atk_dragon_name = battle["dragons"].get(user_id)
    def_dragon_name = battle["dragons"].get(defender_id)
    atk_dragon = get_dragon_by_name(atk_dragon_name, dragons)
    def_dragon = get_dragon_by_name(def_dragon_name, dragons)

    if not atk_dragon or not def_dragon:
        await query.answer("❌ Dragon data missing.", show_alert=True)
        return

    move = atk_dragon["moves"][move_idx]

    # Initialize HP if needed
    if "hp" not in battle:
        battle["hp"] = {
            user_id: atk_dragon["base_hp"],
            defender_id: def_dragon["base_hp"]
        }

    # Defend status
    defend_next = battle.get("defend_next", {})
    is_defending = defend_next.get(defender_id, False)

    damage, mult = calculate_damage(move, atk_dragon, def_dragon)
    if is_defending:
        damage = int(damage * 0.5)
        defend_next[defender_id] = False
    battle["defend_next"] = defend_next

    battle["hp"][defender_id] = max(0, battle["hp"].get(defender_id, def_dragon["base_hp"]) - damage)

    atk_user = await context.bot.get_chat(user_id)
    def_user = await context.bot.get_chat(defender_id)
    atk_name = atk_user.first_name or "Attacker"
    def_name = def_user.first_name or "Defender"

    effect = get_effect_line(mult)
    battle["last_action_text"] = (
        f"\n📜 ⚔️ <b>{atk_name}</b> used <b>{move['name']}</b>!\n"
        f"{effect}\n"
        f"💥 <b>{def_name}</b> loses <b>{damage} HP</b>!"
    )

    if battle["hp"][defender_id] <= 0:
        battle["status"] = "finished"
        winner = users.get(user_id, {})
        loser = users.get(defender_id, {})

        # Award both players
        winner["duskar"] = winner.get("duskar", 0) + 300
        winner["gems"] = winner.get("gems", 0) + 5
        winner["wins"] = winner.get("wins", 0) + 1

        loser["duskar"] = loser.get("duskar", 0) + 150
        loser["gems"] = loser.get("gems", 0) + 2
        loser["losses"] = loser.get("losses", 0) + 1

        # Level system
        def add_xp(user, xp_gain):
            user["xp"] = user.get("xp", 0) + xp_gain
            user["level"] = user.get("level", 1)
            leveled_up = False
            while user["xp"] >= user["level"] * 1000:
                user["xp"] -= user["level"] * 1000
                user["level"] += 1
                leveled_up = True
            return leveled_up

        winner_up = add_xp(winner, 100)
        loser_up = add_xp(loser, 40)

        for uid, dragon_name, xp_gain in [
            (user_id, atk_dragon_name, 100),
            (defender_id, def_dragon_name, 40)
        ]:
            for d in users[uid].get("dragons", []):
                if d["name"] == dragon_name:
                    xp_key = f"xp_{dragon_name.lower()}"
                    d[xp_key] = d.get(xp_key, 0) + xp_gain
                    break

        users[user_id] = winner
        users[defender_id] = loser
        save_json(USER_FILE, users)

        battle["last_action_text"] += (
            f"\n\n🏆 <b>{atk_name}</b> wins the battle!"
            f"\n💰 <b>{atk_name}</b> earned 300 Duskar & 5 Gems"
            f"\n🧠 <b>{atk_name}</b> earned 100 XP"
            f"\n😓 <b>{def_name}</b> earned 150 Duskar & 2 Gems"
            f"\n🧠 <b>{def_name}</b> earned 40 XP"
        )
        if winner_up:
            battle["last_action_text"] += f"\n🔼 <b>{atk_name}</b> leveled up to Level {winner['level']}!"
        if loser_up:
            battle["last_action_text"] += f"\n🔼 <b>{def_name}</b> leveled up to Level {loser['level']}!"

        save_json(BATTLE_FILE, battles)

        await context.bot.edit_message_text(
            chat_id=battle["group_id"],
            message_id=battle["message_id"],
            text=battle["last_action_text"],
            parse_mode=ParseMode.HTML
        )
    else:
        battle["turn"] = defender_id
        save_json(BATTLE_FILE, battles)
        await send_attack_prompt(context, battle_id)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

BATTLE_FILE = "battle.json"
USER_FILE = "users.json"
DRAGON_STATS_FILE = "dragons.json"

# === JSON Load/Save ===
def load_json(filename):
    import json, os
    if not os.path.exists(filename):
        return {}
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename, data):
    import json
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# === CANCEL BATTLE ===
async def cancel_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    battles = load_json(BATTLE_FILE)
    found = False

    for battle_id, battle in list(battles.items()):
        if not isinstance(battle, dict):
            continue
        if battle.get("status") == "pending" and user_id in [battle.get("challenger_id"), battle.get("opponent_id")]:
            del battles[battle_id]
            save_json(BATTLE_FILE, battles)
            await update.message.reply_text(
                "⚠️ Battle challenge cancelled.\nNo rewards. No stats.\n🧊 Challenge withdrawn peacefully.",
                parse_mode=ParseMode.HTML
            )
            found = True
            break

    if not found:
        await update.message.reply_text("❌ No pending battle found for you to cancel.")

