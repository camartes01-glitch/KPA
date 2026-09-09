"""
Member and Nominee Schemas for Registration, Verification, and Digital Cards.
"""
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.member import MemberStatus


class NomineeCreate(BaseModel):
    name: str = Field(..., max_length=150)
    relationship_to_member: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=20)
    dob: Optional[date] = None
    aadhaar_last_4: Optional[str] = Field(None, min_length=4, max_length=4)
    bank_account_no: Optional[str] = Field(None, max_length=50)
    bank_ifsc: Optional[str] = Field(None, max_length=20)
    bank_name: Optional[str] = Field(None, max_length=100)
    is_primary: bool = True


class NomineeRead(NomineeCreate):
    id: uuid.UUID
    member_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class MemberRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    father_or_spouse_name: Optional[str] = Field(None, max_length=150)
    gender: str = Field(..., max_length=20)
    dob: date
    blood_group: Optional[str] = Field(None, max_length=10)
    studio_name: Optional[str] = Field(None, max_length=150)
    experience_years: int = Field(0, ge=0, le=70)
    photo_url: Optional[str] = None
    address_line: Optional[str] = None
    pincode: Optional[str] = Field(None, max_length=10)
    district_id: uuid.UUID
    taluka_id: uuid.UUID
    nominee: NomineeCreate


class MemberRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    membership_no: Optional[str] = None
    full_name: str
    father_or_spouse_name: Optional[str] = None
    gender: str
    dob: date
    blood_group: Optional[str] = None
    studio_name: Optional[str] = None
    experience_years: int
    photo_url: Optional[str] = None
    address_line: Optional[str] = None
    pincode: Optional[str] = None
    district_id: uuid.UUID
    taluka_id: uuid.UUID
    status: MemberStatus
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberWithNomineesRead(MemberRead):
    nominees: List[NomineeRead] = []

    model_config = ConfigDict(from_attributes=True)


class MemberApprovalRequest(BaseModel):
    pass  # Approves application and generates membership number


class MemberRejectionRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class DigitalCardResponse(BaseModel):
    membership_no: str
    member_name: str
    district_name: str
    taluka_name: str
    blood_group: Optional[str] = None
    status: str
    issue_date: str
    qr_data: str
    qr_code_base64: str
