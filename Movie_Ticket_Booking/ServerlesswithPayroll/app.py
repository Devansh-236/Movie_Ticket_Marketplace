from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import logging

from handlers.movies import router as movies_router
from handlers.tickets import router as tickets_router
from handlers.events import router as events_router
from handlers.transactions import router as transactions_router
from handlers.users import router as users_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Movie Booking API with Transaction Tracking",
    description="Serverless movie ticket booking CRUD API with event-driven architecture and user transaction tracking",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(movies_router, prefix="/api", tags=["movies"])
app.include_router(tickets_router, prefix="/api", tags=["tickets"])
app.include_router(events_router, prefix="/api", tags=["events"])
app.include_router(transactions_router, prefix="/api", tags=["transactions"])
app.include_router(users_router, prefix="/api", tags=["users"])

@app.get("/")
async def root():
    return {
        "message": "Movie Booking API with Transaction Tracking is running", 
        "version": "2.0.0",
        "features": [
            "Movie ticket booking",
            "User transaction tracking",
            "Payroll management",
            "Event-driven architecture"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "movie-booking-api-v2"}

# Mangum handler for AWS Lambda
handler = Mangum(app, lifespan="off")
