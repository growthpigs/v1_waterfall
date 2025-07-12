"""
Brand BOS FastAPI Application
Main API entry point for CIA, Cartwheel, and Adsby systems
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from .routes import cia, cartwheel, adsby, health
from ..database.base import SupabaseConnection
from ..config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    Initialize resources on startup, cleanup on shutdown
    """
    # Startup
    logger.info("Starting Brand BOS API...")
    
    # Initialize database connection
    try:
        db = SupabaseConnection()
        app.state.db = db.get_client()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise
    
    # Initialize other resources as needed
    logger.info("Brand BOS API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Brand BOS API...")
    # Cleanup resources if needed


# Create FastAPI app
app = FastAPI(
    title="Brand BOS API",
    description="Business Operating System for automated marketing intelligence and operations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(cia.router, prefix="/api/v1/cia", tags=["cia"])
app.include_router(cartwheel.router, prefix="/api/v1/cartwheel", tags=["cartwheel"])
app.include_router(adsby.router, prefix="/api/v1/adsby", tags=["adsby"])

# Analytics integration routes
try:
    from .routes import analytics
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
except ImportError as e:
    logger.warning(f"Analytics routes not available: {e}")
    pass

# Scheduling integration routes
try:
    from .routes import scheduling
    app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])
except ImportError as e:
    logger.warning(f"Scheduling routes not available: {e}")
    pass

# Workflow orchestration routes
try:
    from .routes import workflow
    app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])
except ImportError as e:
    logger.warning(f"Workflow routes not available: {e}")
    pass


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Brand BOS API",
        "version": "1.0.0",
        "status": "operational",
        "systems": {
            "cia": "Central Intelligence Arsenal",
            "cartwheel": "Content Multiplication Engine",
            "adsby": "Traffic Amplification System"
        },
        "documentation": "/docs"
    }


@app.get("/api/v1/status")
async def system_status():
    """Get overall system status"""
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "operational",
        "systems": {
            "cia": {
                "status": "operational",
                "description": "6-phase intelligence analysis"
            },
            "cartwheel": {
                "status": "operational",
                "description": "12+ content format generation"
            },
            "adsby": {
                "status": "operational",
                "description": "$10k ad grant optimization"
            }
        },
        "database": {
            "status": "connected" if hasattr(app.state, 'db') else "disconnected"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn for development
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )