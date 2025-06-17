from pymongo import MongoClient
import os

# === MongoDB Connection ===
MONGO_URI = os.getenv("MONGO_URI") or "mongodb+srvvewm:grovvewm@cluster0.5aeo13r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["dragon_dusk"]

# === Mapping JSON Filenames to MongoDB Collections ===
collection_map = {
    "users.json": db["users"],
    "group.json": db["groups"],
    "clans.json": db["clans"],
    "battle.json": db["battles"],
    "cooldowns.json": db["cooldowns"],
    "eggs.json": db["eggs"]
}

# === Load entire collection into dictionary ===
def load_json(filename):
    col = collection_map.get(filename)
    data = {}
    if col:
        for doc in col.find():
            doc_id = str(doc["_id"])
            doc.pop("_id", None)
            data[doc_id] = doc
    return data

# === Save entire dictionary to collection ===
def save_json(filename, data):
    col = collection_map.get(filename)
    if col:
        col.delete_many({})
        for key, value in data.items():
            value["_id"] = key
            col.insert_one(value)

# === Update a single user document (for users.json only) ===
def update_user(user_id, user_data):
    users_col = db["users"]
    users_col.update_one({"_id": str(user_id)}, {"$set": user_data}, upsert=True)
