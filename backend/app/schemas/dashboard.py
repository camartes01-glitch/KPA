"""
Dashboard and Reporting Schemas for Role-Aware Analytics and Metrics.
"""
from typing import List, Optional
from pydantic import BaseModel


class DistrictMetricItem(BaseModel):
    district_name: str
    total_members: int
    approved_members: int
    total_collected: float
    pending_dues: float


class DashboardMetricsRead(BaseModel):
    total_members: int
    active_members: int
    pending_approvals: int
    active_welfare_events: int
    total_welfare_target: float
    total_collected_today: float
    total_collected_monthly: float
    total_pending_dues: float
    autopay_active_members: int
    district_breakdown: Optional[List[DistrictMetricItem]] = None
