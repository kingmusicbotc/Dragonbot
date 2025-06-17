from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from telegram.constants import ChatType, ParseMode
from telegram.helpers import escape_markdown

def is_private_chat(update: Update):
    return update.effective_chat.type == ChatType.PRIVATE


import json

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

import json, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# ======= Utility Loaders =======
def load_users():
    with open("users.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def load_dragons():
    with open("dragons.json", "r", encoding="utf-8") as f:
        return json.load(f)


REGIONS = {
    "Volcanic Wastes": {
        "image": "https://graph.org/file/dd88fdf7e0bbfa674d091-b6cc54c6de06d7745c.jpg",
        "element": "🌋 Fire / 🌑 Shadow",
        "enemies": [
            "Pyron", "Blazetail", "Emberfang", "Lavagron", "Cindersnout",
            "Umbrazor", "Trevor", "Voidhorn", "Spectronox", "Nocturnex",
            "Duskwraith", "Grimhorn"
        ],
        "rewards": ["🔥 Ember Egg", "👻 Dark Crystal"]
    },
    "Everleaf Forest": {
        "image": "AgACAgUAAxkBAAILwmhOct_D08qAYBmYdYoQRXdeD5CpAAKSyzEbZEN5VghfhKNlXPOWAQADAgADeQADNgQ",
        "element": "🌳 Nature / ☠️ Poison",
        "enemies": [
            "Venodrax", "Venomscale", "Leaflash", "Barkflare", "Gloreaf"
        ],
        "rewards": ["☘️ Forest Gem", "☠️ Venom Egg"]
    },
    "Crystal Ocean": {
        "image": "AgACAgUAAyEFAASo9k8fAAIEVWhOhHtaZUMX8VRvcnik9EfsEi35AALAwzEbDoJ4VrgzSGDQWNGBAQADAgADeQADNgQ",
        "element": "🌊 Water / ❄️ Ice",
        "enemies": [
            "Aquazor", "Aqualing",
            "Frostclaw", "Cryostrike", "Glacira", "Snowpiercer", "Shardbite"
        ],
        "rewards": ["🌊 Aqua Pearl", "❄️ Frozen Egg"]
    },
    "Radiant Mountains": {
        "image": "AgACAgUAAyEFAASgSr_SAAIbBmhOdeWYd_IqAQGAB14DG6L_h7mAAALGwjEbG2h5Vu35_3Wnr8mlAQADAgADeAADNgQ",
        "element": "🪨 Rock / 🌞 Light",
        "enemies": [
            "Terranox", "Duneblade", "Cragthorn", "Stonehorn",
            "Solarion", "Luxora"
        ],
        "rewards": ["🪨 Earth Core", "🌟 Sun Crystal"]
    }
}

# /region command
async def region(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type != "private":
            await update.message.reply_text(
                "⚠️ Please use this command in my *DM*.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 Use in DM", url="https://t.me/DragonDusk_bot")]
                ]),
                parse_mode="Markdown"
            )
            return

        buttons = [
            InlineKeyboardButton(region, callback_data=f"region_{region}")
            for region in REGIONS
        ]
        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

        await update.message.reply_photo(
            photo="https://graph.org/file/c004723e4bccec24367e9-6e2ef8f90315c9f35a.jpg",
            caption="🌍 *Explore Dragon Regions!*\n\nTap on any region to see the types of dragons and rewards you can discover there.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


# When a region button is clicked
async def show_region_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    region_name = query.data.replace("region_", "")

    # ✅ If the user clicked "Back", show the region list again
    if region_name == "back":
        return await region_back(update, context)

    region = REGIONS.get(region_name)

    if not region:
        try:
            await query.edit_message_caption("❌ Region not found.")
        except Exception:
            await query.message.reply_text("❌ Region not found.")  # fallback
        return

    # Format content
    element = region["element"]
    dragons = ", ".join(region["enemies"])
    rewards = ", ".join(region["rewards"])
    promo = "\n\n➤ [Powered By Nexorra Bots](https://t.me/Nexxxxxo_bots)"

    text = f"""
🏞️ *{region_name}*
Element: {element}

🐉 *Enemies Found:*
{dragons}

🎁 *Exploration Rewards:*
{rewards}
{promo}
""".strip()

    await query.edit_message_media(
        media=InputMediaPhoto(media=region["image"], caption=text, parse_mode="Markdown"),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Back to Regions", callback_data="region_back")
        ]])
    )


