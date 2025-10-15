import sqlite3
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json

# Load env variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "courier_app")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
couriers_collection = db["couriers"]

# Connect to old SQLite
sqlite_file = "couriers.db"
if not os.path.exists(sqlite_file):
    print("❌ couriers.db not found. Place it in this folder first.")
    exit()

conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

# Fetch all couriers
cursor.execute("SELECT * FROM couriers")
cols = [col[0] for col in cursor.description]
rows = cursor.fetchall()

print(f"📦 Found {len(rows)} couriers in SQLite.")

for row in rows:
    doc = dict(zip(cols, row))

    # Handle JSON strings for rates, if any
    if "rates" in doc and isinstance(doc["rates"], str):
        try:
            doc["rates"] = json.loads(doc["rates"])
        except Exception:
            doc["rates"] = {}

    # Convert numeric strings
    for key, val in doc.items():
        if isinstance(val, str):
            try:
                if "." in val:
                    doc[key] = float(val)
                else:
                    doc[key] = int(val)
            except Exception:
                pass

    # Insert or update existing courier
    couriers_collection.update_one({"name": doc["name"]}, {"$set": doc}, upsert=True)

print("✅ Migration complete. All couriers moved to MongoDB.")
conn.close()
client.close()
