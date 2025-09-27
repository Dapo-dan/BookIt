from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import auth, users, services, bookings, reviews
import logging
import asyncio
from sqlalchemy import text

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BookIt API",
    description="A modern booking service application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(services.router)
app.include_router(bookings.router)
app.include_router(reviews.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        from app.db.session import engine
        # Test database connection and ensure tables exist
        async with engine.begin() as conn:
            # Check if users table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.warning("Database tables not found. Please run migrations: alembic upgrade head")
            else:
                logger.info("Database connection successful and tables exist")
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise the exception to allow the app to start
        # The health check will show the database status

@app.get("/")
async def root():
    return {"message": "BookIt API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        from app.db.session import engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            
            # Check if tables exist
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            tables_exist = result.scalar()
            
            if tables_exist:
                return {"status": "healthy", "database": "connected", "tables": "exist"}
            else:
                return {"status": "unhealthy", "database": "connected", "tables": "missing", "message": "Run migrations: alembic upgrade head"}
                
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
