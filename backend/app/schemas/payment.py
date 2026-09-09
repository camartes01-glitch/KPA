"""
Payment Schemas for Order Creation, Signature Verification, and Receipts.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class CreateOrderRequest(BaseModel):
    contribution_id: uuid.UUID


class OrderResponse(BaseModel):
    order_id: str
    amount: float
    amount_paise: int
    currency: str
    receipt_no: str
    key_id: str


class VerifyPaymentRequest(BaseModel):
    gateway_order_id: str
    gateway_payment_id: str
    signature: str


class PaymentReceiptRead(BaseModel):
    id: uuid.UUID
    receipt_no: str
    amount: float
    currency: str
    status: PaymentStatus
    payment_method: Optional[str] = None
    gateway_order_id: str
    gateway_payment_id: Optional[str] = None
    member_name: str
    membership_no: Optional[str] = None
    event_title: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
