from typing import List
from .audit_client import AuditServiceClient
from ..models.task import Event


class TaskHistoryService:
    def __init__(self):
        self.audit_client = AuditServiceClient()

    async def get_task_history(self, task_id: str) -> List[Event]:
        """
        Get the complete history of events for a specific task.
        """
        return await self.audit_client.get_task_history(task_id)