#app/schemas/audit_log.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: int


class AuditLogCreate(AuditLogBase):
    user_id: int


class AuditLogRead(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
