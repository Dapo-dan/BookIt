from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import auth, users, services, bookings, reviews

# Setup logging
setup_logging()

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

@app.get("/")
async def root():
    return {"message": "BookIt API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
