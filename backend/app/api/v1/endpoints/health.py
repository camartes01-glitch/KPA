"""
Health check endpoints — used by load balancers, monitoring, and Docker healthchecks.
"""
import time
from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

_start_time = time.time()


@router.get(
    "",
    summary="Application health check",
    response_description="Service status and metadata",
)
async def health_check():
    """
    Basic health check — returns service info without DB dependency.
    Used by load balancers for liveness probes.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "uptime_seconds": round(time.time() - _start_time, 2),
    }


@router.get(
    "/db",
    summary="Database connectivity check",
    response_description="Database connection status",
)
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """
    Deep health check — verifies database connectivity.
    Used for readiness probes.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        db_status: Literal["ok", "error"] = "ok"
    except Exception as e:
        db_status = "error"
        return {
            "status": "degraded",
            "database": db_status,
            "error": str(e),
        }

    return {
        "status": "ok",
        "database": db_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }
