"""
Welfare Event and Contribution Schemas.
"""
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.welfare import ContributionStatus, WelfareEventStatus


class WelfareEventCreate(BaseModel):
    deceased_member_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=255)
    death_date: date
    cause_of_death: Optional[str] = None
    death_certificate_url: Optional[str] = None


class WelfareEventRead(BaseModel):
    id: uuid.UUID
    deceased_member_id: uuid.UUID
    title: str
    death_date: date
    cause_of_death: Optional[str] = None
    death_certificate_url: Optional[str] = None
    target_amount: float
    collected_amount: float
    status: WelfareEventStatus
    created_by_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WelfareContributionRead(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    member_id: uuid.UUID
    amount: float
    status: ContributionStatus
    payment_method: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WelfareObligationRead(BaseModel):
    contribution_id: uuid.UUID
    event_id: uuid.UUID
    event_title: str
    deceased_member_name: str
    amount: float
    status: ContributionStatus
    created_at: datetime
