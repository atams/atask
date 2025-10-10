"""
atask - AURA Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from atams.db import init_database
from atams.logging import setup_logging_from_settings
from atams.middleware import RequestIDMiddleware
from atams.exceptions import setup_exception_handlers

from app.core.config import settings
from app.api.v1.api import api_router

# Setup logging
setup_logging_from_settings(settings)

# Initialize database
init_database(settings.DATABASE_URL, settings.DEBUG)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="AURA Application with Atlas SSO Integration",
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
)

# Request ID middleware
app.add_middleware(RequestIDMiddleware)

# Exception handlers
setup_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """API Root - Basic information"""
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "ok"}
