"""Utility script to list MongoDB databases and collections."""

import asyncio

from pymongo import AsyncMongoClient

from puchamon.shared.infrastructure.config import settings


async def list_dbs():
    """List all databases and their collections in the configured MongoDB."""
    client = AsyncMongoClient(host=settings.DATABASE_URI)
    dbs = await client.list_database_names()
    print(f"Databases: {dbs}")

    for db_name in dbs:
        db = client[db_name]
        collections = await db.list_collection_names()
        print(f"DB: {db_name}, Collections: {collections}")

if __name__ == "__main__":
    asyncio.run(list_dbs())
