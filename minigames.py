from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
import random, os, json
from db import load_json, save_json
from datetime import datetime

USER_FILE = "users.json"
GAME_COST = 100  # Cost to play a minigame


def reward_user(user):
    user.setdefault("duskar", 0)
    user.setdefault("gems", 0)
    user.setdefault("xp", 0)
    user.setdefault("eggs", [])

    duskar = random.randint(100, 300)
    gems = random.choices([0, 5, 10], weights=[80, 15, 5])[0]
    xp = random.randint(20, 60)

    rarity_chance = random.randint(1, 100)
    egg = None
    if rarity_chance > 95:
        egg = {"rarity": "Legendary", "emoji": "🌟", "status": "pending", "timestamp": datetime.now().isoformat()}
    elif rarity_chance > 85:
        egg = {"rarity": "Rare", "emoji": "🔷", "status": "pending", "timestamp": datetime.now().isoformat()}

    user["duskar"] += duskar
    user["gems"] += gems
    user["xp"] += xp
    if egg:
        user["eggs"].append(egg)

    return duskar, gems, xp, egg

# 🔹 STARTING GAME
async def minigames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton("🧭 Dragon Maze", callback_data=f"game_maze:{user_id}")],
        [InlineKeyboardButton("🧨 Heist Mission", callback_data=f"game_heist:{user_id}")],
        [InlineKeyboardButton("🕹️ More games coming soon...", callback_data=f"coming_soon:{user_id}")]
    ]
    await update.message.reply_text(
        "╭━━━━━━━◆༻🎮༺◆━━━━━━━╮\n"
        "┃ <b>DragonDusk MiniGames</b>\n"
        "╰━━━━━━━◆༻🐉༺◆━━━━━━━╯\n\n"
        "Choose your challenge, brave tamer:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

# 🔹 GAME HANDLER
async def handle_game_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    action, owner_id = data.split(":")
    user_id = str(query.from_user.id)

    if user_id != owner_id:
        await query.answer("⚠️ You're not the one who started this game.", show_alert=True)
        return

    users = load_users()
    user = users.setdefault(user_id, {})
    user.setdefault("duskar", 0)

    # Handle menu-only clicks (no cost)
    if action == "coming_soon":
        await query.answer("🛠️ More games are in development... Stay tuned!", show_alert=True)
        return

    # Handle actual minigames with Duskar deduction
    if action in ["game_maze", "game_heist"]:
        if user["duskar"] < GAME_COST:
            await query.answer("💸 You need 100 Duskar to play! Earn more through exploring or battling.", show_alert=True)
            return

        # Deduct and notify
        user["duskar"] -= GAME_COST
        save_users(users)

        await query.message.reply_text(
            f"💸 You spent <b>{GAME_COST} Duskar</b> to enter the mini-game!",
            parse_mode="HTML"
        )

    if action == "game_maze":
        await query.edit_message_text(
            "🌪️ <b>Dragon Maze</b>\nYou enter the whispering labyrinth...\nWhich path will lead to treasure?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Left", callback_data=f"maze_left:{owner_id}")],
                [InlineKeyboardButton("➡️ Right", callback_data=f"maze_right:{owner_id}")],
                [InlineKeyboardButton("⬆️ Straight", callback_data=f"maze_straight:{owner_id}")],
            ]),
            parse_mode="HTML"
        )

    elif action == "game_heist":
        await query.edit_message_text(
            "🧨 <b>Dragon Heist</b>\nYou sneak into the lava-guarded vault...\n⏳ Looting cursed treasure...",
            parse_mode="HTML"
        )
        duskar, gems, xp, egg = reward_user(user)
        save_users(users)

        text = (
            "╭━━━━━━━◆༻🎮༺◆━━━━━━━╮\n"
            "┃ <b>Mini-Game Rewards Unlocked!</b>\n"
            "╰━━━━━━━◆༻🐉༺◆━━━━━━━╯\n\n"
            f"💰 Duskar Earned: {duskar}\n"
            f"💎 Gems Found: {gems}\n"
            f"🧠 XP Gained: {xp}"
        )
        if egg:
            text += f"\n\n🥚 Bonus Egg: {egg['emoji']} <b>{egg['rarity']}</b>!"
        await query.message.reply_text(text, parse_mode="HTML")

    elif action.startswith("maze_"):
        correct_path = random.choice(["maze_left", "maze_right", "maze_straight"])
        if action == correct_path:
            duskar, gems, xp, egg = reward_user(user)
            save_users(users)
            text = (
                "╭━━━━━━━◆༻🌪️༺◆━━━━━━━╮\n"
                "┃ <b>You escaped the Dragon Maze!</b>\n"
                "╰━━━━━━━◆༻🎁༺◆━━━━━━━╯\n\n"
                f"💰 Duskar: {duskar}\n"
                f"💎 Gems: {gems}\n"
                f"🧠 XP: {xp}"
            )
            if egg:
                text += f"\n🥚 Bonus Egg: {egg['emoji']} <b>{egg['rarity']}</b>!"
        else:
            text = (
                "╭━━━━━━━◆༻💀༺◆━━━━━━━╮\n"
                "┃ <b>Trap Triggered!</b>\n"
                "╰━━━━━━━◆༻🕸️༺◆━━━━━━━╯\n\n"
                "You took a wrong turn...\nA shadowy dragon blocked your escape!"
            )
        await query.edit_message_text(text, parse_mode="HTML")
