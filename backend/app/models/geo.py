"""
Geographic models — Karnataka Districts and Talukas.
Supports bilingual English and Kannada names with hierarchical relationships.
"""
import uuid
from typing import List

from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class District(BaseModel):
    """District in Karnataka (31 official districts)."""
    __tablename__ = "districts"

    name_en: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name_kn: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    talukas: Mapped[List["Taluka"]] = relationship(
        "Taluka",
        back_populates="district",
        cascade="all, delete-orphan",
        order_by="Taluka.name_en",
    )


class Taluka(BaseModel):
    """Taluka / Sub-district within a Karnataka District."""
    __tablename__ = "talukas"

    district_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("districts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name_en: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    name_kn: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    district: Mapped["District"] = relationship("District", back_populates="talukas")
