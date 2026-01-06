"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.config import settings
from src.database import init_db, engine
from sqlalchemy import text
from src.routes.auth import router as auth_router
from src.routes.tasks import router as tasks_router
from src.routes.tags import router as tags_router
from src.routes.better_auth import router as better_auth_router, router_v1 as better_auth_v1_router
from src.middleware import rate_limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize database tables
    print(f"Starting TaskFlow API in {settings.environment} mode")
    print(f"Database URL: {settings.database_url[:50]}...")
    print(f"CORS Origins: {settings.cors_origins}")

    try:
        await init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Warning: Database initialization failed: {e}")
        print("Server will start but database operations may fail")
        import traceback
        traceback.print_exc()

    print("✓ Server startup complete")
    yield
    # Shutdown: Cleanup if needed
    print("Shutting down server...")


# Create FastAPI application
app = FastAPI(
    title="TaskFlow API",
    description="REST API for TaskFlow full-stack todo application",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",")]
if "http://localhost:3000" not in cors_origins:
    cors_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# T179: Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all API endpoints except health check."""
    # Skip rate limiting for health check and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    is_limited, remaining, reset_time = rate_limiter.is_rate_limited(request)

    if is_limited:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Please wait {reset_time} seconds.",
                "retry_after": reset_time,
            },
            headers={"Retry-After": str(reset_time)},
        )

    response = await call_next(request)
    # Add rate limit headers
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with database verification."""
    db_status = "disconnected"
    try:
        # Verify database connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        print(f"Database health check failed: {e}")

    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.environment
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "TaskFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(tags_router)
app.include_router(better_auth_router)  # Better Auth compatible endpoints at /api/auth
app.include_router(better_auth_v1_router)  # Better Auth compatible endpoints at /api/v1
