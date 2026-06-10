import databases
from sqlalchemy import create_engine, MetaData

DATABASE_URL = "sqlite:///./test.db"  # Update this if your database is not SQLite

database = databases.Database(DATABASE_URL)
metadata = MetaData()

class DatabaseClient:
    def __init__(self, database_instance=None):
        self.database = database_instance or database

    async def connect(self):
        """
        Connect to the database. Should be called during application startup.
        """
        await self.database.connect()

    async def disconnect(self):
        """
        Disconnect from the database. Should be called during application shutdown.
        """
        await self.database.disconnect()

    async def fetch_one(self, query: str, values: dict):
        """
        Fetch a single record from the database using a query and values.
        """
        return await self.database.fetch_one(query=query, values=values)
    
    async def fetch_all(self, query: str, values: dict = None):
        """
        Fetch multiple records from the database using a query and values.
        """
        return await self.database.fetch_all(query=query, values=values or {})

