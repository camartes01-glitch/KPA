"""
Geographic schemas for Districts and Talukas.
"""
import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TalukaBase(BaseModel):
    name_en: str = Field(..., max_length=100)
    name_kn: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)


class TalukaCreate(TalukaBase):
    district_id: uuid.UUID


class TalukaRead(TalukaBase):
    id: uuid.UUID
    district_id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DistrictBase(BaseModel):
    name_en: str = Field(..., max_length=100)
    name_kn: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)


class DistrictCreate(DistrictBase):
    pass


class DistrictRead(DistrictBase):
    id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DistrictWithTalukasRead(DistrictRead):
    talukas: List[TalukaRead] = []

    model_config = ConfigDict(from_attributes=True)
