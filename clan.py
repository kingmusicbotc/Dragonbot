import json, os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from db import load_json, save_json


CLAN_FILE = "clans.json"
USER_FILE = "users.json"



async def createclan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    user_name = user.full_name

    clans = load_clans()
    users = load_users()

    if user_id not in users:
        await update.message.reply_text(
            "❌ You must register with /start first."
        )
        return

    # Check if user is already in a clan
    for clan in clans.values():
        if user_id in clan["members"]:
            await update.message.reply_text(
                "⚔️ <b>You’re already in a clan!</b>\n"
                "Leave your current clan to create a new one.",
                parse_mode=ParseMode.HTML
            )
            return

    # Require a name
    if len(context.args) < 1:
        await update.message.reply_text(
            "🛡️ <b>Usage:</b> <code>/createclan &lt;clan_name&gt;</code>\n"
            "✨ Example: <code>/createclan Shadow Reapers</code>",
            parse_mode=ParseMode.HTML
        )
        return

    clan_name = " ".join(context.args)

    if clan_name in clans:
        await update.message.reply_text(
            f"⚠️ <b>Clan</b> <code>{clan_name}</code> <b>already exists.</b>\n"
            "Try a different name or use /joinclan.",
            parse_mode=ParseMode.HTML
        )
        return

    # Check Duskar balance
    if users[user_id].get("duskar", 0) < 2000:
        await update.message.reply_text(
            f"💸 <b>Insufficient Duskar!</b>\n"
            f"You need <b>2000 Duskar</b> to form a clan.\n"
            f"💰 Current Balance: <code>{users[user_id].get('duskar', 0)} Duskar</code>",
            parse_mode=ParseMode.HTML
        )
        return

    # Deduct Duskar
    users[user_id]["duskar"] -= 2000
    save_users(users)

    # Create clan
    clans[clan_name] = {
        "leader": user_id,
        "members": [user_id],
        "level": 1,
        "wins": 0,
        "losses": 0,
        "wars": []
    }
    save_clans(clans)

    await update.message.reply_text(
        f"🏰 <b>Clan Formed Successfully!</b>\n\n"
        f"👑 Leader: <a href='tg://user?id={user_id}'>{user_name}</a>\n"
        f"📛 Name: <code>{clan_name}</code>\n"
        f"📈 Level: 1\n"
        f"💸 Cost: 2000 Duskar deducted\n\n"
        f"🔥 Let the legacy of <b>{clan_name}</b> begin!",
        parse_mode=ParseMode.HTML
    )

async def joinclan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    user_name = user.full_name

    clans = load_clans()
    users = load_users()

    if user_id not in users:
        await update.message.reply_text(
            "❌ You must register first using /start."
        )
        return

    # Already in a clan?
    for clan_name, clan_data in clans.items():
        if user_id in clan_data["members"]:
            await update.message.reply_text(
                f"⚔️ <b>You’re already a member of</b> <code>{clan_name}</code>.\n"
                "Leave your current clan to join a new one.",
                parse_mode=ParseMode.HTML
            )
            return

    # Require clan name
    if len(context.args) < 1:
        await update.message.reply_text(
            "📛 <b>Usage:</b> <code>/joinclan &lt;clan_name&gt;</code>\n"
            "✨ Example: <code>/joinclan Dragon Fangs</code>",
            parse_mode=ParseMode.HTML
        )
        return

    clan_name = " ".join(context.args)

    if clan_name not in clans:
        await update.message.reply_text(
            f"❌ <b>No clan found with name</b> <code>{clan_name}</code>.",
            parse_mode=ParseMode.HTML
        )
        return

    # Add user to clan
    clans[clan_name]["members"].append(user_id)
    save_clans(clans)

    await update.message.reply_text(
        f"✅ <b>You’ve joined the clan!</b>\n"
        f"🏰 <code>{clan_name}</code>\n"
        f"👑 Welcome, <b>{user_name}</b>!",
        parse_mode=ParseMode.HTML
    )

async def myclan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    clans = load_clans()
    found_clan = None
    for clan_name, clan_data in clans.items():
        if user_id in clan_data["members"]:
            found_clan = (clan_name, clan_data)
            break

    if not found_clan:
        await update.message.reply_text(
            "❌ <b>You are not in a clan yet.</b>\nUse /createclan or /joinclan to get started.",
            parse_mode=ParseMode.HTML
        )
        return

    clan_name, clan = found_clan
    members_text = ""
    for member_id in clan["members"]:
        try:
            member = await context.bot.get_chat(member_id)
            member_name = f"<a href='tg://user?id={member_id}'>{member.full_name}</a>"
            if member_id == clan["leader"]:
                members_text += f"👤 {member_name} 👑\n"
            else:
                members_text += f"👤 {member_name}\n"
        except:
            # Fallback if user info can't be fetched
            if member_id == clan["leader"]:
                members_text += f"👤 User <code>{member_id}</code> 👑\n"
            else:
                members_text += f"👤 User <code>{member_id}</code>\n"

    await update.message.reply_text(
        f"🏰 <b>Clan Overview</b>\n\n"
        f"📛 <b>Name:</b> <code>{clan_name}</code>\n"
        f"📈 <b>Level:</b> {clan['level']}\n"
        f"🥇 <b>Wins:</b> {clan['wins']}\n"
        f"🥈 <b>Losses:</b> {clan['losses']}\n\n"
        f"👥 <b>Members:</b>\n{members_text}",
        parse_mode=ParseMode.HTML
    )

