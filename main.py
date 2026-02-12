"""Main FastAPI application"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from datetime import datetime
import time
import uuid
from app.core.config import get_settings
from app.core.logger import get_logger
from app.db.database import init_db
from app.api import keys, events, analytics, audit, health, websocket

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context"""
    # Startup
    logger.info("Starting application...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Event-Driven Analytics & Audit API with async ingestion, rate limiting, and real-time metrics",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware for request/response logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add request ID to state
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        
        # Add request ID to headers
        response.headers["X-Request-ID"] = request_id
        
        # Log request details
        duration = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s - "
            f"Request ID: {request_id}"
        )
        
        return response
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Unhandled exception: {str(e)} - "
            f"{request.method} {request.url.path} - "
            f"Duration: {duration:.3f}s - "
            f"Request ID: {request_id}"
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Include routers
app.include_router(keys.router)
app.include_router(events.router)
app.include_router(analytics.router)
app.include_router(audit.router)
app.include_router(health.router)
app.include_router(websocket.router)


# Custom OpenAPI schema with Bearer token security
def custom_openapi():
    """Custom OpenAPI schema with Bearer token support"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description="Event-Driven Analytics & Audit API with async ingestion, rate limiting, and real-time metrics",
        routes=app.routes,
    )
    
    # Ensure components dict exists and merge security schemes with existing schemas
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    # Add Bearer token security scheme while preserving schemas
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}
    
    openapi_schema["components"]["securitySchemes"]["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "API Key as Bearer token. Create one at POST /api/v1/keys/ (first key doesn't require auth)"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/health",
        "timestamp": datetime.utcnow().isoformat()
    }


# 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
