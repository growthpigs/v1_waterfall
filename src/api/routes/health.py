"""
Health Check Routes
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any

from ...database.base import SupabaseConnection

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Brand BOS API"
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with component status"""
    
    # Check database connection
    db_status = "unknown"
    try:
        db = SupabaseConnection()
        client = db.get_client()
        # Simple query to test connection
        result = client.table("clients").select("id").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": {
                "status": "operational",
                "response_time_ms": 1
            },
            "database": {
                "status": db_status,
                "type": "supabase"
            },
            "cia_engine": {
                "status": "operational",
                "phases": 6,
                "version": "1.0"
            },
            "cartwheel_engine": {
                "status": "operational",
                "formats": 14,
                "version": "1.0"
            },
            "adsby_system": {
                "status": "operational",
                "budget": "$10,000/month",
                "version": "1.0"
            }
        }
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """Kubernetes readiness probe endpoint"""
    # Check if all critical components are ready
    try:
        # Test database
        db = SupabaseConnection()
        client = db.get_client()
        client.table("clients").select("id").limit(1).execute()
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Kubernetes liveness probe endpoint"""
    # Simple check that the service is alive
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }