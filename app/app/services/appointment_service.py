from app.db.db_client import DatabaseClient
from fastapi import Depends

class AppointmentService:
    def __init__(self, db_client: DatabaseClient = Depends(DatabaseClient)):
        self.db_client = db_client

    async def get_appointment_by_id(self, appointment_id: int) -> dict:
        """
        Retrieve a single appointment by its ID from the database.
        """
        query = "SELECT id, user, time, status FROM appointments WHERE id = :id"
        values = {"id": appointment_id}
        row = await self.db_client.fetch_one(query=query, values=values)
        if row:
            return {"id": row["id"], "user": row["user"], "time": row["time"], "status": row["status"]}
        return None
