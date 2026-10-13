from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["open", "in_progress", "resolved"]
EquipmentStatus = Literal["operational", "attention", "offline"]


class EquipmentCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32, pattern=r"^[A-Za-z0-9-]+$")
    name: str = Field(min_length=2, max_length=120)
    room: str = Field(min_length=2, max_length=60)
    category: str = Field(min_length=2, max_length=60)


class EquipmentRead(EquipmentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: EquipmentStatus


class IncidentCreate(BaseModel):
    equipment_id: int
    title: str = Field(min_length=4, max_length=160)
    detail: str = Field(default="", max_length=2000)
    severity: Severity = "medium"
    reported_by: str = Field(min_length=2, max_length=80)


class IncidentUpdate(BaseModel):
    status: IncidentStatus


class IncidentRead(IncidentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: IncidentStatus
    created_at: datetime
    resolved_at: datetime | None


class SummaryRead(BaseModel):
    equipment_total: int
    operational: int
    attention: int
    offline: int
    open_incidents: int
    resolved_incidents: int
