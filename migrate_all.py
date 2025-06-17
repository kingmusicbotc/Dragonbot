# migrate_all.py

import json
from db import save_json, update_user

# === Migrate users.json ===
try:
    with open("users.json", "r") as f:
        users = json.load(f)
    for uid, user_data in users.items():
        update_user(uid, user_data)
    print("✅ users.json migrated successfully.")
except Exception as e:
    print("❌ users.json migration failed:", e)

# === Migrate clans.json ===
try:
    with open("clans.json", "r") as f:
        clans = json.load(f)
    save_json("clans.json", clans)
    print("✅ clans.json migrated successfully.")
except Exception as e:
    print("❌ clans.json migration failed:", e)

# === Migrate group.json ===
try:
    with open("group.json", "r") as f:
        groups = json.load(f)
    save_json("group.json", groups)
    print("✅ group.json migrated successfully.")
except Exception as e:
    print("❌ group.json migration failed:", e)

# === Migrate battle.json ===
try:
    with open("battle.json", "r") as f:
        battle = json.load(f)
    save_json("battle.json", battle)
    print("✅ battle.json migrated successfully.")
except Exception as e:
    print("❌ battle.json migration failed:", e)

# === Migrate cooldowns.json ===
try:
    with open("cooldowns.json", "r") as f:
        cooldowns = json.load(f)
    save_json("cooldowns.json", cooldowns)
    print("✅ cooldowns.json migrated successfully.")
except Exception as e:
    print("❌ cooldowns.json migration failed:", e)

# === Migrate eggs.json ===
try:
    with open("eggs.json", "r") as f:
        eggs = json.load(f)
    save_json("eggs.json", eggs)
    print("✅ eggs.json migrated successfully.")
except Exception as e:
    print("❌ eggs.json migration failed:", e)

