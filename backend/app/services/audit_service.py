import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import AuditLogEntry

class AuditTrailService:
    """
    Step 10: Audit Trail Service.
    Logs every single pipeline transaction (Step 2 to Step 9) with exact timestamps,
    actors, and payloads to ensure complete auditability and non-repudiation.
    """

    def __init__(self):
        self._logs: List[AuditLogEntry] = []

    def log_event(
        self,
        bidder_id: str,
        step: str,
        actor: str,
        action_type: str,
        details: Dict[str, Any],
        notes: Optional[str] = None
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            log_id=f"LOG-{uuid.uuid4().hex[:10].upper()}",
            timestamp=datetime.utcnow(),
            bidder_id=bidder_id,
            step=step,
            actor=actor,
            action_type=action_type,
            details=details,
            notes=notes
        )
        self._logs.append(entry)
        return entry

    def get_logs_for_bidder(self, bidder_id: str) -> List[AuditLogEntry]:
        return [entry for entry in self._logs if entry.bidder_id == bidder_id]

    def get_all_logs(self) -> List[AuditLogEntry]:
        return sorted(self._logs, key=lambda x: x.timestamp, reverse=True)

# Global singleton instance for the prototype
audit_trail = AuditTrailService()
