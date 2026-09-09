"""
AutoPay Schemas for Mandate Registration, Activation, and Recurring Deductions.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.autopay import MandateAuthType, MandateStatus


class CreateMandateRequest(BaseModel):
    auth_type: MandateAuthType = MandateAuthType.UPI
    max_amount: float = Field(500.00, ge=50.00, le=5000.00)
    vpa: Optional[str] = Field(None, description="UPI ID (e.g. member@okhdfcbank)")
    bank_name: Optional[str] = None


class MandateRead(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    gateway_mandate_id: str
    auth_type: MandateAuthType
    max_amount: float
    status: MandateStatus
    vpa: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_last_4: Optional[str] = None
    activated_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivateMandateRequest(BaseModel):
    gateway_mandate_id: str


class BatchDebitSummaryRead(BaseModel):
    event_id: uuid.UUID
    total_eligible_members: int
    autopay_active_count: int
    debited_count: int
    total_amount_debited: float