# Return to region list
async def region_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Rebuild horizontal 2x2 region button layout
    buttons = [
        InlineKeyboardButton(region, callback_data=f"region_{region}")
        for region in REGIONS
    ]
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    await query.edit_message_media(
        media=InputMediaPhoto(
            media="https://graph.org/file/c004723e4bccec24367e9-6e2ef8f90315c9f35a.jpg",
            caption="🌍 *Explore Dragon Regions!*\n\nTap on any region to see the types of dragons and rewards you can discover there.",
            parse_mode="Markdown"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


import difflib

REGION_GEM_COSTS = {
    "Volcanic Wastes": 25,
    "Everleaf Forest": 30,
    "Crystal Ocean": 50
}

TRAVEL_COST = 300
TRAVEL_XP = 50
DEFAULT_REGION = "Radiant Mountains"

async def travel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "⚠️ Please use this command in my *DM*.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Use in DM", url="https://t.me/DragonDusk_bot")]
            ]),
            parse_mode="Markdown"
        )
        return

    users = load_users()
    user_id = str(update.effective_user.id)
    user = users.get(user_id, {})
    user.setdefault("xp", 0)
    user.setdefault("gems", 0)
    user.setdefault("duskar", 0)
    user.setdefault("current_region", DEFAULT_REGION)

    if not context.args:
        await update.message.reply_text(
            "❌ Please use `/travel <region>` to travel.\nExample: `/travel Volcanic Wastes`",
            parse_mode="Markdown"
        )
        return

    input_region = " ".join(context.args).strip().lower()
    all_regions = list(REGIONS.keys())
    matched = difflib.get_close_matches(input_region, all_regions, n=1, cutoff=0.6)

    if not matched:
        await update.message.reply_text(
            "❌ Unknown region. Use `/region` to view available regions.",
            parse_mode="Markdown"
        )
        return

    region_name = matched[0]
    gem_cost = REGION_GEM_COSTS.get(region_name, 0)  # 0 for default free region

    if user["current_region"] == region_name:
        await update.message.reply_text(
            f"🗺️ You are already in *{region_name}*! Use */explore* to begin your journey.",
            parse_mode="Markdown"
        )
        return

    if user["duskar"] < TRAVEL_COST:
        await update.message.reply_text(
            "💰 You need at least *300 Duskar* to travel!",
            parse_mode="Markdown"
        )
        return

    if user["gems"] < gem_cost:
        await update.message.reply_text(
            f"💎 You need *{gem_cost} Gems* to travel to *{region_name}*!",
            parse_mode="Markdown"
        )
        return

    # Deduct costs
    user["duskar"] -= TRAVEL_COST
    user["gems"] -= gem_cost
    user["xp"] += TRAVEL_XP
    user["current_region"] = region_name
    users[user_id] = user
    save_users(users)

    region = REGIONS[region_name]
    image = region["image"]
    element = region["element"]

    await update.message.reply_photo(
        photo=image,
        caption=f"""
🧭 *You have traveled to:* `{region_name}`
🌋 *Region Element:* {element}
💸 *300 Duskar* & *{gem_cost} Gems* deducted
✨ *+50 Travel XP earned*

Get ready to */explore* and encounter dragons of this region!
➤ _Powered by [Nexorra Bots](https://t.me/NexorraBots)_
        """,
        parse_mode="Markdown",
    )



from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def whereami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "⚠️ Please use this command in my *DM*.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Use in DM", url="https://t.me/DragonDusk_bot")]
            ]),
            parse_mode="Markdown"
        )
        return

    users = load_users()
    user_id = str(update.effective_user.id)
    user = users.get(user_id, {})

    region_name = user.get("current_region")
    if not region_name:
        await update.message.reply_text(
            "🏡 You are currently at *Home*. Use `/travel <region>` to begin exploring!",
            parse_mode="Markdown"
        )
        return

    region = REGIONS.get(region_name)
    if not region:
        await update.message.reply_text(
            "❌ Your current region seems invalid. Use `/travel <region>` again.",
            parse_mode="Markdown"
        )
        return

    # Escape values for MarkdownV2
    safe_region_name = escape_markdown(region_name, version=2)
    safe_element = escape_markdown(region["element"], version=2)

    caption = (
        f"📍 *Current Region:* `{safe_region_name}`\n"
        f"🌋 *Element Type:* `{safe_element}`\n\n"
        "Explore using */explore* to find dragons and rewards\\."
    )

    await update.message.reply_photo(
        photo=region["image"],  # ✅ Dynamic image from region data
        caption=caption,
        parse_mode="MarkdownV2"
    )


import random

def load_dragons():
    with open("dragons.json", "r", encoding="utf-8") as f:
        return json.load(f)

import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram import Update

# Make sure REGIONS and load_dragons are already defined
# DRAGON_IMAGE is a static image used for all wild encounters

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ENCOUNTER_IMAGE = "AgACAgUAAyEFAASo9k8fAAIEZGhOhcihAoMTjhMHxsPujZ08AAHw9QACwsMxGw6CeFY_ctlq0yB86wEAAwIAA3kAAzYE"

# Start of the explore function
async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type != "private":
            await update.message.reply_text(
                "⚠️ Please use this command in my *DM*.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💬 Use in DM", url="https://t.me/DragonDusk_bot")]
                ]),
                parse_mode=ParseMode.MARKDOWN
            )
            return

        user_id = str(update.effective_user.id)
        users = load_users()
        DRAGONS = load_dragons()
        user = users.get(user_id, {})

        current_region = user.get("current_region")
        if not current_region:
            await update.message.reply_text("❌ You are not in any region.\nUse `/travel <region>` first.")
            return

        region = REGIONS.get(current_region)
        if not region or not region.get("enemies"):
            await update.message.reply_text("⚠️ No valid enemies found in this region.")
            return

        # Pick a random enemy from region and verify it's in DRAGONS
        enemy_name = next((name for name in random.sample(region["enemies"], len(region["enemies"])) if name in DRAGONS), None)
        if not enemy_name:
            await update.message.reply_text("⚠️ No valid enemy dragons found in this region.")
            return

        # === Boost enemy stats randomly without changing the DB ===
        base_enemy = DRAGONS[enemy_name]
        boosted_enemy = {
            "element": base_enemy["element"],
            "base_hp": int(base_enemy["base_hp"] * random.uniform(1.2, 1.5)),
            "moves": []
        }
        for move in base_enemy["moves"]:
            boosted_move = move.copy()
            boosted_move["power"] += random.randint(5, 20)
            boosted_enemy["moves"].append(boosted_move)

        # Save enemy for battle
        user["explore_enemy"] = {
            "name": enemy_name,
            "hp": boosted_enemy["base_hp"],
            "boosted_moves": boosted_enemy["moves"],
            "element": boosted_enemy["element"]
        }

        users[user_id] = user
        save_users(users)

        # === Dragon selection ===
        user_dragons = user.get("dragons", [])
        if not user_dragons:
            await update.message.reply_text("❌ You don't have any dragons. Use `/dragons` to check.")
            return

        buttons = []
        for i, d in enumerate(user_dragons):
            buttons.append([InlineKeyboardButton(f"{d['name']} (Lvl {d.get('level', 1)})", callback_data=f"select_pve_dragon|{i}")])

        markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_photo(
            photo=ENCOUNTER_IMAGE,
            caption=f"""🐉 *A wild {enemy_name} has appeared!*
    🌪️ *Element:* {boosted_enemy['element']}
    ❤️ *HP:* {boosted_enemy['base_hp']}

    Choose your dragon to fight:
    """,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=markup
        )


# ======= Select Dragon & Start PvE Battle =======
async def select_pve_dragon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    users = load_users()
    DRAGONS = load_dragons()
    user = users.get(user_id, {})
    dragon_index = int(query.data.split("|")[1])

    user_dragons = user.get("dragons", [])
    if dragon_index >= len(user_dragons):
        await query.edit_message_text("❌ Invalid dragon selection.")
        return

    selected = user_dragons[dragon_index]
    selected_name = selected.get("name")
    base_stats = DRAGONS.get(selected_name)
    enemy = user.get("explore_enemy")

    if not base_stats or not enemy:
        await query.edit_message_text("⚠️ Dragon or enemy data missing.")
        return

    user["pve_battle"] = {
        "enemy_name": enemy["name"],
        "enemy_hp": enemy["hp"],
        "user_dragon": {
            "name": selected_name,
            "level": selected.get("level", 1),
            "xp": selected.get("xp", 0),
            "element": base_stats["element"],
            "base_hp": base_stats["base_hp"],
            "moves": base_stats["moves"]
        },
        "user_hp": base_stats["base_hp"],
    }

    user["in_explore_battle"] = True
    users[user_id] = user
    save_users(users)

    await query.edit_message_caption(
        caption=f"⚔️ *Battle Started!*\n\n🆚 *{enemy['name']}* appears!\nUse your skills wisely — good luck!",
        parse_mode=ParseMode.MARKDOWN
    )

    await start_pve_battle_ui(update, context, user_id)

# ======= Show PvE Battle UI =======
async def start_pve_battle_ui(update, context, user_id):
    users = load_users()
    DRAGONS = load_dragons()
    user = users[user_id]
    battle = user.get("pve_battle")
    if not battle:
        return

    def hp_bar(hp, max_hp):
        percent = hp / max_hp
        return "█" * int(percent * 10) + "░" * (10 - int(percent * 10))

    enemy_name = battle["enemy_name"]
    enemy_data = DRAGONS.get(enemy_name)
    user_dragon = battle["user_dragon"]

    buttons = [[InlineKeyboardButton(move["name"], callback_data=f"pve_move|{move['name']}")] for move in user_dragon["moves"]]
    buttons.append([InlineKeyboardButton("🏃‍♂️ Flee", callback_data="pve_flee")])
    if battle["enemy_hp"] <= enemy_data["base_hp"] * 0.2 and not any(d["name"] == enemy_name for d in user.get("dragons", [])):
        buttons.append([InlineKeyboardButton("🎯 Tame", callback_data="pve_tame")])

    sent = await update.effective_message.reply_text(
        f"""╔══════🔥 PvE Battle 🔥══════╗

👤 {update.effective_user.first_name} 🆚 Wild {enemy_name}

🐲 {user_dragon['name']} — {user_dragon['element']}
❤️ {hp_bar(battle['user_hp'], user_dragon['base_hp'])} {battle['user_hp']}/{user_dragon['base_hp']}

🆚

🐉 {enemy_name} — {enemy_data['element']}
❤️ {hp_bar(battle['enemy_hp'], enemy_data['base_hp'])} {battle['enemy_hp']}/{enemy_data['base_hp']}

🎯 Your Turn — choose a move!
""",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

    user["pve_battle"]["message_id"] = sent.message_id
    users[user_id] = user
    save_users(users)

# ======= PvE Move Handler =======
async def pve_move_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()
    user = users.get(user_id, {})
    pve = user.get("pve_battle")
    if not pve or not user.get("in_explore_battle"):
        await query.edit_message_text("⚠️ No active battle.", parse_mode="Markdown")
        return

    move_name = query.data.split("|")[1]
    move = next((m for m in pve["user_dragon"]["moves"] if m["name"] == move_name), None)
    if not move:
        await query.answer("❌ Invalid move.")
        return

    # Damage enemy
    pve["enemy_hp"] = max(0, pve["enemy_hp"] - move.get("power", 0))
    if pve["enemy_hp"] == 0:
        user["duskar"] = user.get("duskar", 0) + 100
        user["xp"] = user.get("xp", 0) + 20
        msg = f"🏆 *Victory!* You defeated {pve['enemy_name']}!\n\n💰 +100 Duskar\n✨ +20 XP"

        if random.random() < 0.05:
            user["gems"] = user.get("gems", 0) + 20
            msg += "\n💎 *+20 Gems* (Lucky!)"

        user["explore_count"] = user.get("explore_count", 0) + 1
        if user["explore_count"] >= 50:
            user["explore_count"] = 0
            egg = random.choices(["Normal", "Rare", "Legendary", "Ultimate"], [0.6, 0.25, 0.1, 0.05])[0]
            user.setdefault("eggs", []).append({"type": egg, "xp": 0})
            msg += f"\n🥚 *You found a `{egg}` egg!*"

        user["in_explore_battle"] = False
        user.pop("pve_battle", None)
        user.pop("explore_enemy", None)
        users[user_id] = user
        save_users(users)

        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🐉 Explore Again", url="https://t.me/DragonDusk_bot?start=explore")]
        ]))
        return

    # Enemy attacks
    enemy = user.get("explore_enemy", {})
    enemy_moves = enemy.get("boosted_moves", [])
    enemy_dmg = random.choice(enemy_moves)["power"] if enemy_moves else 10
    pve["user_hp"] = max(0, pve["user_hp"] - enemy_dmg)

    if pve["user_hp"] <= 0:
        user["in_explore_battle"] = False
        user.pop("pve_battle", None)
        user.pop("explore_enemy", None)
        users[user_id] = user
        save_users(users)

        await query.edit_message_text(
            f"💀 *Defeat...*\nYour dragon fainted.\n\nUse /explore to try again.",
            parse_mode="Markdown"
        )
        return

    # Save and update UI
    users[user_id] = user
    save_users(users)
    await update_pve_ui(update, context, user_id)

# ======= PvE UI Update =======
async def update_pve_ui(update, context, user_id):
    users = load_users()
    user = users[user_id]
    pve = user["pve_battle"]
    enemy = user.get("explore_enemy", {})
    user_dragon = pve["user_dragon"]

    def hp_bar(hp, max_hp):
        percent = hp / max_hp
        return "█" * int(percent * 10) + "░" * (10 - int(percent * 10))

    buttons = [[InlineKeyboardButton(move["name"], callback_data=f"pve_move|{move['name']}")] for move in user_dragon["moves"]]
    buttons.append([InlineKeyboardButton("🏃‍♂️ Flee", callback_data="pve_flee")])
    if pve["enemy_hp"] <= enemy["hp"] * 0.2 and not any(d["name"] == enemy["name"] for d in user.get("dragons", [])):
        buttons.append([InlineKeyboardButton("🎯 Tame", callback_data="pve_tame")])

    try:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=pve["message_id"],
            text=f"""
╔══════🔥 PvE Battle 🔥══════╗

👤 {update.effective_user.first_name} 🆚 Wild {enemy["name"]}

🐲 {user_dragon['name']} — {user_dragon['element']}
❤️ {hp_bar(pve['user_hp'], user_dragon['base_hp'])} {pve['user_hp']}/{user_dragon['base_hp']}

🆚

🐉 {enemy['name']} — {enemy.get('element', '?')}
❤️ {hp_bar(pve['enemy_hp'], enemy['hp'])} {pve['enemy_hp']}/{enemy['hp']}

🎯 Your Turn — choose a move!
""",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
    except Exception as e:
        print("UI update failed:", e)

# ======= Tame =======
async def pve_tame(update, context):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()
    user = users[user_id]
    pve = user.get("pve_battle")
    enemy = user.get("explore_enemy")

    if enemy["hp"] * 0.2 < pve["enemy_hp"]:
        await query.answer("❌ Too strong to tame!", show_alert=True)
        return

    if any(d["name"] == enemy["name"] for d in user.get("dragons", [])):
        await query.message.reply_text("⚠️ You already own this dragon!")
        return

    if random.random() <= 0.7:
        template = load_dragons().get(enemy["name"], {})
        new_dragon = {
            "name": enemy["name"],
            "element": template.get("element", "Unknown"),
            "power": random.randint(40, 60),
            "physical_attack": random.randint(20, 30),
            "elemental_attack": random.randint(20, 30),
            "level": 1,
            "xp": 0,
            "base_hp": template.get("base_hp", 100),
            "current_hp": template.get("base_hp", 100),
        }
        user.setdefault("dragons", []).append(new_dragon)
        user["in_explore_battle"] = False
        user.pop("pve_battle", None)
        user.pop("explore_enemy", None)
        users[user_id] = user
        save_users(users)

        await query.edit_message_text(f"🎉 *Success!* You tamed {enemy['name']}!", parse_mode="Markdown")
    else:
        await query.answer("😓 Taming failed!", show_alert=True)

# ======= Flee =======
async def pve_flee(update, context):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()
    user = users[user_id]
    user["in_explore_battle"] = False
    user.pop("pve_battle", None)
    user.pop("explore_enemy", None)
    users[user_id] = user
    save_users(users)

    await query.edit_message_text("🏃‍♂️ *You fled the battle safely.*\nUse /explore to search again.", parse_mode="Markdown")