async def leaveclan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    clans = load_clans()

    for clan_name, clan_data in clans.items():
        if user_id in clan_data["members"]:
            if clan_data["leader"] == user_id:
                await update.message.reply_text(
                    "👑 <b>You are the leader of this clan!</b>\n"
                    "Transfer leadership or disband the clan before leaving.",
                    parse_mode=ParseMode.HTML
                )
                return

            # Remove member from clan
            clan_data["members"].remove(user_id)
            save_clans(clans)

            await update.message.reply_text(
                f"👋 <b>You have successfully left the clan</b> <code>{clan_name}</code>.",
                parse_mode=ParseMode.HTML
            )
            return

    await update.message.reply_text(
        "❌ <b>You’re not part of any clan.</b>\n"
        "Use /joinclan or /createclan to get started.",
        parse_mode=ParseMode.HTML
    )

# /disbandclan – Disband your clan (Owner only)
async def disbandclan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    clans = load_clans()
    users = load_users()

    user_clan = None
    for name, clan in clans.items():
        if user_id == clan["leader"]:
            user_clan = name
            break

    if not user_clan:
        await update.message.reply_text(
            "❌ <b>You are not the leader of any clan.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    # Remove all members from clan
    del clans[user_clan]
    save_clans(clans)

    await update.message.reply_text(
        f"⚠️ <b>Clan Disbanded!</b>\n\n"
        f"The clan <code>{user_clan}</code> has been permanently removed.\n"
        f"All members are now clanless.",
        parse_mode=ParseMode.HTML
    )

# clan.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json
import os

CLANS_FILE = "clans.json"
BATTLES_FILE = "battle.json"

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

async def clanchallenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[LOG] /clanchallenge triggered")

    user_id = str(update.effective_user.id)
    print("[LOG] User ID:", user_id)

    clans = load_json(CLANS_FILE)
    print("[LOG] Clans loaded")

    battle_data = load_json(BATTLES_FILE)
    print("[LOG] Battle data loaded")

    if not context.args:
        print("[LOG] No args given")
        await update.message.reply_text("❌ Usage: /clanchallenge <clan_name>")
        return

    challenger_clan = None
    for name, data in clans.items():
        print(f"[LOG] Checking clan: {name}, Members: {data.get('members', [])}")
        if user_id in data.get("members", []):
            challenger_clan = name
            print(f"[LOG] Found user's clan: {challenger_clan}")
            break

    if not challenger_clan:
        print("[LOG] User is not in any clan")
        await update.message.reply_text("❌ You are not part of any clan.")
        return

    input_name = " ".join(context.args).lower()
    print("[LOG] Target input name:", input_name)

    clan_name_map = {k.lower(): k for k in clans}
    print("[LOG] Clan name map:", clan_name_map)

    if input_name not in clan_name_map:
        print("[LOG] Target clan not found")
        await update.message.reply_text("❌ Target clan does not exist.")
        return

    target_clan = clan_name_map[input_name]
    print(f"[LOG] Target clan resolved: {target_clan}")

    if target_clan == challenger_clan:
        print("[LOG] User challenged own clan")
        await update.message.reply_text("❌ You cannot challenge your own clan.")
        return

    if "clan_wars" not in battle_data:
        battle_data["clan_wars"] = []

    for war in battle_data["clan_wars"]:
        if war["challenger"] == challenger_clan or war["target"] == challenger_clan:
            print("[LOG] Challenger clan already in war")
            await update.message.reply_text("⚠️ Your clan is already involved in a war.")
            return
        if war["challenger"] == target_clan or war["target"] == target_clan:
            print("[LOG] Target clan already in war")
            await update.message.reply_text("⚠️ The target clan is already in a war.")
            return

    war_entry = {
        "challenger": challenger_clan,
        "target": target_clan,
        "status": "pending",
        "rounds": []
    }

    battle_data["clan_wars"].append(war_entry)
    save_json(BATTLES_FILE, battle_data)
    print("[LOG] War entry added")

    target_owner_id = clans[target_clan]["leader"]
    print(f"[LOG] Target clan owner ID: {target_owner_id}")

    accept_button = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Accept War", callback_data=f"accept_clanwar|{challenger_clan}|{target_clan}")
    ]])

    try:
        await context.bot.send_message(
            chat_id=int(target_owner_id),
            text=(
                f"🏹 *Clan War Request!*\n\n"
                f"🔥 *{challenger_clan}* has challenged your clan *{target_clan}* to a 5-round clan war!\n\n"
                f"Do you accept this challenge?"
            ),
            reply_markup=accept_button,
            parse_mode="Markdown"
        )
        print("[LOG] DM sent successfully")
        await update.message.reply_text(f"✅ Challenge sent to {target_clan}'s leader.")
    except Exception as e:
        await update.message.reply_text("⚠️ Could not send DM to the target clan leader.")
        print(f"[ERROR] DM failed: {e}")

