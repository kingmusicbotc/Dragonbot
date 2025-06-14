
import os
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
    "Shadow": {"strong": None, "weak": None},
    "Poison": {"strong": "Air", "weak": "Earth"},
    "Ice": {"strong": "Air", "weak": "Fire"},
}

ELEMENT_EMOJI = {
    "Fire": "🔥", "Water": "💧", "Air": "🌪️",
    "Earth": "🪨", "Shadow": "☠️", "Poison": "🧪", "Ice": "❄️"
}


import json, os

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

def calculate_damage(move, attacker, defender):
    base = random.randint(20, 30) if move["type"] == "elemental" else random.randint(10, 20)
    multiplier = 1.0
    adv = ELEMENT_ADVANTAGE.get(attacker["element"], {})
    if move["type"] == "elemental":
        if adv.get("strong") == defender["element"]:
            multiplier = 1.3
        elif adv.get("weak") == defender["element"]:
            multiplier = 0.7
    return int(base * multiplier), multiplier

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

# Challenge command
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
        "status": "pending",
        "dragons": {},
        "group_id": update.effective_chat.id
    }
    save_json(BATTLE_FILE, battles)

    # Ask dragon from challenger
    try:
        await ask_dragon_selection(user_id, context, battle_id)
    except Forbidden:
        await update.message.reply_text("❌ Challenger must start the bot in private chat first.")

    # Ask dragon from opponent
    try:
        await ask_dragon_selection(opponent_id, context, battle_id)
    except Forbidden:
        await update.message.reply_text(f"❌ {opponent.first_name} must start the bot in private chat first.")

    await update.message.reply_text("🐉 Challenge sent! Both players must choose their dragons.")

# Dragon selection
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

    await context.bot.send_message(chat_id=int(user_id), text="Choose your dragon:", reply_markup=InlineKeyboardMarkup(keyboard))

# Dragon selection callback
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
    battle = battles.get(battle_id)
    if not battle or user_id not in [battle["challenger_id"], battle["opponent_id"]]:
        await query.edit_message_text("❌ You are not part of this battle.")
        return

    # Save selected dragon
    battle["dragons"][user_id] = dragon_name
    save_json(BATTLE_FILE, battles)

    # ✅ Acknowledge selection
    try:
        await query.edit_message_text(f"✅ You selected <b>{dragon_name}</b>!", parse_mode="HTML")
    except telegram.error.BadRequest as e:
        if "Message is not modified" not in str(e):
            raise

    # ✅ Check if both players selected dragons (move this OUTSIDE the try-except!)
    if battle["dragons"].get(battle["challenger_id"]) and battle["dragons"].get(battle["opponent_id"]):
        battle["status"] = "active"
        battle["turn"] = battle["challenger_id"]
        save_json(BATTLE_FILE, battles)

        group_id = battle.get("group_id")
        if group_id:
            await context.bot.send_message(
                chat_id=group_id,
                text="🔥 Both dragons are ready!\n⚔️ Let the battle begin!"
            )
            await send_attack_prompt(context, battle_id)

