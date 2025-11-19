"""
API routes package.
"""

from fastapi import APIRouter

from . import generate, validate, export

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(generate.router, prefix="/generate", tags=["generate"])
api_router.include_router(validate.router, prefix="/validate", tags=["validate"])
api_router.include_router(export.router, prefix="/export", tags=["export"])

__all__ = ["api_router"]