from telegram import Update
from telegram.ext import ContextTypes
import random

async def accept_clanwar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    if len(data) != 3:
        await query.edit_message_text("❌ Invalid war request.")
        return

    _, challenger_clan, target_clan = data
    user_id = str(query.from_user.id)

    clans = load_json(CLANS_FILE)
    battles = load_json(BATTLES_FILE)

    # 🔒 Ensure user is leader of target clan
    if clans.get(target_clan, {}).get("leader") != user_id:
        await query.edit_message_text("❌ You are not authorized to accept this challenge.")
        return

    for war in battles.get("clan_wars", []):
        if war["challenger"] == challenger_clan and war["target"] == target_clan and war["status"] == "pending":
            # ✅ War found, now check if both clans have at least 5 members
            challenger_members = clans.get(challenger_clan, {}).get("members", [])
            target_members = clans.get(target_clan, {}).get("members", [])

            if len(challenger_members) < 5 or len(target_members) < 5:
                await query.edit_message_text("❌ Both clans must have at least 5 members to start the war.")
                return

            # 🎯 Randomly pick 5 members from each side
            war["challenger_players"] = random.sample(challenger_members, 5)
            war["target_players"] = random.sample(target_members, 5)
            war["current_round"] = 0
            war["challenger_wins"] = 0
            war["target_wins"] = 0
            war["status"] = "in_progress"

            save_json(BATTLES_FILE, battles)

            await query.edit_message_text(
                f"⚔️ Clan War has begun between *{challenger_clan}* and *{target_clan}*!\n\n"
                f"🔥 First battle is about to start...",
                parse_mode="Markdown"
            )

            # ✅ Start the first round
            await start_next_clan_round(context, war)
            return

    await query.edit_message_text("❌ Could not find the war request.")

async def start_next_clan_round(context: ContextTypes.DEFAULT_TYPE, war: dict):
    round_no = war["current_round"]

    if round_no >= 5:
        await finish_clan_war(context, war)
        return

    player1_id = war["challenger_players"][round_no]
    player2_id = war["target_players"][round_no]

    # 🔥 Announce the round
    await context.bot.send_message(
        chat_id=war["group_id"],
        text=f"🛡️ Round {round_no + 1} of Clan War Begins!\n\n"
             f"🔴 *{player1_id}* vs 🔵 *{player2_id}*",
        parse_mode="Markdown"
    )

    # ☑️ Start battle here (reusing your 1v1 dragon battle logic)
    # You’ll need to simulate or hook into your existing challenge mechanism programmatically

async def finish_clan_round(winner_id: str, war_data: dict, context: ContextTypes.DEFAULT_TYPE):
    # Determine which side won
    if winner_id in war_data["challenger_players"]:
        war_data["challenger_wins"] += 1
    elif winner_id in war_data["target_players"]:
        war_data["target_wins"] += 1

    war_data["current_round"] += 1
    save_json(BATTLES_FILE, load_json(BATTLES_FILE))  # optional full reload if needed
    save_json(BATTLES_FILE, battles)

    if war_data["current_round"] >= 5:
        await finish_clan_war(context, war_data)
    else:
        await start_next_clan_round(context, war_data)

async def finish_clan_war(context: ContextTypes.DEFAULT_TYPE, war_data: dict):
    battles = load_json(BATTLES_FILE)
    clans = load_json(CLANS_FILE)

    challenger = war_data["challenger"]
    target = war_data["target"]
    group_id = war_data["group_id"]

    c_wins = war_data["challenger_wins"]
    t_wins = war_data["target_wins"]

    result_text = ""
    if c_wins > t_wins:
        clans[challenger]["wins"] += 1
        clans[challenger]["level"] += 1
        clans[target]["losses"] += 1
        result_text = f"🏆 *{challenger}* wins the Clan War!\n🎉 Reward: +500 Duskar, +10 Gems"
    elif t_wins > c_wins:
        clans[target]["wins"] += 1
        clans[target]["level"] += 1
        clans[challenger]["losses"] += 1
        result_text = f"🏆 *{target}* wins the Clan War!\n🎉 Reward: +500 Duskar, +10 Gems"
    else:
        result_text = "🤝 It's a draw! No clan levels up this time."

    war_data["status"] = "finished"
    save_json(BATTLES_FILE, battles)
    save_json(CLANS_FILE, clans)

    await context.bot.send_message(
        chat_id=group_id,
        text=f"⚔️ Clan War Finished!\n\nFinal Score:\n*{challenger}* - {c_wins} 🆚 {t_wins} - *{target}*\n\n{result_text}",
        parse_mode="Markdown"
    )