async def send_attack_prompt(context, battle_id):
    battles = load_json(BATTLE_FILE)
    dragons = load_json(DRAGON_STATS_FILE)
    battle = battles[battle_id]
    attacker_id = battle["turn"]
    group_id = battle["group_id"]
    message_id = battle.get("message_id")

    attacker_name = battle["dragons"][attacker_id]
    opponent_id = battle["challenger_id"] if attacker_id == battle["opponent_id"] else battle["opponent_id"]
    opponent_name = battle["dragons"][opponent_id]

    attacker = get_dragon_by_name(attacker_name, dragons)
    opponent = get_dragon_by_name(opponent_name, dragons)

    if not attacker or not opponent:
        await context.bot.send_message(group_id, "❌ One or both dragons not found.")
        return

    if "hp" not in battle:
        battle["hp"] = {
            attacker_id: attacker["base_hp"],
            opponent_id: opponent["base_hp"]
        }

    hp1 = battle["hp"][attacker_id]
    hp2 = battle["hp"][opponent_id]
    max_hp1 = attacker["base_hp"]
    max_hp2 = opponent["base_hp"]

    atk_user = await context.bot.get_chat(attacker_id)
    def_user = await context.bot.get_chat(opponent_id)

    def hp_bar(current, total):
        percent = current / total
        filled = int(percent * 10)
        return "█" * filled + "░" * (10 - filled)

    hp_bar1 = hp_bar(hp1, max_hp1)
    hp_bar2 = hp_bar(hp2, max_hp2)

    text = f"""
⚔️ <b>Battle Round</b>

👤 <b>{atk_user.first_name}</b>'s 🐉 <b>{attacker_name}</b> (<i>{attacker["element"]}</i>)  
<b>VS</b>  
👤 <b>{def_user.first_name}</b>'s 🐉 <b>{opponent_name}</b> (<i>{opponent["element"]}</i>)

❤️ <b>HP Status:</b>  
<b>{atk_user.first_name}</b>: {hp_bar1} <code>{hp1}/{max_hp1}</code>  
<b>{def_user.first_name}</b>: {hp_bar2} <code>{hp2}/{max_hp2}</code>

🎯 <b>{atk_user.first_name}, choose your next move:</b>
"""

    keyboard = []
    row = []
    for i, m in enumerate(attacker["moves"]):
        emoji = "🔥" if m["type"] == "elemental" else "💪"
        row.append(InlineKeyboardButton(f"{emoji} {m['name']}", callback_data=f"move_{battle_id}_{i}_{attacker_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if message_id:
            await context.bot.edit_message_text(
                chat_id=group_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        else:
            msg = await context.bot.send_message(
                chat_id=group_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            battle["message_id"] = msg.message_id
            save_json(BATTLE_FILE, battles)
    except:
        pass


async def handle_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    try:
        data = query.data[len("move_"):]
        *battle_parts, attacker_id = data.split("_")
        battle_id = "_".join(battle_parts[:-1])
        move_idx = int(battle_parts[-1])
    except:
        return

    battles = load_json(BATTLE_FILE)
    dragons = load_json(DRAGON_STATS_FILE)
    users = load_json(USER_FILE)
    battle = battles.get(battle_id)
    if not battle or battle["status"] != "active":
        return

    # Deny if not the attacker
    if user_id != battle["turn"]:
        await query.answer("❌ You're not participating in this battle.", show_alert=True)
        return

    attacker_id = user_id
    defender_id = battle["challenger_id"] if attacker_id == battle["opponent_id"] else battle["opponent_id"]
    group_id = battle["group_id"]
    message_id = battle.get("message_id")

    atk_name = (await context.bot.get_chat(attacker_id)).first_name
    def_name = (await context.bot.get_chat(defender_id)).first_name

    atk_dragon_name = battle["dragons"][attacker_id]
    def_dragon_name = battle["dragons"][defender_id]
    atk_dragon = get_dragon_by_name(atk_dragon_name, dragons)
    def_dragon = get_dragon_by_name(def_dragon_name, dragons)
    move = atk_dragon["moves"][move_idx]

    if "hp" not in battle:
        battle["hp"] = {
            attacker_id: atk_dragon["base_hp"],
            defender_id: def_dragon["base_hp"]
        }

    damage, mult = calculate_damage(move, atk_dragon, def_dragon)
    battle["hp"][defender_id] -= damage
    battle["hp"][defender_id] = max(0, battle["hp"][defender_id])

    effect = get_effect_line(mult)
    hp1 = battle["hp"][attacker_id]
    hp2 = battle["hp"][defender_id]
    max_hp1 = atk_dragon["base_hp"]
    max_hp2 = def_dragon["base_hp"]

    def hp_bar(current, total):
        percent = current / total
        filled = int(percent * 10)
        return "█" * filled + "░" * (10 - filled)

    hp_bar1 = hp_bar(hp1, max_hp1)
    hp_bar2 = hp_bar(hp2, max_hp2)

    battle_text = f"""
⚔️ <b>Battle Turn</b>  
👤 <b>{atk_name}</b> vs <b>{def_name}</b>  
🐉 <b>{atk_dragon_name}</b> (<i>{atk_dragon["element"]}</i>) vs <b>{def_dragon_name}</b> (<i>{def_dragon["element"]}</i>)  
❤️ <b>HP:</b>  
<b>{atk_name}</b>: {hp_bar1} <code>{hp1}/{max_hp1}</code>  
<b>{def_name}</b>: {hp_bar2} <code>{hp2}/{max_hp2}</code>

🎯 <b>{atk_name}</b> used <b>{move['name']}</b>!  
{effect}  
💥 <b>{def_name}</b> loses <b>{damage}</b> HP!
"""

    if battle["hp"][defender_id] <= 0:
        battle["status"] = "finished"
        battle_text += f"\n\n🏆 <b>{atk_name}</b> wins the battle!"

        # Send final result
        await context.bot.edit_message_text(
            chat_id=group_id,
            message_id=message_id,
            text=battle_text,
            parse_mode="HTML"
        )

        # Rewards
        winner = users.get(attacker_id, {})
        loser = users.get(defender_id, {})
        winner["duskar"] = winner.get("duskar", 0) + 300
        winner["gems"] = winner.get("gems", 0) + 5
        winner["wins"] = winner.get("wins", 0) + 1
        loser["losses"] = loser.get("losses", 0) + 1
        users[attacker_id] = winner
        users[defender_id] = loser
        save_json(USER_FILE, users)

    else:
        # Switch turn and update same message
        battle["turn"] = defender_id
        save_json(BATTLE_FILE, battles)

        await context.bot.edit_message_text(
            chat_id=group_id,
            message_id=message_id,
            text=battle_text,
            parse_mode="HTML"
        )

        await send_attack_prompt(context, battle_id)
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

BATTLE_FILE = "battle.json"

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



async def cancel_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    battles = load_json(BATTLE_FILE)
    found = False

    for battle_id, battle in list(battles.items()):
        if battle["status"] == "pending" and (battle["challenger_id"] == user_id or battle["opponent_id"] == user_id):
            del battles[battle_id]
            save_json(BATTLE_FILE, battles)
            await update.message.reply_text("⚠️ Battle challenge cancelled.\nNo rewards. No stats.\n🧊 Challenge withdrawn peacefully.", parse_mode="HTML")
            found = True
            break

    if not found:
        await update.message.reply_text("❌ No pending battle found for you to cancel.")
