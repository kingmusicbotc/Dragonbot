# db.py

from pymongo import MongoClient
import os

# === MongoDB Connection ===
# You can set MONGO_URI as an environment variable on Render or Replit
MONGO_URI = os.getenv("MONGO_URI") or "mongodb+srv://grovvewm:grovvewm@cluster0.5aeo13r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["dragon_dusk"]

# === Mapping JSON Filenames to Mongo Collections ===
collection_map = {
    "users.json": db["users"],
    "group.json": db["groups"],
    "clans.json": db["clans"]
}

# === Load JSON-style data from MongoDB ===
def load_json(filename):
    col = collection_map.get(filename)
    data = {}
    for doc in col.find():
        doc_id = str(doc["_id"])
        doc.pop("_id", None)
        data[doc_id] = doc
    return data

# === Save JSON-style data to MongoDB ===
def save_json(filename, data):
    col = collection_map.get(filename)
    col.delete_many({})  # Clear all existing entries
    for key, doc in data.items():
        doc["_id"] = key  # Use key as MongoDB document ID
        col.insert_one(doc)
