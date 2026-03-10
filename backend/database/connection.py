"""
Indian Currency Detection - Database Module
MongoDB connection and operations
"""
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[settings.DB_NAME]
        # Verify connection
        await client.admin.command("ping")
        print(f"✅ Connected to MongoDB: {settings.DB_NAME}")

        # Create indexes
        await db.users.create_index("email", unique=True)
        await db.detection_history.create_index("user_id")
        await db.detection_history.create_index("date")
        print("✅ Database indexes created")
    except Exception as e:
        print(f"⚠️ MongoDB connection warning: {e}")
        print("    → Continue in demo mode (no data persistence)")
        # Don't raise — allow app to start in demo mode


async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        try:
            client.close()
            print("🔌 MongoDB connection closed")
        except Exception as e:
            print(f"⚠️ Error closing MongoDB: {e}")


def get_database():
    """Get database instance"""
    return db
