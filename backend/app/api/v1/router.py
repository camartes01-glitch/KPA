"""
V1 API Router — registers all endpoint modules.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit_logs,
    auth,
    autopay,
    dashboard,
    geo,
    health,
    members,
    notifications,
    payments,
    reports,
    welfare,
)

api_router = APIRouter()

# ── Core ──────────────────────────────────────────────────────────────────────
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(geo.router, prefix="/geo", tags=["Geographic"])
api_router.include_router(members.router, prefix="/members", tags=["Members"])
api_router.include_router(welfare.router, prefix="/welfare-events", tags=["Welfare Events"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(autopay.router, prefix="/autopay", tags=["AutoPay"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])
